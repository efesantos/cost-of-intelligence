"""UDHR fertility cross-check -- genre-robustness of the language tax (Stream B
sensitivity: two-corpora check).

FLORES-200 is parallel *news* text. If the measured fertility (tokens-per-meaning
relative to English) is a genuine property of a language under a tokenizer -- and
not an artefact of the news genre -- it should reproduce on a very different genre.
The Universal Declaration of Human Rights (legal/declarative prose, human
translated, fixed structure of preamble + 30 articles) is that second genre.

This module:
  1. Downloads the Unicode UDHR XML for every FLORES language we can map
     (`unicode-org/udhr`, data/udhr/*.xml), cached with a
     retrieval timestamp to data/raw/udhr/.
  2. Aligns each language to English by (section, paragraph-index) unit id -- the
     UDHR's fixed structure makes this a true parallel corpus. Only unit ids
     present in BOTH English and the target language are kept (robust to the rare
     translation that merges/splits a paragraph).
  3. Computes fertility per (language, family) with the SAME tokenlab paired
     bootstrap used for FLORES (seed=0), writing data/udhr_fertility.parquet.
  4. Compares UDHR vs FLORES o200k fertility and flags any language where they
     differ by >15% relative (`genre_flag`), and writes reports/udhr_crosscheck.md.

Source: UDHR in XML project (https://github.com/unicode-org/udhr; the Unicode
Consortium stopped hosting https://www.unicode.org/udhr/ in January 2024). No
licence file was found in that repository, so no licence is claimed for the files.
"""
from __future__ import annotations

import datetime
import json
import pathlib
import time
import xml.etree.ElementTree as ET
from typing import Dict

import pandas as pd
import requests
import yaml

from tokenlab import fertility as F
from tokenlab import tokenizers as T

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "udhr"
LANG_CONFIG = ROOT / "config" / "languages.yaml"
FLORES_FERT = ROOT / "data" / "fertility.parquet"
OUT_PARQUET = ROOT / "data" / "udhr_fertility.parquet"
OUT_REPORT = ROOT / "reports" / "udhr_crosscheck.md"

N_RESAMPLES = 10_000
SEED = 0
GENRE_THRESHOLD = 0.15  # relative-difference flag: |UDHR - FLORES| / FLORES

BASE_URL = "https://raw.githubusercontent.com/unicode-org/udhr/main/data/udhr/{fname}"

# FLORES-200 code -> Unicode UDHR filename. Variant chosen to match the FLORES /
# panel primary country where the UDHR project ships country/orthography variants
# (e.g. Nigerian Hausa, European Portuguese, modern German 1996, modern-orthography
# Romanian 2006, monotonic Greek). [INFERENCE] variant choices flagged in report.
UDHR_FILES: Dict[str, str] = {
    "eng_Latn": "udhr_eng.xml",
    "por_Latn": "udhr_por_PT.xml",   # [INFERENCE] European PT (FLORES por primary = PRT)
    "spa_Latn": "udhr_spa.xml",
    "fra_Latn": "udhr_fra.xml",
    "swh_Latn": "udhr_swh.xml",
    "hau_Latn": "udhr_hau_NG.xml",   # [INFERENCE] Nigerian Hausa (primary = NGA)
    "yor_Latn": "udhr_yor.xml",
    "zul_Latn": "udhr_zul.xml",
    "amh_Ethi": "udhr_amh.xml",
    "arb_Arab": "udhr_arb.xml",
    "hin_Deva": "udhr_hin.xml",
    "zho_Hans": "udhr_cmn_hans.xml",  # Mandarin, Simplified
    "ind_Latn": "udhr_ind.xml",
    "vie_Latn": "udhr_vie.xml",
    "tha_Thai": "udhr_tha.xml",
    "tur_Latn": "udhr_tur.xml",
    "rus_Cyrl": "udhr_rus.xml",
    "deu_Latn": "udhr_deu_1996.xml",  # [INFERENCE] modern (1996 reform) orthography
    "ita_Latn": "udhr_ita.xml",
    "pol_Latn": "udhr_pol.xml",
    "jpn_Jpan": "udhr_jpn.xml",
    "kor_Hang": "udhr_kor.xml",
    "ben_Beng": "udhr_ben.xml",
    "tgl_Latn": "udhr_tgl.xml",
    "ukr_Cyrl": "udhr_ukr.xml",
    "ron_Latn": "udhr_ron_2006.xml",  # [INFERENCE] most recent (2006) orthography
    "ell_Grek": "udhr_ell_monotonic.xml",  # modern monotonic Greek
    "pes_Arab": "udhr_pes_1.xml",
}


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fetch(fname: str, max_retries: int = 6) -> str | None:
    """Download one UDHR XML, cached to disk. Returns XML text or None on failure."""
    RAW.mkdir(parents=True, exist_ok=True)
    cache = RAW / fname
    if cache.exists():
        return cache.read_text(encoding="utf-8")
    url = BASE_URL.format(fname=fname)
    last = None
    for attempt in range(max_retries):
        try:
            r = requests.get(url, timeout=45)
            r.raise_for_status()
            text = r.text
            cache.write_text(text, encoding="utf-8")
            (RAW / f"{fname}.meta.json").write_text(
                json.dumps({"retrieved_at": _now(), "url": url, "bytes": len(text)})
            )
            return text
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(min(2 ** attempt, 20))
    print(f"    WARN {fname} failed after retries: {last}")
    return None


