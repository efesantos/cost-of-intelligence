"""Sensitivity battery (Task B-9).

Sweeps the modelling choices and reports the range each headline number takes, so
"which choices move the numbers" is explicit. Axes implemented here:
  (1) input:output ratio r in {1, 3, 9}
  (2) market FX vs PPP wages
  (3) per-tokenizer-family spread (the "tokenizer lottery")
  (4) input-only vs output-only pricing (r -> 0 and r -> large)

Not yet implemented (flagged): FLORES+ vs UDHR fertility (needs the UDHR corpus,
Task future); wage-tier swaps (only World Bank Tier-2 is populated so far).
"""
from __future__ import annotations

import pathlib

import pandas as pd

import instruments as I

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "sensitivity.md"

# Focus countries for the headline "work_minutes" number.
FOCUS = ["USA", "PRT", "BRA", "AGO", "MOZ", "KEN", "NGA", "ETH"]


def _work_minutes_table(r, kind, family="openai_o200k"):
    df = I.compute(r=r, price_tier="flagship")
    df = df[df.family == family]
    # a country can host >1 language (e.g. Nigeria: Hausa + Yoruba); average them
    return df.groupby("country")[f"work_minutes_{kind}"].mean()


def main():
    rows = []
    # (1) r sweep + (2) market/ppp, o200k family
    for r in (1, 3, 9):
        for kind in ("market", "ppp"):
            wm = _work_minutes_table(r, kind)
            for c in FOCUS:
                if c in wm.index and pd.notna(wm[c]):
                    rows.append({"axis": "r_and_wagebasis", "r": r, "wage": kind,
                                 "country": c, "work_minutes": wm[c]})
    swept = pd.DataFrame(rows)

    # (3) per-family spread at r=3, ppp
    base = I.compute(r=3)
    fam_rows = []
    for c in FOCUS:
        sub = base[(base.country == c)].dropna(subset=["work_minutes_ppp"])
        if len(sub):
            fam_rows.append({"country": c,
                             "min": sub["work_minutes_ppp"].min(),
                             "max": sub["work_minutes_ppp"].max(),
                             "min_family": sub.loc[sub["work_minutes_ppp"].idxmin(), "family"],
                             "max_family": sub.loc[sub["work_minutes_ppp"].idxmax(), "family"]})
    fam = pd.DataFrame(fam_rows)

    # (4) input-only (r=0) vs output-only (r=1e6)
    io_rows = []
    for label, r in (("input_only", 0.0), ("output_only", 1e6)):
        wm = _work_minutes_table(r, "ppp")
        for c in FOCUS:
            if c in wm.index and pd.notna(wm[c]):
                io_rows.append({"pricing": label, "country": c, "work_minutes": wm[c]})
    io = pd.DataFrame(io_rows)

    lines = ["# Sensitivity battery (Task B-9)", "",
             "Every headline `work_minutes` number with its range across modelling choices.",
             "Bundle = 1M English-equivalent tokens/month. Family = o200k unless noted.", ""]

    lines += ["## (1)+(2) r ratio x wage basis (o200k)", "",
              "| country | " + " | ".join(f"r={r},{k}" for r in (1, 3, 9) for k in ("mkt", "ppp")) + " |",
              "|" + "---|" * 7]
    for c in FOCUS:
        cells = []
        for r in (1, 3, 9):
            for k in ("market", "ppp"):
                v = swept[(swept.r == r) & (swept.wage == k) & (swept.country == c)]["work_minutes"]
                cells.append(f"{v.iloc[0]:.0f}" if len(v) else "—")
        lines.append(f"| {c} | " + " | ".join(cells) + " |")

    lines += ["", "## (3) per-family spread (r=3, PPP work_minutes)", "",
              "> Note: this spread bundles TWO effects — the family's tokenizer fertility AND its",
              "> representative anchor model's price (e_real = (1e6/p_blend)/fertility uses that",
              "> family's live model price). So a large spread is the *deployment* reality (which",
              "> model+tokenizer you are routed to), not fertility alone. A fertility-only lottery",
              "> is in reports/fertility_report.md.", "",
              "| country | min | max | min family | max family | max/min |", "|---|---|---|---|---|---|"]
    for _, r in fam.iterrows():
        ratio = r["max"] / r["min"] if r["min"] else float("nan")
        lines.append(f"| {r['country']} | {r['min']:.0f} | {r['max']:.0f} | "
                     f"{r['min_family']} | {r['max_family']} | {ratio:.2f}× |")

    lines += ["", "## (4) input-only vs output-only pricing (PPP work_minutes)", "",
              "| country | input-only | output-only | ratio |", "|---|---|---|---|"]
    for c in FOCUS:
        i = io[(io.pricing == "input_only") & (io.country == c)]["work_minutes"]
        o = io[(io.pricing == "output_only") & (io.country == c)]["work_minutes"]
        if len(i) and len(o):
            lines.append(f"| {c} | {i.iloc[0]:.0f} | {o.iloc[0]:.0f} | {o.iloc[0]/i.iloc[0]:.2f}× |")

    lines += ["", "## Not yet swept (flagged)",
              "- FLORES+ vs UDHR fertility genre check (needs UDHR corpus ingest).",
              "- Wage-tier swaps (Tier 1 ILOSTAT / Tier 3 minimum wage) — only World Bank Tier-2",
              "  is populated in this run; the pipeline supports the column when tiers are added."]
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    # loud summary of the tokenizer lottery
    if len(fam):
        worst = fam.loc[(fam["max"] / fam["min"]).idxmax()]
        print(f"  tokenizer-lottery worst spread: {worst['country']} "
              f"{worst['min']:.0f}–{worst['max']:.0f} min ({worst['max']/worst['min']:.1f}×)")


if __name__ == "__main__":
    main()
