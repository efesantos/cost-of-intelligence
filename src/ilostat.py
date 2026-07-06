"""ILOSTAT Tier-1 wages: mean nominal monthly earnings of employees -> hourly USD
(Stream B, Task B-3 upgrade).

The repo's baseline wage layer (src/wages.py) is Tier-2: World Bank GNI per capita
/ 2080 h, a crude full-employment-hours proxy. This module produces a better
**Tier-1** wage -- ILOSTAT *average monthly earnings of employees* converted to an
hourly USD rate -- into a SEPARATE artifact (data/ilostat_wages.parquet), leaving
data/wages.parquet untouched.

Source: ILOSTAT SDMX 2.1 REST API (https://sdmx.ilo.org/rest), dataflow
``DF_EAR_EMTA_SEX_CUR_NB`` -- "Average monthly earnings of employees by sex and
currency". ILOSTAT publishes each observation in three currency views
(CUR_TYPE_LCU local currency, CUR_TYPE_USD US$, CUR_TYPE_PPP int$). We prefer the
ILOSTAT-published **USD** value directly (its own market-FX conversion), so no
separate FX join is needed for the vast majority of countries; where only LCU is
published we fall back to the World Bank official exchange rate PA.NUS.FCRF (LCU
per US$, retried with backoff, cached). `fx_lcu_per_usd` is recorded either way --
for USD-published rows it is the exchange rate ILOSTAT implicitly used
(LCU value / USD value), a transparent audit trail.

Hourly = monthly / (WEEKS_PER_MONTH x HOURS_PER_WEEK). WEEKS_PER_MONTH = 52/12.
HOURS_PER_WEEK = 40 is an [INFERENCE] default (ILOSTAT's mean-actual-hours series
is not joined here); this is flagged in the report and is a natural sensitivity axis.
"""
from __future__ import annotations

import datetime
import json
import pathlib
import re
import time
from typing import List, Optional

import pandas as pd
import requests
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "ilostat"
CONFIG = ROOT / "config" / "country_language.yaml"
OUT_PARQUET = ROOT / "data" / "ilostat_wages.parquet"
OUT_REPORT = ROOT / "reports" / "ilostat_wages.md"

DATAFLOW = "DF_EAR_EMTA_SEX_CUR_NB"
SDMX_URL = (
    "https://sdmx.ilo.org/rest/data/{flow}/all"
    "?startPeriod=2010&format=csv&dimensionAtObservation=AllDimensions"
)
WB_FX_URL = "https://api.worldbank.org/v2/country/{iso}/indicator/PA.NUS.FCRF?format=json&mrv=10"

WEEKS_PER_MONTH = 52 / 12          # 4.333...; standard month-to-week conversion
HOURS_PER_WEEK = 40                # [INFERENCE] full-time default; see module docstring
SEX_TOTAL = "SEX_T"
CUR_USD, CUR_LCU = "CUR_TYPE_USD", "CUR_TYPE_LCU"


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def target_countries(cfg: dict) -> List[str]:
    """Union of language primary ISO3s and the country_names display keys."""
    iso = set(cfg["country_names"].keys())
    for m in cfg["languages"].values():
        iso.add(m["primary"])
        iso.update(m.get("alternates", []))
    return sorted(iso)


def _fetch_ilostat(max_retries: int = 6) -> Optional[pd.DataFrame]:
    """Download the full earnings dataflow as CSV, cached to disk with timestamp."""
    RAW.mkdir(parents=True, exist_ok=True)
    cache = RAW / f"{DATAFLOW}.csv"
    if cache.exists():
        return pd.read_csv(cache, dtype=str)
    url = SDMX_URL.format(flow=DATAFLOW)
    last = None
    for attempt in range(max_retries):
        try:
            r = requests.get(
                url, timeout=45,
                headers={"Accept": "application/vnd.sdmx.data+csv;version=1.0.0"},
            )
            r.raise_for_status()
            cache.write_bytes(r.content)
            (RAW / f"{DATAFLOW}.meta.json").write_text(
                json.dumps({"retrieved_at": _now(), "url": url, "bytes": len(r.content)})
            )
            return pd.read_csv(cache, dtype=str)
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(min(2 ** attempt, 20))
    print(f"    WARN ILOSTAT fetch failed after retries: {last}")
    return None


def _wb_fx(iso: str, year: int, max_retries: int = 6) -> Optional[float]:
    """World Bank official exchange rate (LCU per US$) for `year`, cached.

    Fallback FX only, used when ILOSTAT publishes LCU but not USD for a country.
    """
    RAW.mkdir(parents=True, exist_ok=True)
    cache = RAW / f"fx_{iso}.json"
    if cache.exists():
        rows = json.loads(cache.read_text())["rows"]
    else:
        url = WB_FX_URL.format(iso=iso)
        rows, last = None, None
        for attempt in range(max_retries):
            try:
                r = requests.get(url, timeout=45)
                r.raise_for_status()
                data = r.json()
                rows = data[1] if len(data) > 1 and data[1] else []
                cache.write_text(json.dumps({"retrieved_at": _now(), "url": url, "rows": rows}))
                break
            except Exception as e:  # noqa: BLE001
                last = e
                time.sleep(min(2 ** attempt, 20))
        if rows is None:
            print(f"    WARN WB FX {iso} failed after retries: {last}")
            return None
    by_year = {row["date"]: row["value"] for row in rows if row.get("value") is not None}
    if str(year) in by_year:
        return float(by_year[str(year)])
    # else nearest available year
    if by_year:
        nearest = min(by_year, key=lambda d: abs(int(d) - year))
        return float(by_year[nearest])
    return None


