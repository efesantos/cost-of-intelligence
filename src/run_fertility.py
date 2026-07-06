"""Compute fertility for every (language, tokenizer family) and emit artifacts
(Stream B, Task B-1 part 2).

Outputs:
  * data/fertility.parquet          -- tidy table: language, family, fertility, CI, ...
  * reports/fertility_report.md     -- human-readable table + sanity-check log

Acceptance checks enforced here (B-1):
  * EN fertility == 1.000 for every family (identity check).
  * Every configured language x family cell populated or logged unavailable.
  * Ordering sanity: fertility(Latin-script European lang) < fertility(Ge'ez Amharic)
    per family, consistent with Petrov et al. 2023's published pattern -- if
    violated, we flag it loudly (halt-and-escalate in the plan).
"""
from __future__ import annotations

import datetime
import pathlib

import pandas as pd

import corpus
from tokenlab import fertility as F
from tokenlab import tokenizers as T

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_PARQUET = ROOT / "data" / "fertility.parquet"
OUT_REPORT = ROOT / "reports" / "fertility_report.md"
N_RESAMPLES = 10_000
SEED = 0


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> None:
    cfg = corpus.load_config()
    names = cfg["names"]
    ref = cfg["reference"]
    langs = corpus.all_languages(cfg)
    families = [f for f in T.REGISTRY]

    aligned = {lang: corpus.read_aligned(lang) for lang in langs}
    en = aligned[ref]

    rows, unavailable, sanity = [], [], []
    for family in families:
        try:
            T.count("probe", family)
        except Exception as e:  # noqa: BLE001
            unavailable.append((family, "*", f"family load failed: {type(e).__name__}"))
            continue
        for lang in langs:
            try:
                res = F.compute_fertility(
                    aligned[lang], en, family=family, language=lang,
                    n_resamples=N_RESAMPLES, seed=SEED,
                )
                rows.append({
                    "language": lang, "language_name": names.get(lang, lang),
                    "family": family, "fertility": res.fertility,
                    "ci_low": res.ci_low, "ci_high": res.ci_high,
                    "n_sentences": res.n_sentences,
                    "total_tokens_lang": res.total_tokens_lang,
                    "total_tokens_en": res.total_tokens_en,
                })
            except Exception as e:  # noqa: BLE001
                unavailable.append((family, lang, str(e)[:80]))

    df = pd.DataFrame(rows).sort_values(["family", "fertility"]).reset_index(drop=True)
    OUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT_PARQUET, index=False)

    # --- identity check: EN == 1.000 per family ---
    identity_ok = True
    for family in df["family"].unique():
        en_val = df[(df.family == family) & (df.language == ref)]["fertility"]
        if len(en_val) == 0 or abs(float(en_val.iloc[0]) - 1.0) > 1e-9:
            identity_ok = False
            sanity.append(f"IDENTITY FAIL: {family} EN fertility = {en_val.values}")
    if identity_ok:
        sanity.append("IDENTITY OK: English fertility == 1.000 for every family.")

    # --- ordering sanity: European Latin < Amharic Ge'ez per family ---
    for family in df["family"].unique():
        sub = df[df.family == family].set_index("language")["fertility"]
        if "amh_Ethi" in sub.index and "fra_Latn" in sub.index:
            if sub["fra_Latn"] < sub["amh_Ethi"]:
                sanity.append(f"ORDER OK ({family}): French {sub['fra_Latn']:.2f} < Amharic {sub['amh_Ethi']:.2f}")
            else:
                sanity.append(f"ORDER WARN ({family}): French {sub['fra_Latn']:.2f} !< Amharic {sub['amh_Ethi']:.2f}")

    _write_report(df, families, unavailable, sanity, ref, names)
    print(f"wrote {OUT_PARQUET} ({len(df)} rows) and {OUT_REPORT}")
    for line in sanity:
        print("  " + line)


def _write_report(df, families, unavailable, sanity, ref, names) -> None:
    lines = [
        "# Fertility report (FLORES-200 devtest)",
        "",
        f"Generated: {_now()}  |  bootstrap resamples: {N_RESAMPLES}, seed {SEED}",
        "",
        "Fertility = corpus-total tokens in language L / corpus-total tokens in English,",
        "per tokenizer family. English is 1.000 by construction. 95% CI from a paired",
        "sentence-level bootstrap. Source: Muennighoff/flores200 (CC-BY-SA-4.0).",
        "",
        "## Fertility by language x family",
        "",
    ]
    piv = df.pivot(index="language_name", columns="family", values="fertility")
    # order rows by mean fertility across families
    piv = piv.loc[piv.mean(axis=1).sort_values().index]
    header = "| language | " + " | ".join(piv.columns) + " |"
    sep = "|" + "---|" * (len(piv.columns) + 1)
    lines += [header, sep]
    for lang_name, row in piv.iterrows():
        cells = " | ".join(f"{v:.3f}" if pd.notna(v) else "—" for v in row)
        lines.append(f"| {lang_name} | {cells} |")

    lines += ["", "## Language Tax (surcharge = fertility − 1), o200k family", ""]
    o = df[df.family == "openai_o200k"].sort_values("fertility")
    lines += ["| language | fertility [95% CI] | surcharge |", "|---|---|---|"]
    for _, r in o.iterrows():
        lines.append(f"| {r.language_name} | {r.fertility:.3f} [{r.ci_low:.3f}, {r.ci_high:.3f}] | +{r.fertility-1:.0%} |")

    lines += ["", "## Sanity checks", ""]
    lines += [f"- {s}" for s in sanity]
    if unavailable:
        lines += ["", "## Unavailable cells", ""]
        lines += [f"- {fam} / {lang}: {reason}" for fam, lang, reason in unavailable]
    else:
        lines += ["", "All configured language × family cells populated."]

    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
