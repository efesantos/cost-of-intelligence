"""Export a compact JSON for the interactive page (Task B-10). No backend.

Writes docs/data.json with fertility, prices, wages, and the AEI outcome so the
static page can recompute all four instruments client-side as the user moves the
(language, country, family, bundle) selectors -- demonstrating the bundle-linearity
claim live.
"""
from __future__ import annotations

import datetime
import json
import pathlib

import pandas as pd
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "data.json"


def main():
    fert = pd.read_parquet(ROOT / "data" / "fertility.parquet")
    wages = pd.read_parquet(ROOT / "data" / "wages.parquet")
    prices = yaml.safe_load((ROOT / "config" / "prices.yaml").read_text())
    mapping = yaml.safe_load((ROOT / "config" / "country_language.yaml").read_text())
    aei = pd.read_parquet(ROOT / "data" / "aei.parquet")

    fert_map = {}
    for _, r in fert.iterrows():
        fert_map.setdefault(r["language"], {"name": r["language_name"], "families": {}})
        fert_map[r["language"]]["families"][r["family"]] = {
            "fertility": round(r["fertility"], 4),
            "ci": [round(r["ci_low"], 4), round(r["ci_high"], 4)]}

    price_map = {}
    for fam, tiers in prices["anchors"].items():
        price_map[fam] = {}
        for tier, d in tiers.items():
            if d.get("model"):
                price_map[fam][tier] = {"model": d["model"],
                                        "input": d["input_usd_per_mtok"],
                                        "output": d["output_usd_per_mtok"]}

    wage_map = {}
    for _, r in wages.iterrows():
        wage_map[r["country"]] = {"name": r["country_name"],
                                  "market": r["hourly_wage_usd_market"],
                                  "ppp": r["hourly_wage_usd_ppp"],
                                  "year": r["gni_year"]}

    aei_map = {r["country"]: round(r["usage_per_capita_index"], 4)
               for _, r in aei.iterrows() if pd.notna(r["usage_per_capita_index"])}

    lang_country = {lang: m["primary"] for lang, m in mapping["languages"].items()}

    out = {
        "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
        "price_source": prices["_meta"]["retrieved_at"],
        "fertility": fert_map, "prices": price_map, "wages": wage_map,
        "aei": aei_map, "lang_country": lang_country,
        "families": sorted(price_map.keys()),
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1, default=lambda x: None if pd.isna(x) else float(x)))
    print(f"wrote {OUT.relative_to(ROOT)} "
          f"({len(fert_map)} langs, {len(wage_map)} countries, {len(price_map)} families)")


if __name__ == "__main__":
    main()
