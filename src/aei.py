"""Anthropic Economic Index ingestion + outcome-variable selection (Task B-6).

Reads the AEI Sept-2025 release (`Anthropic/EconomicIndex`, ungated), extracts the
country-level adoption outcome, and writes data/aei.parquet + docs/aei_notes.md.

Outcome variable (selected per the plan's rule "prefer the release's own per-capita
normalized usage measure"): **`usage_per_capita_index`** at facet=country. Per the
release's own data_documentation.md, this is a concentration index = a geography's
usage share divided by its working-age-population share (1.0 = proportional,
>1.0 over-represented, <1.0 under-represented). It is already per-capita normalized,
so no separate population join is needed. We do NOT invent an outcome.

We also carry `usage_pct` (raw share) and `usage_tier` for robustness/description.
Enriched data keys countries by ISO-3 (`geo_id`), matching our country panel.
"""
from __future__ import annotations

import datetime
import pathlib

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "raw" / "aei" / "aei_enriched_claude_ai_2025-08-04_to_2025-08-11.csv"
OUT = ROOT / "data" / "aei.parquet"
MEMO = ROOT / "docs" / "aei_notes.md"
RELEASE = "release_2025_09_15"
WINDOW = "2025-08-04_to_2025-08-11"


def _ensure_source() -> None:
    """Download the enriched AEI CSV from HF if not present (kept out of git; 26 MB)."""
    if SRC.exists():
        return
    from huggingface_hub import hf_hub_download
    SRC.parent.mkdir(parents=True, exist_ok=True)
    rel = f"{RELEASE}/data/output/aei_enriched_claude_ai_{WINDOW}.csv"
    p = hf_hub_download("Anthropic/EconomicIndex", rel, repo_type="dataset")
    import shutil
    shutil.copy(p, SRC)


def build() -> pd.DataFrame:
    _ensure_source()
    df = pd.read_csv(SRC)
    country = df[df.facet == "country"]
    wide = {}
    for var in ("usage_per_capita_index", "usage_pct", "usage_tier"):
        sub = country[country.variable == var][["geo_id", "geo_name", "value"]]
        wide[var] = sub.set_index("geo_id")["value"]
    out = pd.DataFrame(wide)
    names = country.drop_duplicates("geo_id").set_index("geo_id")["geo_name"]
    out.insert(0, "country_name", names)
    out.index.name = "country"
    out = out.reset_index()
    out.to_parquet(OUT, index=False)
    return out


def write_memo(df: pd.DataFrame) -> None:
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    n = len(df)
    top = df.sort_values("usage_per_capita_index", ascending=False).head(5)
    lines = [
        "# AEI outcome-variable memo (Task B-6)",
        "",
        f"Generated: {now}",
        "",
        f"**Source:** `Anthropic/EconomicIndex`, release `{RELEASE}`, Claude.ai (Free and Pro),",
        f"usage window `{WINDOW}`. Ungated. File: `data/output/aei_enriched_claude_ai_{WINDOW}.csv`.",
        "",
        "## Chosen outcome variable",
        "",
        "**`usage_per_capita_index`** at `facet=country`. Per the release's own",
        "`data_documentation.md`: *\"Concentration index showing if a geography has more/less",
        "usage than expected based on population share (1.0 = proportional, >1.0 = over-",
        "representation, <1.0 = under-representation)\"* — computed as usage share divided by",
        "working-age-population share during the release's enrichment step. It is already",
        "per-capita normalized, so no separate population join is required. This satisfies the",
        "B-6 rule (prefer the release's own per-capita normalized usage measure).",
        "",
        "Also retained for robustness/description: `usage_pct` (raw share of global usage) and",
        "`usage_tier` (adoption quartile).",
        "",
        f"## Coverage: {n} countries with a country-level index.",
        "",
        "Top-5 adoption (per-capita index):",
        "",
        "| country | usage_per_capita_index |",
        "|---|---|",
    ]
    for _, r in top.iterrows():
        lines.append(f"| {r['country_name']} | {r['usage_per_capita_index']:.2f} |")
    # panel-relevant countries
    panel = ["USA", "PRT", "BRA", "MEX", "ZAF", "KEN", "NGA", "EGY", "IND", "MOZ", "AGO"]
    sub = df[df.country.isin(panel)].sort_values("usage_per_capita_index", ascending=False)
    lines += ["", "Panel countries (the affordability gradient the study links to adoption):", "",
              "| country | usage_per_capita_index |", "|---|---|"]
    for _, r in sub.iterrows():
        lines.append(f"| {r['country_name']} | {r['usage_per_capita_index']:.3f} |")
    lines += ["", "[INFERENCE] The gradient — e.g. Angola near the bottom — is consistent with the",
              "affordability thesis, but B-7 tests it *correlationally* with income controls; this",
              "memo asserts only what the AEI variable measures, not causation."]
    MEMO.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    df = build()
    write_memo(df)
    print(f"wrote {OUT.name} ({len(df)} countries) and {MEMO.relative_to(ROOT)}")
    print("  outcome = usage_per_capita_index (country facet)")
