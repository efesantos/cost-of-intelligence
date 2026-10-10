"""Sensitivity battery (Task B-9).

Sweeps the modelling choices and reports the range each headline number takes, so
"which choices move the numbers" is explicit. Axes implemented here:
  (1) input:output ratio r in {1, 3, 9}
  (2) market FX vs PPP wages
  (3) per-tokenizer-family spread (the "tokenizer lottery")
  (4) input-only vs output-only pricing (r -> 0 and r -> large)
  (5) all three wage bases side by side (WB market, WB PPP, ILOSTAT)

Rows are (country, language) pairs, so a country with two languages (Nigeria:
Hausa + Yoruba) is never silently averaged, and the Lusophone alternates (BRA, AGO,
MOZ) are computed from the alternate country mapping. The FLORES vs UDHR genre
check is in reports/udhr_crosscheck.md.
"""
from __future__ import annotations

import pathlib

import pandas as pd

import instruments as I

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "sensitivity.md"

# Focus (country, language) pairs for the headline "work_minutes" number.
FOCUS = [("USA", "eng_Latn"), ("PRT", "por_Latn"), ("BRA", "por_Latn"), ("AGO", "por_Latn"),
         ("MOZ", "por_Latn"), ("KEN", "swh_Latn"), ("NGA", "hau_Latn"), ("NGA", "yor_Latn"),
         ("ETH", "amh_Ethi")]


def _label(c, lang):
    return f"{c} ({lang.split('_')[0]})"


def _work_minutes_table(r, kind, family="openai_o200k"):
    df = I.compute(r=r, price_tier="flagship", include_alternates=True)
    df = df[df.family == family]
    return df.set_index(["country", "language"])[f"work_minutes_{kind}"]


def main():
    rows = []
    # (1) r sweep + (2) market/ppp, o200k family
    for r in (1, 3, 9):
        for kind in ("market", "ppp"):
            wm = _work_minutes_table(r, kind)
            for c in FOCUS:
                if c in wm.index and pd.notna(wm[c]):
                    rows.append({"axis": "r_and_wagebasis", "r": r, "wage": kind,
                                 "country": _label(*c), "work_minutes": wm[c]})
    swept = pd.DataFrame(rows)

    # (3) per-family spread at r=3, ppp
    base = I.compute(r=3, include_alternates=True)
    fam_rows = []
    for c, lang in FOCUS:
        sub = base[(base.country == c) & (base.language == lang)].dropna(subset=["work_minutes_ppp"])
        if len(sub):
            fam_rows.append({"country": _label(c, lang),
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
                io_rows.append({"pricing": label, "country": _label(*c), "work_minutes": wm[c]})
    io = pd.DataFrame(io_rows)

    lines = ["# Sensitivity battery (Task B-9)", "",
             "Every headline `work_minutes` number with its range across modelling choices.",
             "Bundle = 1M English-equivalent tokens/month. Family = o200k unless noted.", ""]

    lines += ["## (1)+(2) r ratio x wage basis (o200k)", "",
              "| country | " + " | ".join(f"r={r},{k}" for r in (1, 3, 9) for k in ("mkt", "ppp")) + " |",
              "|" + "---|" * 7]
    for c in [_label(*p) for p in FOCUS]:
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
    for c in [_label(*p) for p in FOCUS]:
        i = io[(io.pricing == "input_only") & (io.country == c)]["work_minutes"]
        o = io[(io.pricing == "output_only") & (io.country == c)]["work_minutes"]
        if len(i) and len(o):
            lines.append(f"| {c} | {i.iloc[0]:.0f} | {o.iloc[0]:.0f} | {o.iloc[0]/i.iloc[0]:.2f}× |")

    wb = base[base.family == "openai_o200k"].set_index(["country", "language"])
    lines += ["", "## (5) three wage bases side by side (o200k, r=3)", "",
              "> World Bank Tier-2 is GNI per capita / 2080 h, in market US$ (Atlas) or PPP int$;",
              "> ILOSTAT Tier-1 is mean monthly employee earnings in US$ / (40 h x 4.333 weeks).",
              "> Token prices are one global US$ price (caveat C1), so the market-rate columns are",
              "> the like-for-like basis; PPP divides a US$ price by a PPP wage.", "",
              "| country | WB market | WB PPP | ILOSTAT | market/PPP |", "|---|---|---|---|---|"]
    for c in FOCUS:
        if c in wb.index:
            r_ = wb.loc[c]
            ilo_v = f"{r_['work_minutes_ilo']:.0f}" if pd.notna(r_["work_minutes_ilo"]) else "—"
            lines.append(f"| {_label(*c)} | {r_['work_minutes_market']:.0f} | {r_['work_minutes_ppp']:.0f} | "
                         f"{ilo_v} | {r_['work_minutes_market'] / r_['work_minutes_ppp']:.2f}× |")

    lines += ["", "## Other sensitivity axes (separate reports)",
              "- **FLORES vs UDHR fertility** genre check: see `reports/udhr_crosscheck.md`",
              "  (a second, legal-prose corpus). Portuguese/Spanish/French are stable (<7%);",
              "  several languages (e.g. Vietnamese, Yoruba, Hausa) are strongly genre-sensitive.",
              "- **Wage-tier swap in the adoption regression** (pre-registered check 2): see",
              "  `reports/adoption_results.md`. ILOSTAT coverage notes: `reports/ilostat_wages.md`."]
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    # loud summary of the tokenizer lottery
    if len(fam):
        worst = fam.loc[(fam["max"] / fam["min"]).idxmax()]
        print(f"  tokenizer-lottery worst spread: {worst['country']} "
              f"{worst['min']:.0f}–{worst['max']:.0f} min ({worst['max']/worst['min']:.1f}×)")


if __name__ == "__main__":
    main()
