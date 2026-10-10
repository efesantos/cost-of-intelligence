# Cost of Intelligence

**What does intelligence actually cost people — in minutes of their own work — across
languages and countries? And does that cost predict who adopts AI?**

This repo treats the token as an economic unit and builds four reusable instruments,
then tests, correlationally, whether affordability gates adoption. It **extends
"The African Language Tax" (Somide 2026, arXiv 2606.24460)** from cost measurement to
*affordability* and *adoption consequences*, and from African languages to the
Lusophone/Hispanophone Global South. See [`docs/novelty.md`](docs/novelty.md).

- **Paper:** [`paper/main.pdf`](paper/main.pdf), built from [`writeup/README.md`](writeup/README.md) with `make paper`.
- **Interactive explorer:** <https://efesantos.github.io/cost-of-intelligence/> (source in [`docs/index.html`](docs/index.html)).

## The headline (reproducible)

Minutes of local work to buy **1M English-equivalent tokens a month** (OpenAI o200k
family, gpt-4o list price, r = 3), from FLORES-200 fertility, OpenRouter prices retrieved
on 2026-10-10 and World Bank GNI per capita. Tokens are paid for at market exchange rates,
so the market-rate column is the like-for-like one. The PPP column shows the burden as if
tokens were priced like local goods.

| Country (language) | PPP wage | Market-rate wage |
|---|--:|--:|
| 🇺🇸 United States (English) | 11 | 11 |
| 🇵🇹 Portugal (Portuguese) | 24 | 41 |
| 🇲🇽 Mexico (Spanish) | 53 | 97 |
| 🇿🇦 South Africa (Zulu) | 112 | 278 |
| 🇪🇬 Egypt (Arabic) | 72 | 429 |
| 🇰🇪 Kenya (Swahili) | 218 | 685 |
| 🇳🇬 Nigeria (Hausa) | 170 | 1,156 |
| 🇳🇬 Nigeria (Yoruba) | 238 | 1,616 |
| 🇪🇹 Ethiopia (Amharic) | **1,619** | **5,279** |

The same bundle costs a worker in Ethiopia, in Amharic, about **140 times** as many minutes
of work as a worker in the United States, in English, at PPP wages, and about **460 times**
at market-rate wages. Fertility (more tokens for the same meaning) contributes a factor of
about 5.8, and the wage gap a factor of about 25 at PPP or 80 at market rates. A third wage
basis, ILOSTAT mean earnings of employees, is in the paper (Table 2) and on the explorer.
*(`make results` regenerates every number from the committed data.)*

## The four instruments

| Instrument | Definition |
|---|---|
| **Real intelligence exchange rate** `e_real` | `(1e6 / p_blend) ÷ fertility` — English-equivalent tokens per USD |
| **Intelligence Wage** `IW` | `e_real × hourly_wage` — cognition an hour of local labour buys |
| **Affordability Index** `work_minutes` | `(bundle · fertility · p_blend / 1e6) ÷ wage × 60` — the UBS *Prices & Earnings* "minutes of work" method, done for tokens |
| **Language Tax** `surcharge` | `fertility − 1` — the regressive token surcharge |

`p_blend = (1·input + r·output)/(1+r)`, default `r=3` [INFERENCE, swept in B-9].
Everything is reported **per tokenizer family** — no single "the token."

## Adoption linkage (the load-bearing novelty)

Regressing country-level AI adoption (Anthropic Economic Index `usage_per_capita_index`,
Sept 2025 release) on affordability, following the analysis plan in
[`docs/adoption_analysis_plan.md`](docs/adoption_analysis_plan.md). The plan was committed in
the same commit as the data, so it cannot be shown to predate the analysis; the paper says so
and lists every deviation from it. Result over a **23-country** panel:

- **Spearman ρ(work_minutes, adoption) = −0.85 (p < 0.0001).** The more minutes of work the
  bundle costs, the lower the adoption.
- With a GDP-per-capita (PPP) control, the affordability coefficient is close to zero (−0.05,
  p = 0.92). Affordability and income are almost the same variable in this panel (r = −0.98),
  so the data cannot separate them.
- **Not robust.** The coefficient is negative on every wage basis but significant only with
  ILOSTAT wages (p = 0.019), and leaving out single countries flips its sign six times. The
  tokenizer part of affordability shows no association with adoption once income is controlled.
