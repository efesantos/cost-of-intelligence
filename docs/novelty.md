# Honest Novelty Statement (Stream B §B2)

This page states plainly what already exists (and must be cited, never claimed) and what Stream B
adds. Every "what is new" claim is tagged **[INFERENCE until final prior-art check B-13]** — the
novelty is provisional until the final prior-art pass (see `prior_art_log.md`) confirms nothing
below has been published.

**Required framing sentence (verbatim):**

> We extend The African Language Tax from cost measurement to affordability measurement and adoption
> consequences, and from African languages to the Lusophone/Hispanophone Global South.

---

## Already published — cite, never claim

We claim **none** of the following as ours. They are prior art we consume and build on:

- **Petrov et al. 2023 — arXiv:2305.15425.** Cross-language tokenizer "tax": languages differ in
  tokens-per-text, imposing a systematic cost/context penalty. Foundational fertility-disparity result.
- **"The African Language Tax" — arXiv:2606.24460 (2026).** The direct anchor paper we extend. It
  establishes the African tokenizer tax **including FX conversion** (§6.3), **FX-compounding**
  (§6.6), and a **one-line wage equivalence** (§10.1: cost ≈ "1,340 annual minimum-wage salaries").
  Note precisely what it does **not** do, since that scopes our contribution: it does **not** build a
  constructed affordability index, does **not** link to adoption data, and does **not** cover
  Portuguese/Spanish.
- **Token price indices (consumed, not invented):** Silicon Data **SDLLMTK**, **BenchLM**,
  **inferencepriceindex.com**, **Epoch AI**. We consume token-price signals; we do not claim to have
  created a token price index.
- **Stanford AI Index** — quality-adjusted cost-of-intelligence deflation. Method lineage for
  treating intelligence cost as a deflating, quality-adjusted quantity.
- **UBS Prices & Earnings / Big Mac "minutes of work."** Affordability-method lineage — the
  "minutes of local labour to buy X" construction. (See caveat C1: we borrow the *affordability*
  method, **not** the currency-valuation inference.)
- **Anthropic Economic Index** — McCrory et al. 2025, arXiv:2511.15080; HF dataset
  `Anthropic/EconomicIndex`. Source of the adoption outcome.
- **Clio** — 2024, arXiv:2412.13678. Prior privacy-preserving usage-analysis method.

---

## What is new (Stream B's defensible contribution)

Each point is provisional — **[INFERENCE until final prior-art check B-13]**:

- **(a) A constructed multi-country affordability index.** [INFERENCE until final prior-art check
  B-13] A purpose-built index expressing the token bundle as **local work-minutes** across multiple
  countries — going beyond the anchor paper's single-line wage equivalence to a systematic,
  cross-country constructed index.
- **(b) `e_real` and the Intelligence Wage as formal, reusable, family-stratified objects.**
  [INFERENCE until final prior-art check B-13] The real intelligence exchange rate
  `e_real = (1e6 / p_blend) ÷ fertility` and the Intelligence Wage `IW = e_real × hourly_wage` are
  defined as first-class, reusable, tokenizer-family-stratified quantities, not one-off numbers.
- **(c) The adoption linkage (load-bearing).** [INFERENCE until final prior-art check B-13]
  Regressing country-level Anthropic Economic Index adoption on the affordability penalty, with
  controls — **fully absent from the prior work above.** This is the load-bearing novelty and is
  reported strictly as correlational (see `adoption_analysis_plan.md`).
- **(d) Lusophone/Hispanophone stratification, including variant-level fertility.** [INFERENCE until
  final prior-art check B-13] Extending the analysis to Portuguese and Spanish and the
  Lusophone/Hispanophone Global South, including **variant-level** fertility (e.g. pt-AO, pt-MZ) —
  languages the anchor paper does not cover.

---

## Discipline

We never say "we discover." We say "**we extend X**." If B-13 surfaces any of (a)–(d) in prior
work, the corresponding claim is downgraded to "we extend / replicate" and this page is updated
before submission.