def _parse_units(xml_text: str) -> Dict[str, str]:
    """Parse a UDHR XML into {unit_id -> paragraph text}.

    Unit ids are stable across translations because the UDHR structure is fixed:
    ``preamble:0, preamble:1, ...`` and ``artN:0, artN:1, ...`` (paragraph index
    within the preamble / within article N). All ``<para>`` descendants are taken
    in document order -- including those nested inside ``<orderedlist>/<listitem>``
    sub-clauses (many articles number their points that way). ``<title>`` elements
    are skipped so only declaration prose is measured (article labels like
    "Article 1" would add cross-language noise). Namespaces are stripped for
    robustness.
    """
    root = ET.fromstring(xml_text)

    def tag(el) -> str:
        return el.tag.rsplit("}", 1)[-1]  # strip {namespace}

    units: Dict[str, str] = {}
    for section in root:
        sec = tag(section)
        if sec == "preamble":
            key = "preamble"
        elif sec == "article":
            key = f"art{section.get('number')}"
        else:
            continue  # skip <title>, <note>, etc. at top level
        idx = 0
        for para in section.iter():
            if tag(para) != "para":
                continue
            text = "".join(para.itertext()).strip()
            if text:
                units[f"{key}:{idx}"] = text
                idx += 1
    return units


def _load_udhr() -> Dict[str, Dict[str, str]]:
    """Return {flores_code -> {unit_id -> text}} for every mappable language.

    Requirements for this to succeed offline: the Unicode UDHR XML files listed in
    ``UDHR_FILES`` present under data/raw/udhr/ (they are fetched on first run from
    ``unicode-org/udhr``). Each file must be a valid UDHR XML with <preamble> and
    <article number=...> sections. Languages whose download fails are skipped and
    reported, never faked.
    """
    out: Dict[str, Dict[str, str]] = {}
    for code, fname in UDHR_FILES.items():
        xml_text = _fetch(fname)
        if xml_text is None:
            continue
        try:
            units = _parse_units(xml_text)
        except ET.ParseError as e:
            print(f"    WARN {code} ({fname}) parse failed: {e}")
            continue
        if units:
            out[code] = units
            print(f"  {code:10s} {len(units):3d} units <- {fname}")
    return out


def main() -> None:
    cfg = yaml.safe_load(LANG_CONFIG.read_text())
    names = cfg["names"]
    ref = cfg["reference"]

    print("Loading UDHR (Unicode udhr XML, cached)...")
    corpora = _load_udhr()
    if ref not in corpora:
        raise SystemExit(
            "UDHR English (eng_Latn) unavailable -- cannot form the reference. "
            "See reports/udhr_crosscheck.md for the blocker. Ensure data/raw/udhr/"
            "udhr_eng.xml is present (network required on first run)."
        )
    en = corpora[ref]

    families = list(T.REGISTRY)
    flores = pd.read_parquet(FLORES_FERT)

    rows = []
    for code, units in corpora.items():
        shared = sorted(set(units) & set(en))
        lang_aligned = {sid: units[sid] for sid in shared}
        en_aligned = {sid: en[sid] for sid in shared}
        for family in families:
            try:
                res = F.compute_fertility(
                    lang_aligned, en_aligned, family=family, language=code,
                    n_resamples=N_RESAMPLES, seed=SEED,
                )
            except Exception as e:  # noqa: BLE001
                print(f"    WARN {code}/{family}: {str(e)[:80]}")
                continue
            rows.append({
                "language": code, "language_name": names.get(code, code),
                "family": family, "fertility": res.fertility,
                "ci_low": res.ci_low, "ci_high": res.ci_high,
                "n_units": len(shared),
                "total_tokens_lang": res.total_tokens_lang,
                "total_tokens_en": res.total_tokens_en,
            })

    df = pd.DataFrame(rows)

    # Join FLORES fertility per (language, family) for the genre comparison.
    fl = flores[["language", "family", "fertility"]].rename(
        columns={"fertility": "flores_fertility"})
    df = df.merge(fl, on=["language", "family"], how="left")
    df["rel_diff"] = (df["fertility"] - df["flores_fertility"]).abs() / df["flores_fertility"]
    df["genre_flag"] = df["rel_diff"] > GENRE_THRESHOLD

    df = df.sort_values(["family", "fertility"]).reset_index(drop=True)
    OUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT_PARQUET, index=False)

    _write_report(df, corpora, families, names, ref)
    n_lang = df["language"].nunique()
    n_flag = int(df[df.family == "openai_o200k"]["genre_flag"].sum())
    print(f"wrote {OUT_PARQUET} ({len(df)} rows, {n_lang} languages) and {OUT_REPORT}")
    print(f"  o200k genre flags (>15% UDHR vs FLORES): {n_flag}")


