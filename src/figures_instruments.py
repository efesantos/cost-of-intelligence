"""Instrument + adoption figures (Task B-10). Runs after instruments.parquet,
aei.parquet exist. Date-stamped with the price snapshot's retrieval date (G2).
Outputs PNG+SVG+PDF to figures/ (the PDFs are what the LaTeX paper includes).
"""
from __future__ import annotations

import datetime
import pathlib

import matplotlib
matplotlib.use("Agg")
matplotlib.rcdefaults()  # same look whatever the local matplotlibrc says
matplotlib.rcParams["svg.hashsalt"] = "cost-of-intelligence"  # stable SVG ids
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIGDIR = ROOT / "figures"
_PRICES = yaml.safe_load((ROOT / "config" / "prices.yaml").read_text())
STAMP = _PRICES["_meta"]["retrieved_at"][:10] if "_meta" in _PRICES else \
    datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
SUB = f"OpenRouter prices retrieved {STAMP} + World Bank wages + FLORES-200 fertility"


def _save(fig, name):
    FIGDIR.mkdir(exist_ok=True)
    # no creation timestamps in the files, so re-running only changes them when data change
    meta = {"png": {}, "svg": {"Date": None}, "pdf": {"CreationDate": None}}
    for ext in ("png", "svg", "pdf"):
        fig.savefig(FIGDIR / f"{name}.{ext}", bbox_inches="tight", dpi=150, metadata=meta[ext])
    plt.close(fig)
    print(f"  wrote figures/{name}.png|svg")


def fig_work_minutes(instr, family="openai_o200k"):
    """Headline figure: both World Bank Tier-2 bases for every country, side by side.
    Market rate is the like-for-like basis for a single US$ token price (C1); PPP is shown
    with it, never instead of it."""
    d = instr[instr.family == family].dropna(subset=["work_minutes_market", "work_minutes_ppp"]).copy()
    d = d.sort_values("work_minutes_market")
    fig, ax = plt.subplots(figsize=(8, 6.5))
    y = np.arange(len(d))
    ax.hlines(y, d["work_minutes_ppp"], d["work_minutes_market"], color="#c9c9c9", lw=2, zorder=1)
    ax.scatter(d["work_minutes_ppp"], y, color="#56B4E9", s=40, zorder=2,
               label="PPP wage (GNI PPP / 2080 h)")
    ax.scatter(d["work_minutes_market"], y, color="#0072B2", s=40, zorder=3,
               label="market-rate wage (GNI Atlas / 2080 h)")
    for yi, (_, r) in zip(y, d.iterrows()):
        ax.annotate(f"{r.work_minutes_ppp:,.0f} / {r.work_minutes_market:,.0f}",
                    (r.work_minutes_market, yi), xytext=(6, 0), textcoords="offset points",
                    va="center", fontsize=7)
    ax.set_xscale("log")
    ax.set_xlim(d["work_minutes_ppp"].min() * 0.7, d["work_minutes_market"].max() * 3)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{r.country_name} ({r.language_name})" for _, r in d.iterrows()], fontsize=8)
    ax.set_xlabel("minutes of local work to buy 1M English-equivalent tokens a month (log scale)")
    ax.set_title("Minutes of work to buy the same monthly bundle\n"
                 "World Bank wages at PPP and at market exchange rates (labels: PPP / market)",
                 fontsize=11)
    ax.legend(fontsize=8, loc="lower right")
    fig.text(0.1, 0.01, SUB, fontsize=7, color="gray")
    _save(fig, "fig_work_minutes")


def fig_work_minutes_single(instr, family="openai_o200k", kind="ilo"):
    d = instr[instr.family == family].dropna(subset=[f"work_minutes_{kind}"]).copy()
    d = d.sort_values(f"work_minutes_{kind}")
    fig, ax = plt.subplots(figsize=(8, 6))
    y = range(len(d))
    ax.hlines(y, 0, d[f"work_minutes_{kind}"], color="#c9c9c9", lw=1.5, zorder=1)
    ax.scatter(d[f"work_minutes_{kind}"], y, color="#0072B2", s=45, zorder=2)
    us = d[d.country == "USA"][f"work_minutes_{kind}"]
    if len(us):
        ax.axvline(us.iloc[0], color="#D55E00", ls="--", lw=1, label="US / English reference")
    ax.set_yticks(list(y))
    ax.set_yticklabels([f"{r.country_name} ({r.language_name})" for _, r in d.iterrows()], fontsize=8)
    for yi, (_, r) in zip(y, d.iterrows()):
        ax.annotate(f"{r[f'work_minutes_{kind}']:,.0f}", (r[f"work_minutes_{kind}"], yi), xytext=(6, 0),
                    textcoords="offset points", va="center", fontsize=7)
    ax.set_xlim(right=d[f"work_minutes_{kind}"].max() * 1.1)
    ax.set_xlabel("minutes of local work to buy 1M English-equivalent tokens/month  "
                  f"({kind.upper()} wages)")
    basis = {"ppp": "World Bank GNI, PPP", "ilo": "ILOSTAT actual earnings, market US$",
             "market": "World Bank GNI, market US$"}[kind]
    ax.set_title(f"Minutes of work to buy the same answer\n({basis})", fontsize=12)
    ax.legend(fontsize=8, loc="lower right")
    fig.text(0.1, 0.01, SUB, fontsize=7, color="gray")
    _save(fig, f"fig_work_minutes_{kind}")


