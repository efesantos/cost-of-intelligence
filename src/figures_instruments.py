"""Instrument + adoption figures (Task B-10). Runs after instruments.parquet,
aei.parquet exist. Date-stamped (G2). Outputs PNG+SVG to figures/.
"""
from __future__ import annotations

import datetime
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIGDIR = ROOT / "figures"
STAMP = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
SUB = f"live prices (OpenRouter) + World Bank wages + FLORES-200 fertility · {STAMP}"


def _save(fig, name):
    FIGDIR.mkdir(exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(FIGDIR / f"{name}.{ext}", bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"  wrote figures/{name}.png|svg")


def fig_work_minutes(instr, family="openai_o200k", kind="ppp"):
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
        ax.text(r[f"work_minutes_{kind}"] * 1.02, yi, f"{r[f'work_minutes_{kind}']:.0f}", va="center", fontsize=7)
    ax.set_xlabel("minutes of local work to buy 1M English-equivalent tokens/month  "
                  f"({kind.upper()} wages)")
    ax.set_title("Minutes of work to buy the same answer", fontsize=12)
    ax.legend(fontsize=8, loc="lower right")
    fig.text(0.1, 0.01, SUB, fontsize=7, color="gray")
    _save(fig, "fig_work_minutes")


def fig_intelligence_wage(instr, family="openai_o200k", kind="ppp"):
    d = instr[instr.family == family].dropna(subset=[f"iw_{kind}_tokens_per_hour"]).copy()
    d = d.sort_values(f"iw_{kind}_tokens_per_hour", ascending=True)
    fig, ax = plt.subplots(figsize=(8, 6))
    y = range(len(d))
    ax.barh(y, d[f"iw_{kind}_tokens_per_hour"] / 1e6, color="#009E73", height=0.6)
    ax.set_yticks(list(y))
    ax.set_yticklabels([f"{r.country_name}" for _, r in d.iterrows()], fontsize=8)
    ax.set_xlabel("Intelligence Wage: millions of English-equivalent tokens "
                  f"per hour of local work ({kind.upper()})")
    ax.set_title("The Intelligence Wage: cognition an hour of labour buys", fontsize=12)
    fig.text(0.1, 0.01, SUB, fontsize=7, color="gray")
    _save(fig, "fig_intelligence_wage")


def fig_adoption_scatter(instr, family="openai_o200k", kind="ppp"):
    aei = pd.read_parquet(ROOT / "data" / "aei.parquet")[["country", "usage_per_capita_index"]]
    d = instr[instr.family == family].dropna(subset=[f"work_minutes_{kind}"])
    d = d.merge(aei, on="country")
    d = d[(d.usage_per_capita_index > 0) & (d.work_minutes_ppp > 0)]
    if len(d) < 3:
        print("  (adoption scatter skipped: <3 points)")
        return
    fig, ax = plt.subplots(figsize=(7.5, 6))
    x = np.log(d[f"work_minutes_{kind}"])
    yv = np.log(d["usage_per_capita_index"])
    ax.scatter(x, yv, color="#0b5cad", s=40, zorder=3)
    for _, r in d.iterrows():
        ax.annotate(r["country"], (np.log(r[f"work_minutes_{kind}"]),
                    np.log(r["usage_per_capita_index"])), fontsize=7,
                    xytext=(3, 3), textcoords="offset points")
    # OLS fit line
    b, a = np.polyfit(x, yv, 1)
    xs = np.linspace(x.min(), x.max(), 50)
    ax.plot(xs, a + b * xs, color="#D55E00", lw=1.5, label=f"slope={b:.2f}")
    ax.set_xlabel(f"log(minutes of work to buy 1M Etok, {kind.upper()})  →  less affordable")
    ax.set_ylabel("log(AEI usage per-capita index)  →  more adoption")
    ax.set_title("Affordability vs adoption (correlational)", fontsize=12)
    ax.legend(fontsize=8)
    fig.text(0.1, 0.01, "AEI usage_per_capita_index (Sept 2025) · " + SUB, fontsize=7, color="gray")
    _save(fig, "fig_adoption_scatter")


def main():
    instr = pd.read_parquet(ROOT / "data" / "instruments.parquet")
    print("Generating instrument figures...")
    fig_work_minutes(instr)
    fig_intelligence_wage(instr)
    fig_adoption_scatter(instr)


if __name__ == "__main__":
    main()