def _write_report(df, corpora, families, names, ref) -> None:
    o = df[df.family == "openai_o200k"].sort_values("fertility")
    n_flag = int(o["genre_flag"].sum())
    lines = [
        "# UDHR fertility cross-check (genre robustness)",
        "",
        f"Generated: {_now()}  |  bootstrap resamples: {N_RESAMPLES}, seed {SEED}",
        "",
        "Second-corpus sensitivity check for the language tax. FLORES-200 is parallel",
        "*news* text; the UDHR is human-translated *legal/declarative* prose with a",
        "fixed preamble + 30-article structure, aligned here by (section, paragraph)",
        "unit id. Fertility = corpus-total tokens in L / corpus-total tokens in English,",
        "same tokenlab paired-bootstrap machinery as the FLORES run. A `genre_flag` marks",
        f"any language where |UDHR - FLORES| / FLORES > {GENRE_THRESHOLD:.0%} for the o200k family.",
        "",
        "Source: UDHR in XML (github.com/unicode-org/udhr). No licence file was found in",
        "that repository, so no licence is claimed for the files. English is 1.000 by construction.",
        "",
        f"Coverage: {df['language'].nunique()} languages, {len(families)} tokenizer families. "
        f"o200k genre flags: {n_flag} / {len(o)}.",
        "",
        "## UDHR vs FLORES fertility (o200k family)",
        "",
        "| language | UDHR fertility [95% CI] | FLORES fertility | rel. diff | genre flag |",
        "|---|---|---|---|---|",
    ]
    for _, r in o.iterrows():
        fl = f"{r.flores_fertility:.3f}" if pd.notna(r.flores_fertility) else "—"
        rd = f"{r.rel_diff:.1%}" if pd.notna(r.rel_diff) else "—"
        flag = "**YES**" if bool(r.genre_flag) else ""
        lines.append(
            f"| {r.language_name} | {r.fertility:.3f} [{r.ci_low:.3f}, {r.ci_high:.3f}] "
            f"| {fl} | {rd} | {flag} |"
        )

    flagged = o[o.genre_flag].sort_values("rel_diff", ascending=False)
    lines += ["", "## Genre-sensitivity flags (o200k)", ""]
    if len(flagged):
        for _, r in flagged.iterrows():
            direction = "higher" if r.fertility > r.flores_fertility else "lower"
            lines.append(
                f"- **{r.language_name}**: UDHR {r.fertility:.3f} vs FLORES "
                f"{r.flores_fertility:.3f} ({r.rel_diff:.1%} {direction} on UDHR)."
            )
    else:
        lines.append("- None. Every mapped language reproduces its FLORES fertility "
                     "within 15% on UDHR text -- the language tax is genre-robust here.")

    # Full per-family flag counts.
    lines += ["", "## Genre flags per tokenizer family", "",
              "| family | languages flagged (>15%) |", "|---|---|"]
    for fam in families:
        sub = df[df.family == fam]
        lines.append(f"| {fam} | {int(sub['genre_flag'].sum())} / {len(sub)} |")

    # Alignment provenance.
    lines += ["", "## Alignment units per language", "",
              "Shared (section, paragraph) ids kept after intersecting with English.",
              "", "| language | UDHR file | shared units |", "|---|---|---|"]
    en_units = corpora[ref]
    for code in sorted(corpora, key=lambda c: names.get(c, c)):
        shared = len(set(corpora[code]) & set(en_units))
        lines.append(f"| {names.get(code, code)} | {UDHR_FILES[code]} | {shared} |")

    missing = [c for c in UDHR_FILES if c not in corpora]
    if missing:
        lines += ["", "## Languages not retrieved", "",
                  "Download/parse failed (network on first run); code would compute "
                  "these given the cached XML:", ""]
        lines += [f"- {names.get(c, c)} ({UDHR_FILES[c]})" for c in missing]

    lines += ["", "## Notes / assumptions", "",
              "- [INFERENCE] Where the UDHR project ships country/orthography variants, "
              "the variant matching the FLORES/panel primary country was chosen "
              "(European Portuguese, Nigerian Hausa, modern German 1996, Romanian 2006, "
              "monotonic Greek). This affects only which single translation is measured.",
              "- [INFERENCE] Titles (\"Article 1\") are excluded; only declaration prose "
              "paragraphs are tokenized, so cross-language label noise cannot inflate the ratio.",
              "- FLORES por_Latn is variant-ambiguous (see docs/flores_variant_note.md); the "
              "UDHR row here uses European Portuguese, so a Portuguese genre flag may partly "
              "reflect variant, not genre."]

    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
