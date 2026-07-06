"""Generate Stream B figures from data/fertility.parquet (Task B-10, initial set).

All figures are date-stamped (data-retrieval discipline, G2). Run: python src/figures.py
Outputs PNG + SVG into figures/.
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
FERT = ROOT / "data" / "fertility.parquet"
FIGDIR = ROOT / "figures"
STAMP = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
SUB = "FLORES-200 devtest · source Muennighoff/flores200 · " + STAMP

# Colorblind-safe qualitative palette (Okabe–Ito), one per family.
FAMILY_COLORS = {
    "openai_o200k": "#0072B2", "openai_cl100k": "#56B4E9", "llama3": "#D55E00",
    "qwen2": "#009E73", "gemma": "#CC79A7", "aya": "#E69F00",
}


def _save(fig, name: str) -> None:
    FIGDIR.mkdir(exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(FIGDIR / f"{name}.{ext}", bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"  wrote figures/{name}.png|svg")


def fig_heatmap(df: pd.DataFrame) -> None:
    piv = df.pivot(index="language_name", columns="family", values="fertility")
    piv = piv.loc[piv.mean(axis=1).sort_values().index]
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(piv.values, aspect="auto", cmap="YlOrRd", vmin=1.0)
    ax.set_xticks(range(len(piv.columns)))
    ax.set_xticklabels(piv.columns, rotation=40, ha="right", fontsize=9)
    ax.set_yticks(range(len(piv.index)))
    ax.set_yticklabels(piv.index, fontsize=9)
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            v = piv.values[i, j]
            ax.text(j, i, f"{v:.1f}", ha="center", va="center",
                    color="black" if v < 4 else "white", fontsize=8)
    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("fertility (× English tokens)")
    ax.set_title("The tokenizer lottery: tokens to express the same meaning\n"
                 "relative to English, by language and tokenizer family", fontsize=11)
    fig.text(0.12, 0.02, SUB, fontsize=7, color="gray")
    _save(fig, "fig_fertility_heatmap")


def fig_language_tax(df: pd.DataFrame, family: str = "openai_o200k") -> None:
    sub = df[df.family == family].sort_values("fertility")
    sub = sub[sub.language != "eng_Latn"]
    fig, ax = plt.subplots(figsize=(8, 5))
    y = range(len(sub))
    err = np.vstack([sub.fertility - sub.ci_low, sub.ci_high - sub.fertility])
    ax.barh(y, sub.fertility - 1, color=FAMILY_COLORS[family], left=1, height=0.6)
    ax.errorbar(sub.fertility, y, xerr=err, fmt="none", ecolor="black", capsize=2, lw=0.8)
    ax.axvline(1.0, color="gray", lw=1, ls="--")
    ax.set_yticks(list(y))
    ax.set_yticklabels(sub.language_name, fontsize=9)
    ax.set_xlabel("fertility = tokens per meaning, ÷ English  (1.0 = parity)")
    for yi, (_, r) in zip(y, sub.iterrows()):
        ax.text(r.fertility + 0.05, yi, f"+{r.fertility-1:.0%}", va="center", fontsize=8)
    ax.set_title(f"The Language Tax ({family})\nhow much more it costs to say the "
                 "same thing, in tokens", fontsize=11)
    ax.text(0, -0.13, SUB, transform=ax.transAxes, fontsize=7, color="gray")
    _save(fig, "fig_language_tax")


def fig_tokenizer_lottery(df: pd.DataFrame) -> None:
    """For a handful of languages, show the spread across families (the lottery)."""
    langs = ["por_Latn", "swh_Latn", "yor_Latn", "amh_Ethi"]
    sub = df[df.language.isin(langs)]
    order = sub.groupby("language").fertility.mean().sort_values().index
    fig, ax = plt.subplots(figsize=(8, 5))
    for i, lang in enumerate(order):
        d = sub[sub.language == lang]

        for _, r in d.iterrows():
            ax.scatter(r.fertility, i, s=60, color=FAMILY_COLORS[r.family],
                       label=r.family if i == 0 else "", zorder=3, edgecolor="white", lw=0.5)
        ax.plot([d.fertility.min(), d.fertility.max()], [i, i], color="lightgray", lw=2, zorder=1)
        ax.text(d.fertility.max() + 0.1, i,
                f"{d.fertility.min():.1f}–{d.fertility.max():.1f}×", va="center", fontsize=8)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([df[df.language == lc].language_name.iloc[0] for lc in order])
    ax.set_xlabel("fertility (× English tokens)")
    ax.axvline(1.0, color="gray", ls="--", lw=1)
    ax.legend(title="tokenizer family", fontsize=8, loc="lower right")
    ax.set_title("Same language, different tax: fertility depends on which\n"
                 "tokenizer family you happen to be routed to", fontsize=11)
    ax.text(0, -0.13, SUB, transform=ax.transAxes, fontsize=7, color="gray")
    _save(fig, "fig_tokenizer_lottery")


def main() -> None:
    df = pd.read_parquet(FERT)
    print("Generating figures...")
    fig_heatmap(df)
    fig_language_tax(df)
    fig_tokenizer_lottery(df)


if __name__ == "__main__":
    main()
