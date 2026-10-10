"""The four instruments (Stream B, Task B-5).

For every (language, country, tokenizer family, model tier) computes:

  e_real       = (1e6 / p_blend) / fertility        EN-equivalent tokens per USD
  IW           = e_real * hourly_wage_usd           EN-equivalent tokens per hour of local work
  work_minutes = (bundle_Etok * fertility * p_blend / 1e6) / hourly_wage_usd * 60
  surcharge    = fertility - 1                       the Language Tax

p_blend = (1*input + r*output)/(1+r), default r=3 [INFERENCE, swept in B-9].
Bundle = 1M English-equivalent tokens/month by default [INFERENCE — arbitrary but
transparent; work_minutes is LINEAR in bundle size so rankings are invariant].

Every row carries its tokenizer family, model id, and the retrieval dates of the
price and wage inputs. Nothing is ever pooled across families (no "the" token).

Instruments are reported in BOTH market-FX and PPP terms via the two wage columns
from Task B-3 (GNI in current US$ vs PPP int$).
"""
from __future__ import annotations

import pathlib

import pandas as pd
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
FERT = ROOT / "data" / "fertility.parquet"
WAGES = ROOT / "data" / "wages.parquet"
PRICES = ROOT / "config" / "prices.yaml"
MAPPING = ROOT / "config" / "country_language.yaml"
OUT = ROOT / "data" / "instruments.parquet"

DEFAULT_R = 3.0
DEFAULT_BUNDLE_ETOK = 1_000_000.0


def p_blend(inp: float, out: float, r: float = DEFAULT_R) -> float:
    """Blended $/Mtok = (1*input + r*output)/(1+r)."""
    return (inp + r * out) / (1.0 + r)


def compute(r: float = DEFAULT_R, bundle_etok: float = DEFAULT_BUNDLE_ETOK,
            price_tier: str = "flagship", write: bool = False,
            include_alternates: bool = False) -> pd.DataFrame:
    """One row per (language, country, family). By default each language is paired
    with its PRIMARY country only (the canonical instruments.parquet). With
    include_alternates=True, each language is also paired with the alternate
    countries in config/country_language.yaml (e.g. Portuguese in BRA/AGO/MOZ), for
    the sensitivity and alternate-mapping checks; the `mapping` column says which."""
    fert = pd.read_parquet(FERT)
    wages = pd.read_parquet(WAGES).set_index("country")
    # ILOSTAT Tier-1 hourly wage (actual employee earnings), reported alongside the
    # World Bank Tier-2 (GNI/2080) basis so every instrument carries BOTH.
    ilo_path = ROOT / "data" / "ilostat_wages.parquet"
    ilo = (pd.read_parquet(ilo_path).set_index("country")["hourly_wage_usd_ilo"].to_dict()
           if ilo_path.exists() else {})
    prices = yaml.safe_load(PRICES.read_text())["anchors"]
    mapping = yaml.safe_load(MAPPING.read_text())
    targets = {lang: [(m["primary"], "primary")] +
               ([(c, "alternate") for c in m.get("alternates", [])] if include_alternates else [])
               for lang, m in mapping["languages"].items()}

    rows = []
    for _, fr in fert.iterrows():
        lang, family = fr["language"], fr["family"]
        anchor = prices.get(family, {}).get(price_tier)
        if not anchor or not anchor.get("model"):
            continue
        pb = p_blend(anchor["input_usd_per_mtok"], anchor["output_usd_per_mtok"], r)
        fertility = fr["fertility"]
        e_real = (1e6 / pb) / fertility
        for country, role in targets.get(lang, []):
            if country not in wages.index:
                continue
            w = wages.loc[country]
            rec = {
                "language": lang, "language_name": fr["language_name"],
                "country": country, "country_name": w["country_name"],
                "family": family, "model_tier": price_tier, "model_id": anchor["model"],
                "fertility": fertility, "surcharge": fertility - 1.0,
                "p_blend_usd_per_mtok": pb, "r": r, "bundle_etok": bundle_etok,
                "price_input": anchor["input_usd_per_mtok"], "price_output": anchor["output_usd_per_mtok"],
                "e_real_tokens_per_usd": e_real,
                "price_retrieved_at": anchor["retrieved_at"],
                "gni_year": w["gni_year"],
            }
            wage_bases = {"market": w["hourly_wage_usd_market"],   # WB Tier-2 GNI/2080, market US$
                          "ppp": w["hourly_wage_usd_ppp"],          # WB Tier-2, PPP int$
                          "ilo": ilo.get(country)}                  # ILOSTAT Tier-1, actual earnings US$
            for kind, wage in wage_bases.items():
                if wage and wage > 0:
                    rec[f"iw_{kind}_tokens_per_hour"] = e_real * wage
                    rec[f"work_minutes_{kind}"] = (bundle_etok * fertility * pb / 1e6) / wage * 60
                else:
                    rec[f"iw_{kind}_tokens_per_hour"] = None
                    rec[f"work_minutes_{kind}"] = None
            rec["hourly_wage_ilo"] = ilo.get(country)
            if include_alternates:
                rec["mapping"] = role
            rows.append(rec)

    df = pd.DataFrame(rows)
    if write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(OUT, index=False)
    return df


def _identity_checks(df: pd.DataFrame) -> list:
    """B-5 acceptance identity checks."""
    out = []
    en = df[df.language == "eng_Latn"]
    if (en["surcharge"].abs() < 1e-9).all():
        out.append("OK: English surcharge == 0 for every family.")
    else:
        out.append("FAIL: English surcharge != 0.")
    # linearity: doubling bundle doubles work_minutes exactly
    d2 = compute(bundle_etok=DEFAULT_BUNDLE_ETOK * 2)
    merged = df.merge(d2, on=["language", "family"], suffixes=("", "_2x"))
    ratio = merged["work_minutes_market_2x"] / merged["work_minutes_market"]
    if ((ratio - 2.0).abs().dropna() < 1e-9).all():
        out.append("OK: work_minutes is exactly linear in bundle size.")
    else:
        out.append("FAIL: work_minutes not linear in bundle.")
    return out


if __name__ == "__main__":
    df = compute(write=True)
    print(f"wrote {OUT.name} ({len(df)} rows)")
    for line in _identity_checks(df):
        print("  " + line)
    # headline preview: work_minutes for the o200k family, PPP terms
    sub = df[(df.family == "openai_o200k")].sort_values("work_minutes_ppp")
    print("\n  Minutes of local work to buy 1M English-equivalent tokens (o200k, PPP):")
    for _, r in sub.iterrows():
        wm = r["work_minutes_ppp"]
        print(f"    {r['country_name'][:16]:16s} {r['language_name'][:12]:12s} "
              f"fert={r['fertility']:.2f}  {wm:.1f} min" if wm else
              f"    {r['country_name'][:16]:16s} (no wage)")