- **Association, not causation.** Affordability ranks countries' adoption well, but we cannot
  separate it from income with observational country data.

## What's built (all live-pulled, date-stamped, `make all`-reproducible)

- `src/corpus.py` + `src/run_fertility.py` — fertility for **28 languages × 6 tokenizer
  families** on FLORES-200 with paired bootstrap CIs. Identity + ordering sanity checks pass.
  See [`reports/fertility_report.md`](reports/fertility_report.md). A second-corpus genre
  cross-check (UDHR legal prose) is in [`reports/udhr_crosscheck.md`](reports/udhr_crosscheck.md).
  *Provenance note:* FLORES-200 is accessed via the ungated `Muennighoff/flores200` mirror
  (the canonical `flores_plus` is gated); recorded in the [`DATASHEET`](DATASHEET.md).
- `src/prices.py` — live OpenRouter anchor prices per family (flagship + small), snapshotted
  (latest snapshot 2026-10-10).
- `src/wages.py` — **three wage bases, all reported**: World Bank GNI at market rates
  (Atlas) and at PPP → hourly Tier-2 proxy for **40 countries**, plus ILOSTAT Tier-1 mean
  monthly employee earnings → hourly USD for **38 of the 40** (`data/ilostat_wages.parquet`);
  GDP-PPP & internet controls included (raw API responses cached). The wage-basis choice
  moves the numbers most for the poorest countries — see `fig_wage_basis_comparison` and
  the three cards on the interactive page.
- `src/instruments.py` — the four instruments; identity + bundle-linearity unit-tested.
- `src/aei.py` — Economic Index outcome (`usage_per_capita_index`); see [`docs/aei_notes.md`](docs/aei_notes.md).
- `src/adoption.py` — the planned regression, Spearman, leave-one-out and the plan's other
  robustness checks.
- `src/sensitivity.py` — sweeps r ∈ {1,3,9}, market/PPP, per-family, input/output pricing.
- `src/figures_instruments.py` — headline work-minutes chart (PPP and market rate side by
  side), Intelligence Wage, adoption scatter. `docs/index.html` — interactive four-instrument
  explorer (GH-Pages).
- `paper/build.py` — builds `paper/main.tex`, `paper/main.pdf` and the arXiv upload
  `paper/arxiv-source.tar.gz` from `writeup/README.md` (`make paper`; needs pandoc and pdflatex).

## Caveats (binding — see [`docs/caveats.md`](docs/caveats.md))

C1 **Law of One Price**: tokens sell at one global USD price, so this is an *affordability*
index, **not** a currency-valuation claim. C3 per-family reporting. C7 output-fertility is an
assumption. Full list in the writeup and page footer.

## Reproduce

```bash
pip install -r requirements.txt
make results  # every derived number, figure and report, offline, from the committed data
make paper    # paper/main.tex, paper/main.pdf and the arXiv upload (needs pandoc and pdflatex)
pytest -q

# full rebuild from the live sources (needs ../tokenlab and network access;
# re-fetching prices will move the numbers)
pip install -e ../tokenlab
make all
```

## Authorship & AI assistance

This project is **co-authored with Claude (Anthropic)**, by design. The workflow is a
deliberate planner/executor split: Elmer Santos sets the research direction, makes the
judgment calls, and personally executes the human gates (source checks, wage-basis and
scope decisions, final edits); Claude Fable 5 authored the execution-ready master plan;
Claude Opus 4.8 agents executed the build at $0 API spend. Every commit carries a
`Co-Authored-By: Claude` trailer, and every number regenerates from committed data
via `make all`.

The arXiv listing names the human author only. arXiv's policy is that generative AI tools
"should not be listed as an author"; the paper's "Use of AI assistance" section describes
how Claude was used.

---

Anchor citation: Somide (2026), **The African Language Tax** (arXiv 2606.24460), §6.3/§6.6 (FX)
and §10.1 (wages). Also Petrov et al. 2023; Anthropic Economic Index (Appel et al. 2025);
FLORES-200 (NLLB Team 2022). Code MIT; derived data and figures CC BY 4.0. Third-party raw
files keep their own terms (see the [`DATASHEET`](DATASHEET.md)).