def fig_intelligence_wage(instr, family="openai_o200k", kind="ppp"):
    d = instr[instr.family == family].dropna(subset=[f"iw_{kind}_tokens_per_hour"]).copy()
    d = d.sort_values(f"iw_{kind}_tokens_per_hour", ascending=True)
    fig, ax = plt.subplots(figsize=(8, 6))
    y = range(len(d))
    ax.barh(y, d[f"iw_{kind}_tokens_per_hour"] / 1e6, color="#009E73", height=0.6)
    ax.set_yticks(list(y))
    ax.set_yticklabels([f"{r.country_name} ({r.language_name})" for _, r in d.iterrows()], fontsize=8)
    ax.set_xlabel("Intelligence Wage: millions of English-equivalent tokens "
                  f"per hour of local work ({kind.upper()})")
    ax.set_title("The Intelligence Wage: what an hour of local work buys", fontsize=12)
    fig.text(0.1, 0.01, SUB, fontsize=7, color="gray")
    _save(fig, "fig_intelligence_wage")


def fig_adoption_scatter(family="openai_o200k", kind="ppp"):
    """The regression panel itself (one row per country, as in src/adoption.py), so the
    points are exactly the N the paper reports."""
    import adoption
    d = adoption.build_panel(family=family, wage_kind=kind)
    if len(d) < 3:
        print("  (adoption scatter skipped: <3 points)")
        return
    fig, ax = plt.subplots(figsize=(7.5, 6))
    x = np.log(d["work_minutes"])
    yv = np.log(d["usage_per_capita_index"])
    ax.scatter(x, yv, color="#0b5cad", s=40, zorder=3)
    nudge = {"PHL": (3, -9), "FRA": (-18, 4)}  # keep neighbouring labels apart
    for _, r in d.iterrows():
        ax.annotate(r["country"], (np.log(r["work_minutes"]), np.log(r["usage_per_capita_index"])),
                    fontsize=7, xytext=nudge.get(r["country"], (3, 3)), textcoords="offset points")
    b, a = np.polyfit(x, yv, 1)
    xs = np.linspace(x.min(), x.max(), 50)
    ax.plot(xs, a + b * xs, color="#D55E00", lw=1.5,
            label=f"bivariate fit, slope {b:.2f} (no income control)")
    ax.set_xlabel(f"log(minutes of work to buy 1M Etok, {kind.upper()} wage)  →  less affordable")
    ax.set_ylabel("log(AEI usage per-capita index)  →  more adoption")
    ax.set_title(f"Affordability and adoption, N = {len(d)} countries (association only)", fontsize=11)
    ax.legend(fontsize=8)
    fig.text(0.1, 0.01, "AEI usage_per_capita_index (release 2025-09-15) · " + SUB, fontsize=7, color="gray")
    _save(fig, "fig_adoption_scatter")


def fig_wage_basis(instr, family="openai_o200k"):
    """All three wage bases side by side: WB market rate, WB PPP, ILOSTAT (market US$).
    Token prices are one global US$ price (C1), so the market-rate bars are the
    like-for-like basis; the PPP bars divide a US$ price by a PPP wage."""
    d = instr[instr.family == family].dropna(subset=["work_minutes_ppp", "work_minutes_ilo"]).copy()
    d = d.sort_values("work_minutes_market")
    fig, ax = plt.subplots(figsize=(8, 7.5))
    y = np.arange(len(d))
    h = 0.27
    # top to bottom within each country: market, PPP, ILOSTAT (the legend's order)
    ax.barh(y + h, d["work_minutes_market"], height=h, color="#0072B2",
            label="World Bank Tier-2, market rate (GNI Atlas / 2080 h)")
    ax.barh(y, d["work_minutes_ppp"], height=h, color="#56B4E9",
            label="World Bank Tier-2, PPP (GNI PPP / 2080 h)")
    ax.barh(y - h, d["work_minutes_ilo"], height=h, color="#D55E00",
            label="ILOSTAT Tier-1 (mean employee earnings, market US$)")
    ax.set_yticks(y)
    ax.set_yticklabels([f"{r.country_name} ({r.language_name})" for _, r in d.iterrows()], fontsize=8)
    ax.set_xlabel("minutes of local work to buy 1M English-equivalent tokens/month (log scale)")
    ax.set_xscale("log")
    ax.set_title("Three wage bases, reported side by side", fontsize=11)
    ax.legend(fontsize=7.5, loc="lower right")
    fig.text(0.1, 0.01, SUB, fontsize=7, color="gray")
    _save(fig, "fig_wage_basis_comparison")


def main():
    instr = pd.read_parquet(ROOT / "data" / "instruments.parquet")
    print("Generating instrument figures...")
    fig_work_minutes(instr)
    fig_work_minutes_single(instr, kind="ilo")
    fig_intelligence_wage(instr)
    fig_adoption_scatter()
    fig_wage_basis(instr)


if __name__ == "__main__":
    main()
