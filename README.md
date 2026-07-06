# Cost of Intelligence

**What does intelligence actually cost people — in minutes of their own work — across
languages and countries? And does that cost predict who adopts AI?**

This repo treats the token as an economic unit and builds four reusable instruments,
then tests, correlationally, whether affordability gates adoption. It **extends
"The African Language Tax" (arXiv 2606.24460)** from cost measurement to
*affordability* and *adoption consequences*, and from African languages to the
Lusophone/Hispanophone Global South. See [`docs/novelty.md`](docs/novelty.md).

## The headline (live data, reproducible)

Minutes of local work to buy **1M English-equivalent tokens/month** (OpenAI o200k
family, PPP wages) — live OpenRouter prices + World Bank wages + FLORES-200 fertility:

| | minutes | | minutes |
|---|--:|---|--:|
| 🇺🇸 US (English) | ~11 | 🇿🇦 South Africa (Zulu) | ~112 |
| 🇵🇹 Portugal (Portuguese) | ~24 | 🇳🇬 Nigeria (Yoruba) | ~238 |
| 🇲🇽 Mexico (Spanish) | ~53 | 🇰🇪 Kenya (Swahili) | ~218 |
| 🇪🇬 Egypt (Arabic) | ~72 | 🇪🇹 Ethiopia (Amharic) | **~1,620** |

The same answer costs an Ethiopian worker on Amharic **~140× more minutes of labour**
than an American on English — fertility (more tokens per meaning) multiplied by lower
wages. *(Numbers regenerate with `make all`; exact values carry CIs and date stamps.)*

## The four instruments

| Instrument | Definition |
|---|---|
| **Real intelligence exchange rate** `e_real` | `(1e6 / p_blend) ÷ fertility` — English-equivalent tokens per USD |
| **Intelligence Wage** `IW` | `e_real × hourly_wage` — cognition an hour of local labour buys |
| **Affordability Index** `work_minutes` | `(bundle · fertility · p_blend / 1e6) ÷ wage × 60` — the Big Mac "minutes of work" method, done for tokens |
| **Language Tax** `surcharge` | `fertility − 1` — the regressive token surcharge |

`p_blend = (1·input + r·output)/(1+r)`, default `r=3` [INFERENCE, swept in B-9].
Everything is reported **per tokenizer family** — no single "the token."

## Adoption linkage (the load-bearing novelty)

Regressing country-level AI adoption (Anthropic Economic Index `usage_per_capita_index`,
Sept 2025) on affordability. Pre-registered in [`docs/adoption_analysis_plan.md`](docs/adoption_analysis_plan.md)
**before** the merge. Current result (N=9, honestly underpowered):

- **Spearman ρ(work_minutes, adoption) = −0.68 (p = 0.042)** — less affordable → less adoption.
- In OLS with a GDP-per-capita-PPP control the affordability coefficient loses significance
  (affordability is collinear with income) — *exactly* the pre-registered "the tax adds no
  explanatory power beyond income" outcome, which is itself informative.
- **Association, not causation.** Expanding the language set (→ more countries, N≥15) is the
  path to a better-powered estimate.

## What's built (all live-pulled, date-stamped, `make all`-reproducible)

- `src/corpus.py` + `src/run_fertility.py` — fertility for **12 languages × 6 tokenizer
  families** on FLORES-200 with paired bootstrap CIs. Identity + ordering sanity checks pass.
  See [`reports/fertility_report.md`](reports/fertility_report.md).
- `src/prices.py` — live OpenRouter anchor prices per family (flagship + small), snapshotted.
- `src/wages.py` — World Bank GNI (market + PPP) → hourly wage, Tier-2, + GDP-PPP & internet
  controls, for 23 countries (raw responses cached).
- `src/instruments.py` — the four instruments; identity + bundle-linearity unit-tested.
- `src/aei.py` — Economic Index outcome (`usage_per_capita_index`); see [`docs/aei_notes.md`](docs/aei_notes.md).
- `src/adoption.py` — the pre-registered regression + Spearman + leave-one-out.
- `src/sensitivity.py` — sweeps r ∈ {1,3,9}, market/PPP, per-family, input/output pricing.
- `src/figures_instruments.py` — headline "Minutes of work" lollipop, Intelligence Wage,
  adoption scatter. `docs/index.html` — interactive four-instrument explorer (GH-Pages).

## Caveats (binding — see [`docs/caveats.md`](docs/caveats.md))

C1 **Law of One Price**: tokens sell at one global USD price, so this is an *affordability*
index, **not** a currency-valuation claim. C3 per-family reporting. C7 output-fertility is an
assumption. Full list in the writeup and page footer.

## Reproduce

```bash
pip install -e ../tokenlab && pip install -r requirements.txt
make all      # corpus → fertility → prices → wages → instruments → figures
pytest -q
```

Anchor citation: **The African Language Tax** (arXiv 2606.24460), §6.3/§6.6 (FX) and §10.1
(wages). Also Petrov et al. 2023; Anthropic Economic Index (McCrory et al. 2025); FLORES-200.
Data CC-BY-4.0; code MIT.