def _currency_code(note_classif: Optional[str]) -> Optional[str]:
    """Extract the ISO-4217-ish local currency code from ILOSTAT's NOTE_CLASSIF,
    e.g. 'KES: Kenyan shilling' -> 'KES'."""
    if not note_classif or not isinstance(note_classif, str):
        return None
    m = re.search(r"\b([A-Z]{3})\s*:", note_classif)
    return m.group(1) if m else None


def _pick_country(df_c: pd.DataFrame) -> Optional[dict]:
    """Given all SEX_T earnings rows for one country, pick the most recent year and
    assemble USD / LCU / currency / implied-FX for it."""
    if df_c.empty:
        return None
    df_c = df_c.copy()
    df_c["year"] = df_c["TIME_PERIOD"].astype(int)
    df_c["val"] = df_c["OBS_VALUE"].astype(float)
    # Prefer the most recent year that has a USD figure; else most recent with LCU.
    usd = df_c[df_c["CUR"] == CUR_USD]
    lcu = df_c[df_c["CUR"] == CUR_LCU]
    if not usd.empty:
        year = int(usd["year"].max())
    elif not lcu.empty:
        year = int(lcu["year"].max())
    else:
        return None
    yr_usd = usd[usd["year"] == year]
    yr_lcu = lcu[lcu["year"] == year]
    usd_val = float(yr_usd["val"].iloc[0]) if not yr_usd.empty else None
    lcu_val = float(yr_lcu["val"].iloc[0]) if not yr_lcu.empty else None
    note = None
    for frame in (yr_lcu, yr_usd):
        if not frame.empty and isinstance(frame["NOTE_CLASSIF"].iloc[0], str):
            note = frame["NOTE_CLASSIF"].iloc[0]
            break
    src = None
    for frame in (yr_usd, yr_lcu):
        if not frame.empty:
            src = frame["SOURCE"].iloc[0]
            break
    return {
        "year": year, "usd": usd_val, "lcu": lcu_val,
        "currency": _currency_code(note), "ilo_source": src,
    }


def build() -> pd.DataFrame:
    cfg = yaml.safe_load(CONFIG.read_text())
    names = cfg["country_names"]
    countries = target_countries(cfg)

    print(f"Fetching ILOSTAT {DATAFLOW} (cached)...")
    raw = _fetch_ilostat()
    if raw is None:
        _write_blocker_report(countries, names)
        raise SystemExit(
            "ILOSTAT SDMX unreachable -- wrote blocker to reports/ilostat_wages.md. "
            "Code would compute Tier-1 wages once data/raw/ilostat/"
            f"{DATAFLOW}.csv is present."
        )

    tot = raw[raw["SEX"] == SEX_TOTAL]
    retrieved = _now()
    rows, missing = [], []
    for iso in countries:
        picked = _pick_country(tot[tot["REF_AREA"] == iso])
        if picked is None:
            missing.append(iso)
            continue

        year = picked["year"]
        usd_month = picked["usd"]
        lcu_month = picked["lcu"]
        currency = picked["currency"]

        # Implied FX from ILOSTAT's own conversion (LCU/USD); else World Bank fallback.
        fx = None
        source = None
        if usd_month is not None and lcu_month is not None and usd_month > 0:
            fx = lcu_month / usd_month
            source = f"ILOSTAT {DATAFLOW} CUR_TYPE_USD (published US$)"
        elif usd_month is not None:
            source = f"ILOSTAT {DATAFLOW} CUR_TYPE_USD (published US$)"
        elif lcu_month is not None:
            fx = _wb_fx(iso, year)
            if fx:
                usd_month = lcu_month / fx
                source = (f"ILOSTAT {DATAFLOW} CUR_TYPE_LCU -> USD via "
                          f"World Bank PA.NUS.FCRF ({year})")
            else:
                missing.append(iso)
                continue

        hourly = usd_month / (WEEKS_PER_MONTH * HOURS_PER_WEEK) if usd_month else None
        rows.append({
            "country": iso,
            "country_name": names.get(iso, iso),
            "hourly_wage_usd_ilo": hourly,
            "monthly_earnings_usd": usd_month,
            "monthly_earnings_local": lcu_month,
            "currency": currency,
            "fx_lcu_per_usd": fx,
            "year": year,
            "wage_tier": 1,
            "hours_per_week_assumption": HOURS_PER_WEEK,
            "weeks_per_month": round(WEEKS_PER_MONTH, 4),
            "source": source,
            "ilo_source": picked["ilo_source"],
            "retrieved_at": retrieved,
        })
        print(f"  {iso} {names.get(iso, iso)[:16]:16s} "
              f"${(hourly or 0):6.2f}/h  (month ${(usd_month or 0):,.0f} {currency or ''}, {year})")

    df = pd.DataFrame(rows).sort_values("country").reset_index(drop=True)
    OUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT_PARQUET, index=False)
    _write_report(df, missing, names, countries)
    print(f"wrote {OUT_PARQUET} ({len(df)}/{len(countries)} countries); "
          f"missing Tier-1: {missing or 'none'}")
    return df


