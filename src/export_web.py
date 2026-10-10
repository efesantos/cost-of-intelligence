"""Export a compact JSON for the interactive page (Task B-10). No backend.

Writes docs/data.json with fertility, prices, wages, and the AEI outcome so the
static page can recompute all four instruments client-side as the user moves the
(language, country, family, bundle) selectors -- demonstrating the bundle-linearity
claim live.
"""
from __future__ import annotations

import json
import pathlib

import pandas as pd
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "data.json"


def _fertility_date() -> str | None:
    report = ROOT / "reports" / "fertility_report.md"
    if report.exists():
        for line in report.read_text().splitlines():
            if line.startswith("Generated:"):
                return line.split()[1][:10]
    return None


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

    ilo_path = ROOT / "data" / "ilostat_wages.parquet"
    ilo = (pd.read_parquet(ilo_path).set_index("country")["hourly_wage_usd_ilo"].to_dict()
           if ilo_path.exists() else {})
    wage_map = {}
    for _, r in wages.iterrows():
        wage_map[r["country"]] = {"name": r["country_name"],
                                  "market": r["hourly_wage_usd_market"],
                                  "ppp": r["hourly_wage_usd_ppp"],
                                  "ilo": ilo.get(r["country"]),
                                  "year": r["gni_year"]}

    aei_map = {r["country"]: round(r["usage_per_capita_index"], 4)
               for _, r in aei.iterrows() if pd.notna(r["usage_per_capita_index"])}

    lang_country = {lang: m["primary"] for lang, m in mapping["languages"].items()}

    # source dates shown on the page; "generated" is the newest of them, so re-running
    # the export on unchanged data leaves the files unchanged
    ilo_df = pd.read_parquet(ilo_path) if ilo_path.exists() else None
    sources = {
        "prices": prices["_meta"]["retrieved_at"][:10],
        "fertility": _fertility_date(),
        "wb_gni_year": str(wages["gni_year"].max()),
        "ilostat_years": (f"{ilo_df['year'].min()}-{ilo_df['year'].max()}" if ilo_df is not None else None),
        "aei_release": "release_2025_09_15 (Claude.ai, 2025-08-04 to 2025-08-11)",
    }
    out = {
        "generated": max(sources["prices"], sources["fertility"] or ""),
        "price_source": prices["_meta"]["retrieved_at"],
        "sources": sources,
        "fertility": fert_map, "prices": price_map, "wages": wage_map,
        "aei": aei_map, "lang_country": lang_country,
        "families": sorted(price_map.keys()),
    }
    OUT.parent.mkdir(exist_ok=True)
    blob = json.dumps(out, indent=1, default=lambda x: None if pd.isna(x) else float(x))
    OUT.write_text(blob)  # for GitHub Pages (served over https)
    # Also emit a JS global so the page works when opened directly via file:// (fetch
    # of a local .json is blocked by CORS on file://; a <script src> is not).
    (OUT.parent / "data.js").write_text("window.__COI_DATA__ = " + blob + ";\n")
    print(f"wrote {OUT.relative_to(ROOT)} + data.js "
          f"({len(fert_map)} langs, {len(wage_map)} countries, {len(price_map)} families)")


if __name__ == "__main__":
    main()
