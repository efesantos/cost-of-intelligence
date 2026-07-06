"""Model price layer (Stream B, Task B-2).

Pulls the OpenRouter model list + live per-token prices, saves a timestamped raw
snapshot (G2 live-data rule), and resolves one *anchor* model per tokenizer
family (a flagship + a small) so downstream instruments have a concrete,
date-stamped price to divide by.

Why OpenRouter as the price source: it is a single live API covering all
families, listed as a valid ⟲ source in the plan. First-party pricing-page
snapshots (Anthropic/OpenAI/Google) are a recommended manual cross-check (save
HTML to data/raw/prices/) but are not required for the pipeline to run.

Prices are reported **input and output separately** and never hardcoded from
memory. A blended price uses p_blend = (1*input + r*output)/(1+r), default r=3
[INFERENCE — swept in sensitivity B-9].
"""
from __future__ import annotations

import datetime
import json
import pathlib

import requests
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "prices"
OUT_YAML = ROOT / "config" / "prices.yaml"
OPENROUTER = "https://openrouter.ai/api/v1/models"

# Family -> ordered candidate substrings for [flagship, small]. The resolver
# picks the first NON-FREE model id containing each substring. Recorded exactly.
# Gemini stands in for the Gemma/SentencePiece tokenizer family price [INFERENCE];
# Cohere Command stands in for the Aya tokenizer family [INFERENCE].
ANCHORS = {
    "openai_o200k": {"flagship": ["openai/gpt-4o", "openai/gpt-4.1"],
                     "small": ["openai/gpt-4o-mini", "openai/gpt-4.1-mini"]},
    "llama3": {"flagship": ["meta-llama/llama-3.3-70b-instruct", "meta-llama/llama-3.1-70b-instruct"],
               "small": ["meta-llama/llama-3.1-8b-instruct", "meta-llama/llama-3.2-3b-instruct"]},
    "qwen2": {"flagship": ["qwen/qwen-2.5-72b-instruct", "qwen/qwen2.5-72b-instruct"],
              "small": ["qwen/qwen-2.5-7b-instruct", "qwen/qwen2.5-7b-instruct"]},
    "gemma": {"flagship": ["google/gemma-2-27b-it", "google/gemini-2.5-flash", "google/gemini-2.0-flash"],
              "small": ["google/gemma-2-9b-it", "google/gemini-2.0-flash-lite", "google/gemini-2.5-flash-lite"]},
    "aya": {"flagship": ["cohere/command-r-plus", "cohere/command-a"],
            "small": ["cohere/command-r7b", "cohere/command-r-08"]},
}

# Ids containing any of these are non-text or alias variants -> never anchors.
_BLOCK = ("search", "preview", "image", "audio", "realtime", "tts", "vision",
          "embed", "moderation", "~", ":free", ":thinking", "-online")


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def pull_snapshot() -> tuple[list, str, pathlib.Path]:
    RAW.mkdir(parents=True, exist_ok=True)
    ts = _now()
    resp = requests.get(OPENROUTER, timeout=30)
    resp.raise_for_status()
    payload = resp.json()
    day = ts[:10].replace("-", "")
    path = RAW / f"openrouter_{day}.json"
    path.write_text(json.dumps({"_retrieved_at": ts, "source": OPENROUTER, **payload}, indent=2))
    return payload["data"], ts, path


def _resolve(models_by_id: dict, substrings: list) -> str | None:
    for sub in substrings:
        # exact base-id match first (e.g. "openai/gpt-4o"), then base with a
        # date/version suffix (e.g. "openai/gpt-4o-2024-11"); never noisy variants.
        candidates = []
        for mid, m in models_by_id.items():
            if not mid.startswith(sub):
                continue
            if any(b in mid for b in _BLOCK):
                continue
            pr = m.get("pricing", {})
            if float(pr.get("prompt", 0) or 0) <= 0:
                continue
            # exact match ranks above suffixed variants
            candidates.append((0 if mid == sub else 1, len(mid), mid))
        if candidates:
            return sorted(candidates)[0][2]
    return None


def build() -> dict:
    models, ts, snap = pull_snapshot()
    by_id = {m["id"]: m for m in models}
    resolved = {}
    for family, tiers in ANCHORS.items():
        resolved[family] = {}
        for tier, subs in tiers.items():
            mid = _resolve(by_id, subs)
            if mid is None:
                resolved[family][tier] = {"model": None, "note": "no non-free match found"}
                continue
            pr = by_id[mid]["pricing"]
            resolved[family][tier] = {
                "model": mid,
                "input_usd_per_mtok": round(float(pr["prompt"]) * 1e6, 6),
                "output_usd_per_mtok": round(float(pr["completion"]) * 1e6, 6),
                "source": "openrouter",
                "source_url": OPENROUTER,
                "retrieved_at": ts,
            }
    out = {"_meta": {"retrieved_at": ts, "snapshot": str(snap.relative_to(ROOT)),
                     "note": "prices in USD per 1M tokens; input & output separate; "
                             "Gemini stands in for gemma-family price [INFERENCE]; "
                             "Cohere Command for aya-family price [INFERENCE]"},
           "anchors": resolved}
    OUT_YAML.parent.mkdir(parents=True, exist_ok=True)
    OUT_YAML.write_text(yaml.safe_dump(out, sort_keys=False, allow_unicode=True))
    return out


if __name__ == "__main__":
    out = build()
    print(f"wrote {OUT_YAML.relative_to(ROOT)} (retrieved {out['_meta']['retrieved_at']})")
    for fam, tiers in out["anchors"].items():
        for tier, d in tiers.items():
            if d.get("model"):
                print(f"  {fam:14s} {tier:8s} {d['model']:42s} "
                      f"in=${d['input_usd_per_mtok']}/Mtok out=${d['output_usd_per_mtok']}/Mtok")
            else:
                print(f"  {fam:14s} {tier:8s} UNRESOLVED")
