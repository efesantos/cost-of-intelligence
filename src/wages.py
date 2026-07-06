"""Wage / PPP / development-control layer with a source hierarchy (Task B-3).

Pulls, per country, live from the World Bank API (public, no key), caching each
raw response to data/raw/worldbank/ with a retrieval timestamp (G2). World Bank
is flaky/rate-limited from some networks, so every call retries with backoff and
a re-run reuses cached raw files for free.

Wage source hierarchy (recorded per country as `wage_tier`):
  Tier 1  ILOSTAT mean monthly earnings -> hourly  (best; attempted opportunistically)
  Tier 2  World Bank GNI per capita / 2080 h        [INFERENCE: crude full-employment
          -hours proxy -- an explicit caveat and a sensitivity axis]
  Tier 3  statutory minimum wage (lower-bound framing; cite African Language Tax §10.1)

This module ships Tier 2 as the always-available baseline, in BOTH market-US$
(NY.GNP.PCAP.CD) and PPP-int$ (NY.GNP.PCAP.PP.CD) terms, so instruments can be
reported in market-FX and PPP without a separate fragile FX join. GDP per capita
PPP and internet penetration are pulled here as B-7 regression controls.
"""
from __future__ import annotations

import datetime
import json
import pathlib
import time

import pandas as pd
import requests
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "worldbank"
CONFIG = ROOT / "config" / "country_language.yaml"
OUT_WAGES = ROOT / "data" / "wages.parquet"
OUT_CONTROLS = ROOT / "data" / "controls.parquet"

HOURS_PER_YEAR = 2080  # [INFERENCE] full-time-equivalent hours; a Tier-2 assumption.

INDICATORS = {
    "gni_pc_usd": "NY.GNP.PCAP.CD",        # GNI per capita, current US$ (market)
    "gni_pc_ppp": "NY.GNP.PCAP.PP.CD",     # GNI per capita, PPP current int$
    "gdp_pc_ppp": "NY.GDP.PCAP.PP.CD",     # GDP per capita, PPP (control)
    "internet_pct": "IT.NET.USER.ZS",      # internet users % pop (control)
}


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _wb_fetch(iso: str, indicator: str, max_retries: int = 8) -> list:
    """Fetch most-recent-5 values for one country/indicator, cached to disk."""
    RAW.mkdir(parents=True, exist_ok=True)
    cache = RAW / f"{iso}_{indicator}.json"
    if cache.exists():
        return json.loads(cache.read_text())["rows"]
    url = f"https://api.worldbank.org/v2/country/{iso}/indicator/{indicator}?format=json&mrv=5"
    last = None
    for attempt in range(max_retries):
        try:
            r = requests.get(url, timeout=45)
            r.raise_for_status()
            data = r.json()
            rows = data[1] if len(data) > 1 and data[1] else []
            cache.write_text(json.dumps({"retrieved_at": _now(), "url": url, "rows": rows}))
            return rows
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(min(2 ** attempt, 20))
    print(f"    WARN {iso}/{indicator} failed after retries: {last}")
    return []


def _latest(rows: list):
    for row in rows:  # WB returns newest-first
        if row.get("value") is not None:
            return row["value"], row["date"]
    return None, None


def all_countries(cfg: dict) -> list:
    isos = set()
    for m in cfg["languages"].values():
        isos.add(m["primary"])
        isos.update(m.get("alternates", []))
    isos.update(cfg["lusophone_territories"].values())
    return sorted(isos)


def build() -> pd.DataFrame:
    cfg = yaml.safe_load(CONFIG.read_text())
    names = cfg["country_names"]
    countries = all_countries(cfg)
    wage_rows, control_rows = [], []
    for iso in countries:
        vals = {}
        for key, ind in INDICATORS.items():
            v, yr = _latest(_wb_fetch(iso, ind))
            vals[key] = v
            vals[f"{key}_year"] = yr
        gni_usd = vals["gni_pc_usd"]
        gni_ppp = vals["gni_pc_ppp"]
        wage_rows.append({
            "country": iso, "country_name": names.get(iso, iso),
            "wage_tier": 2,
            "hourly_wage_usd_market": (gni_usd / HOURS_PER_YEAR) if gni_usd else None,
            "hourly_wage_usd_ppp": (gni_ppp / HOURS_PER_YEAR) if gni_ppp else None,
            "gni_pc_usd": gni_usd, "gni_pc_ppp": gni_ppp,
            "gni_year": vals["gni_pc_usd_year"] or vals["gni_pc_ppp_year"],
            "source": "World Bank NY.GNP.PCAP.(CD|PP.CD)",
            "hours_per_year_assumption": HOURS_PER_YEAR,
        })
        control_rows.append({
            "country": iso, "country_name": names.get(iso, iso),
            "gdp_pc_ppp": vals["gdp_pc_ppp"], "gdp_year": vals["gdp_pc_ppp_year"],
            "internet_pct": vals["internet_pct"], "internet_year": vals["internet_pct_year"],
        })
        wr = wage_rows[-1]
        print(f"  {iso} {names.get(iso, iso)[:18]:18s} "
              f"mkt=${(wr['hourly_wage_usd_market'] or 0):.2f}/h  "
              f"ppp=${(wr['hourly_wage_usd_ppp'] or 0):.2f}/h  ({wr['gni_year']})")

    wdf = pd.DataFrame(wage_rows)
    cdf = pd.DataFrame(control_rows)
    OUT_WAGES.parent.mkdir(parents=True, exist_ok=True)
    wdf.to_parquet(OUT_WAGES, index=False)
    cdf.to_parquet(OUT_CONTROLS, index=False)
    return wdf


if __name__ == "__main__":
    print("Pulling World Bank wages + controls (cached, retried)...")
    df = build()
    missing = df[df.hourly_wage_usd_ppp.isna()]["country"].tolist()
    print(f"wrote {OUT_WAGES.name} ({len(df)} countries); missing wage: {missing or 'none'}")