def _write_report(df, missing, names, countries) -> None:
    lines = [
        "# ILOSTAT Tier-1 wages (mean monthly earnings -> hourly USD)",
        "",
        f"Generated: {_now()}",
        "",
        "Tier-1 wage layer: ILOSTAT *average monthly earnings of employees* "
        "(SEX total, all economic activities), converted to an hourly USD rate. "
        "This is a better alternative to the repo's Tier-2 World Bank GNI/2080 proxy "
        "and is written to a SEPARATE artifact (data/ilostat_wages.parquet); "
        "data/wages.parquet is untouched.",
        "",
        f"- Dataflow: `{DATAFLOW}` (Average monthly earnings of employees by sex and currency).",
        "- Currency: ILOSTAT-published **US$** (CUR_TYPE_USD) preferred; World Bank "
        "PA.NUS.FCRF fallback where only local currency is published.",
        f"- Hourly = monthly / ({WEEKS_PER_MONTH:.3f} weeks/month x {HOURS_PER_WEEK} h/week). "
        "**[INFERENCE]** 40 h/week is a full-time default (ILOSTAT mean-actual-hours not joined).",
        f"- Most recent available year taken per country (range "
        f"{int(df['year'].min())}-{int(df['year'].max())}).",
        "",
        f"Coverage: **{len(df)} / {len(countries)}** target countries have Tier-1 data.",
        "",
        "## Tier-1 hourly wages",
        "",
        "| country | hourly USD | monthly USD | local/mo | currency | FX (LCU/US$) | year |",
        "|---|---|---|---|---|---|---|",
    ]
    for _, r in df.sort_values("hourly_wage_usd_ilo", ascending=False).iterrows():
        loc = f"{r.monthly_earnings_local:,.0f}" if pd.notna(r.monthly_earnings_local) else "—"
        fx = f"{r.fx_lcu_per_usd:,.3f}" if pd.notna(r.fx_lcu_per_usd) else "—"
        mu = f"{r.monthly_earnings_usd:,.0f}" if pd.notna(r.monthly_earnings_usd) else "—"
        lines.append(
            f"| {r.country_name} | ${r.hourly_wage_usd_ilo:.2f} | {mu} | {loc} "
            f"| {r.currency or '—'} | {fx} | {int(r.year)} |"
        )

    lines += ["", "## Coverage", "",
              f"- Tier-1 obtained: {len(df)} countries.",
              f"- Missing (no ILOSTAT earnings series): "
              f"{', '.join(names.get(c, c) for c in missing) if missing else 'none'}."]
    # How many relied on the WB FX fallback vs ILOSTAT USD.
    fx_fallback = df[df["source"].str.contains("World Bank", na=False)]
    if len(fx_fallback):
        lines.append(f"- Used World Bank FX fallback (LCU-only in ILOSTAT): "
                     f"{', '.join(fx_fallback['country_name'])}.")
    else:
        lines.append("- All covered countries had an ILOSTAT-published USD value "
                     "(no World Bank FX fallback needed).")

    lines += ["", "## Notes / assumptions", "",
              "- [INFERENCE] 40 h/week full-time default drives the hourly conversion; "
              "swap for ILOSTAT mean weekly hours actually worked to refine.",
              "- `fx_lcu_per_usd` for USD-published rows is ILOSTAT's implied rate "
              "(local monthly / USD monthly), shown for audit; it is not an independent source.",
              "- Most recent year differs by country; earnings are nominal (not deflated).",
              "- Economic-activity aggregate (all activities) and SEX total are used; "
              "no industry or sex breakdown is applied."]
    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.write_text("\n".join(lines) + "\n")


def _write_blocker_report(countries, names) -> None:
    lines = [
        "# ILOSTAT Tier-1 wages -- BLOCKED",
        "",
        f"Generated: {_now()}",
        "",
        "The ILOSTAT SDMX endpoint was unreachable after retries with backoff.",
        "",
        f"- Endpoint: `{SDMX_URL.format(flow=DATAFLOW)}`",
        f"- Target countries ({len(countries)}): "
        f"{', '.join(names.get(c, c) for c in countries)}.",
        "",
        "This module WOULD produce data/ilostat_wages.parquet given the cached CSV "
        f"at data/raw/ilostat/{DATAFLOW}.csv (SDMX data+csv: columns REF_AREA, SEX, "
        "CUR, TIME_PERIOD, OBS_VALUE). Re-run `python src/ilostat.py` when reachable.",
    ]
    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    build()
