# Honest Novelty Statement (Stream B §B2)

This page states plainly what already exists (and must be cited, never claimed) and what Stream B
adds. The final prior-art pass (B-13) was run on 2026-10-10; its queries and outcomes are in
`prior_art_log.md`. Each claim below carries its verdict from that pass.

**Required framing sentence (verbatim):**

> We extend The African Language Tax from cost measurement to affordability measurement and adoption
> consequences, and from African languages to the Lusophone/Hispanophone Global South.

---

## Already published — cite, never claim

We claim **none** of the following as ours. They are prior art we consume and build on:

- **Petrov et al. 2023 — arXiv:2305.15425 (NeurIPS 2023).** Cross-language tokenizer "tax": languages
  differ in tokens-per-text, imposing a systematic cost/context penalty. Foundational
  fertility-disparity result.
- **Ahia et al. 2023 — EMNLP 2023 (arXiv:2305.13707).** API cost disparities across languages, using
  the Human Development Index as a proxy for affordability. The closest earlier link between
  tokenizer cost and income.
- **Solatorio et al. 2024 — arXiv:2410.10665.** FLORES-200 plus World Bank income groups: speakers of
  languages from lower-income countries pay more per API call.
- **Sathish et al. 2024 (LLeMpower) — arXiv:2404.09356.** A flat subscription price compared with
  income across countries.
- **Somide 2026, "The African Language Tax" — arXiv:2606.24460.** The direct anchor paper we extend.
  It establishes the African tokenizer tax **including FX conversion** (§6.3), **FX-compounding**
  (§6.6), and a **one-line wage equivalence** (§10.1: the annual cost of one illustrative Amharic
  customer-service deployment is "roughly 1,340 annual salaries at the Nigerian minimum wage").
  Note precisely what it does **not** do, since that scopes our contribution: it does **not** build a
  constructed affordability index, does **not** link to adoption data, and does **not** cover
  Portuguese/Spanish.
- **Ovcharov 2026 — arXiv:2605.24718.** Tokenizer fertility across European languages, including
  Portuguese and Spanish.
- **Misra et al. 2025 — arXiv:2511.02752.** Country-level AI adoption is about 20% lower in
  low-resource-language countries after socio-economic controls. The closest earlier link between
  language and adoption; it has no tokenizer, price or wage measure.
- **ITU, *The affordability of ICT services 2024* (2025).** Affordability as price ÷ monthly GNI per
  capita. On the World Bank Tier-2 basis our work-minutes index is exactly 104 × the ITU ratio.
- **Token price indices (consumed, not invented):** Silicon Data **SDLLMTK**, the **BenchLM** Token
  Price Index, **Epoch AI**'s inference-price trends. We consume token-price signals; we do not claim
  to have created a token price index.
- **Stanford AI Index 2025** — falling inference cost at a fixed performance level. Method lineage
  for treating machine cognition as a good whose price falls over time.
- **UBS *Prices & Earnings* "minutes of work"** (last edition 2018) and **Ashenfelter 2012** ("Big Macs
  per hour"). Affordability-method lineage. (See caveat C1: we borrow the *affordability* method,
  **not** the *Economist* Big Mac index's currency-valuation inference.)
- **Anthropic Economic Index** — Appel et al. 2025, arXiv:2511.15080; HF dataset
  `Anthropic/EconomicIndex`. Source of the adoption outcome, and of the income elasticity of usage
  (about 0.7) that our income control echoes.
- **Clio** — Tamkin et al. 2024, arXiv:2412.13678. Prior privacy-preserving usage-analysis method.

---

## What is new (Stream B's defensible contribution)

- **(a) A constructed multi-country affordability index.** **Stands** (no conflict found). A
  purpose-built index expressing a fixed token bundle as **local work-minutes** across 28 languages
  and 40 countries, carrying fertility, live prices and three wage bases. It goes beyond the anchor
  paper's single-line wage equivalence; Ahia et al. 2023, Solatorio et al. 2024 and Sathish et al.
  2024 relate cost to income but build no per-country work-time index. We describe it as extending
  the ITU affordability ratio to LLM tokens.
- **(b) `e_real` and the Intelligence Wage as formal, reusable, family-stratified objects.**
  **Stands** (no conflict found). The real intelligence exchange rate
  `e_real = (1e6 / p_blend) ÷ fertility` and the Intelligence Wage `IW = e_real × hourly_wage` are
  defined as first-class, reusable, tokenizer-family-stratified quantities, not one-off numbers.
- **(c) The adoption linkage (load-bearing).** **Narrowed.** Regressing country-level Anthropic
  Economic Index adoption on the affordability penalty, with controls. No earlier work links a
  tokenizer-and-wage affordability measure to adoption data, but Misra et al. 2025 already links
  language-resource status to adoption, so we say "we extend Misra et al. (2025)" and do **not** say
  the link is absent from prior work. Reported strictly as correlational (see
  `adoption_analysis_plan.md`).
- **(d) Lusophone/Hispanophone stratification.** **Narrowed.** Portuguese and Spanish *fertility* is
  already published (Ahia et al. 2023; Ovcharov 2026), so for fertility we say "we extend". What
  stands is the *affordability* cut across the Lusophone and Hispanophone Global South (Portugal,
  Brazil, Angola, Mozambique; Mexico, Colombia, Spain). The earlier claim of **variant-level**
  fertility (pt-AO, pt-MZ) is **withdrawn**: FLORES-200 has one Portuguese and the paper reports no
  variant results.

---

## Discipline

We never say "we discover." We say "**we extend X**." If later work surfaces any of (a)–(d), the
corresponding claim is downgraded to "we extend / replicate" and this page is updated.
