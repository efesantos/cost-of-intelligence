"""FLORES-200 corpus download + alignment (Stream B, Task B-1 part 1).

Downloads the FLORES-200 devtest split for the configured language set and writes
one aligned JSONL per language ({id -> sentence}) into data/raw/flores/ with a
`retrieved_at` timestamp header, per the live-data rule (G2).

Source: `Muennighoff/flores200` (ungated mirror of FLORES-200; the canonical
`openlanguagedata/flores_plus` and `facebook/flores` are gated). FLORES-200 is
CC-BY-SA-4.0. The mirror is loaded via its loading script (trust_remote_code).

Alignment: every language pair `eng_Latn-<lang>` shares the same sentence `id`,
so the English column is identical across pairs and the corpus is truly parallel.
"""
from __future__ import annotations

import datetime
import json
import pathlib
from typing import Dict, List

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "flores"
CONFIG = ROOT / "config" / "languages.yaml"


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_config() -> dict:
    return yaml.safe_load(CONFIG.read_text())


def all_languages(cfg: dict) -> List[str]:
    seen, out = set(), []
    for group in ("launch", "extension", "panel"):
        for lang in cfg.get(group) or []:
            if lang not in seen:
                seen.add(lang)
                out.append(lang)
    return out


def download(split: str = "devtest") -> Dict[str, pathlib.Path]:
    """Download + write aligned JSONL per language. Returns {lang: path}."""
    from datasets import load_dataset

    cfg = load_config()
    ref = cfg["reference"]
    RAW.mkdir(parents=True, exist_ok=True)
    written: Dict[str, pathlib.Path] = {}

    unavailable = []
    for lang in all_languages(cfg):
        if lang == ref:
            pair = f"{ref}-por_Latn"  # any pair carries the identical eng column
            col = f"sentence_{ref}"
        else:
            pair = f"{ref}-{lang}"
            col = f"sentence_{lang}"
        try:
            ds = load_dataset("Muennighoff/flores200", pair, split=split, trust_remote_code=True)
        except Exception as e:  # noqa: BLE001 -- skip languages absent from FLORES-200
            unavailable.append((lang, type(e).__name__))
            print(f"  {lang:10s} UNAVAILABLE ({type(e).__name__}) -- skipped")
            continue
        aligned = {str(row["id"]): row[col] for row in ds}
        out = RAW / f"{lang}.jsonl"
        with out.open("w", encoding="utf-8") as fh:
            fh.write(json.dumps({"_meta": {
                "language": lang, "split": split, "source": "Muennighoff/flores200",
                "license": "CC-BY-SA-4.0", "retrieved_at": _now(), "n_sentences": len(aligned),
            }}, ensure_ascii=False) + "\n")
            for sid, text in aligned.items():
                fh.write(json.dumps({"id": sid, "text": text}, ensure_ascii=False) + "\n")
        written[lang] = out
        print(f"  {lang:10s} {len(aligned):5d} sentences -> {out.name}")
    if unavailable:
        print(f"  {len(unavailable)} unavailable: {[u[0] for u in unavailable]}")
    return written


def read_aligned(lang: str) -> Dict[str, str]:
    """Read a written JSONL back into {id -> text}, skipping the _meta line."""
    out: Dict[str, str] = {}
    for line in (RAW / f"{lang}.jsonl").read_text(encoding="utf-8").splitlines():
        rec = json.loads(line)
        if "_meta" in rec:
            continue
        out[rec["id"]] = rec["text"]
    return out


if __name__ == "__main__":
    print("Downloading FLORES-200 devtest for configured languages...")
    download()
    print("done.")
