# Datasheet — Cost-of-Intelligence Affordability Panel

Structured following the *Datasheets for Datasets* framework (Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daumé III, H., & Crawford, K. (2021). *Datasheets for Datasets.* Communications of the ACM, 64(12), 86–92).

All quantitative figures are placeholders to be filled from downstream artifacts. Derived assumptions are tagged `[INFERENCE]`.

---

## Motivation

- **For what purpose was the dataset created?**
  To build a compiled *affordability panel* that combines tokenizer fertility, live model prices, and wage/PPP data so that the cost of LLM "intelligence" can be expressed in economically meaningful units (real cost, wage-equivalence, work-minutes) across languages — with a focus on the Lusophone and Hispanophone Global South.
- **Framing note (honest novelty).** This panel *extends* prior cost-measurement work (notably "The African Language Tax") from raw cost to *affordability* and *adoption consequences*; it does not claim to originate the tokenizer-fertility-tax concept.
- **Who created the dataset / on behalf of whom / funding?** {{author, affiliation, funding — or "independent/unfunded"}}

## Composition

- **What do the instances represent?**
  Rows in a panel keyed by (language × tokenizer family × price snapshot × wage reference), plus derived instrument columns.
- **Coverage.**
  - **Fertility** (tokens per unit text) for **≥10 languages × 6 tokenizer families**, measured on **FLORES-200 devtest**.
  - **Prices** — per-model input/output token prices.
  - **Wages / PPP** — income references per country.
  - **The four instruments** (derived): e_real, Intelligence Wage, work-minutes Affordability Index, Language Tax. {{see writeup §3 for formulas}}
- **How many instances are there total?** {{from results_tables.md}}
- **Does the dataset contain all possible instances or a sample?** Sample — {{languages, families, and countries actually included, and selection rationale}}.
- **What data does each instance consist of?** {{list columns: language code, tokenizer family, fertility, input price, output price, GNI/PPP wage, retrieval date, derived instruments}}
- **Is any information missing?** {{note languages/countries with missing wage or price data}}
- **Are relationships between instances explicit?** Yes — shared language codes and tokenizer-family IDs link fertility, price, and wage rows.
- **Recommended splits?** None — this is a descriptive/analytic panel, not a train/test resource.

## Sources & Tiers

- **FLORES-200 devtest** — via `Muennighoff/flores200` (Hugging Face). License: **CC-BY-SA-4.0**. Used for fertility measurement.
- **OpenRouter** — **live** model prices, date-stamped at pull time.
- **World Bank** — GNI and GDP-PPP for wages.
  - **Tier-2 wage proxy = GNI / 2080 hours** `[INFERENCE]` — the 2080-hour full-time-year divisor is an assumption used to convert annual income to an hourly wage; it is not a sourced country-specific figure.
- **Anthropic Economic Index** — adoption / usage signals for the adoption analysis.
- **Source tiers.** {{define Tier-1 (direct/authoritative) vs Tier-2 (proxy/derived) and label each source accordingly}}

## Retrieval Dates

- **All price and adoption data are live-pulled and date-stamped.** Every OpenRouter price snapshot and every Economic Index pull carries a retrieval timestamp; results are only valid as of those dates. {{table of source → retrieval date from results_tables.md}}
- FLORES-200 and World Bank vintages: {{dataset version / year}}.

## Preprocessing / Cleaning / Labeling

- **Fertility computation.** {{describe tokenization procedure per family on FLORES-200 devtest}}
- **Price normalization.** {{per-token unit conventions, input vs output handling}}
- **Wage derivation.** GNI → hourly via the 2080-hour divisor `[INFERENCE]`; PPP adjustment {{describe}}.
- **Was raw data saved?** {{yes/no + location}}

## Uses

- **Intended uses.**
  - Economics/policy: quantifying the affordability gap in LLM access across languages and incomes.
  - Measuring the "Language Tax" and its wage-equivalence.
  - Correlational adoption analysis (see writeup §4 — **association, not causation**).
- **Uses to avoid.** Causal claims about adoption; strong claims where Law-of-One-Price and per-family assumptions fail (see Known Limitations).

## Distribution

- **Data license:** **CC-BY-4.0.**
- **Code license:** **MIT.**
- **How distributed / where?** {{repo / HF URL}}
- **Third-party terms.** FLORES-200 portions remain **CC-BY-SA-4.0**; OpenRouter and World Bank data subject to their respective terms. {{enumerate}}

## Maintenance

- **Maintainer / contact:** {{}}
- **Update cadence.** Prices and adoption are live sources; note re-pull policy and how stale snapshots are versioned. {{}}
- **Error reporting / contributions:** {{issue tracker / policy}}

## Known Limitations

See **`docs/caveats.md`** for the full list. Highlighted here:

- **C1 — Law of One Price.** {{one line}} The panel assumes comparable pricing across the market in ways that may not hold.
- **C2 — Input/output r assumption.** Assumes a fixed input-to-output ratio r; sensitivity {{from caveats.md}}.
- **C3 — Per-family measurement.** Fertility is measured per tokenizer family, not per individual model; models sharing a family are assumed to share fertility.
- **C7 — Output-fertility assumption.** Output token counts are approximated via {{assumption}}; this may misstate output-side cost.
- **FLORES `por_Latn` variant ambiguity.** FLORES-200 Portuguese (`por_Latn`) does not distinguish pt-PT / pt-BR / pt-AO, so language-variant granularity is limited on the fertility side. {{note how this is handled}}
- **Wage-tier crudeness for Angola / Mozambique.** GNI/2080h `[INFERENCE]` is especially crude where informal economies dominate; treat Angola and Mozambique wage figures as coarse proxies.
