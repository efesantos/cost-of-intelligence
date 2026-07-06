# {{Title — e.g. "The Cost of Intelligence: From Language Tax to Affordability and Adoption in the Lusophone/Hispanophone Global South"}}

> **Target length:** 3,000–4,500 words. This file is a skeleton: section headers, 1–2 sentence statements of intent, and `{{placeholders}}`. No result numbers are invented here.

> **Framing sentence (load-bearing — keep verbatim):** We extend *The African Language Tax* from cost measurement to affordability measurement and adoption consequences, and from African languages to the Lusophone/Hispanophone Global South.

---

## Abstract

{{Placeholder — 150–250 words.}} **State up front, not buried:** the adoption analysis is **correlational, not causal** — affordability is collinear with development, and we report only whether the Language Tax adds explanatory power beyond income, not whether it causes non-adoption. Summarize the four instruments and the Luanda/Lisbon/São Paulo sub-study at a glance with `{{}}` placeholders.

---

## 1. The Token as an Economic Unit

Frame the token as the atomic unit of LLM cost, and motivate why tokenizer fertility (tokens per unit of meaning) turns a flat per-token price into an unequal per-language price.

- Why per-token pricing is not per-meaning pricing. {{}}
- Why this matters for non-English, lower-resourced languages. {{}}

## 2. Prior Art

- **Anchor being EXTENDED — "The African Language Tax"**, arXiv:2606.24460.
  - Cite **§6.3 / §6.6** for the FX and FX-compounding treatment we build on. {{what they show; what we extend}}
  - Cite **§10.1** for the one-line wage-equivalence they gesture at, which we develop into a full instrument. {{}}
- **Petrov et al. 2023**, arXiv:2305.15425 — tokenizer inequality across languages. {{}}
- **Price indices consumed (not invented) here:** SDLLMTK, BenchLM, inferencepriceindex, Epoch. {{what each provides}}
- **Stanford AI Index** — macro context on cost/compute trends. {{}}
- **UBS Prices & Earnings** — wage / cost-of-living reference methodology. {{}}
- **Anthropic Economic Index** — McCrory et al. 2025, arXiv:2511.15080 — adoption/usage signal. {{}}
- **Clio** — arXiv:2412.13678 — privacy-preserving usage analysis context. {{}}

Close by stating precisely what is new: affordability + adoption, and Lusophone/Hispanophone coverage — an extension, not a new measurement paradigm.

## 3. The Four Instruments

Define each instrument with its formula. {{fill formulas from analysis notebooks; do not invent numbers}}

- **3.1 e_real (real per-meaning cost).** {{formula}} — fertility-adjusted, FX-adjusted real cost of a unit of output.
- **3.2 Intelligence Wage.** {{formula}} — cost of a standard unit of model "work" expressed against local wages.
- **3.3 Work-minutes Affordability Index.** {{formula}} — minutes of local labor required to afford a standard task.
- **3.4 Language Tax.** {{formula}} — the multiplicative premium a language pays relative to the English baseline.

## 4. Adoption Analysis

**Fixed correlational framing (keep verbatim):** *association, not causation; affordability is collinear with development — we report whether the tax adds explanatory power beyond income, not whether it causes non-adoption.*

- Model specification: adoption regressed on income, with the Language Tax entered as an additional regressor to test incremental explanatory power. {{spec + `{{}}` results from results_tables.md}}
- What a positive/null result would and would not license us to say. {{}}

## 5. Lusophone Sub-Study

Decompose work-minutes affordability for three Portuguese-speaking cities — **Luanda vs. Lisbon vs. São Paulo** — into its **fertility × wage × FX** components.

- Component decomposition method. {{}}
- What the decomposition isolates (how much of the affordability gap is tokenizer fertility vs. local wage vs. exchange rate). {{from results_tables.md}}
- Note FLORES `por_Latn` variant ambiguity as a caveat on the fertility component (see DATASHEET / caveats.md). {{}}

## 6. Caveats

Reference **`docs/caveats.md`** — all seven caveats apply; summarize each in one line.

- **C1** Law of One Price. {{}}
- **C2** Input/output r assumption. {{}}
- **C3** Per-family fertility. {{}}
- **C4** {{from caveats.md}}
- **C5** {{from caveats.md}}
- **C6** {{from caveats.md}}
- **C7** Output-fertility assumption. {{}}

## 7. Policy / Economics Closing

Tie the instruments and the adoption analysis to policy implications for equitable AI access in the Global South, keeping the correlational caveat visible.

- What affordability (not just cost) reveals about access. {{}}
- What the Lusophone sub-study implies for pt-PT vs pt-BR vs pt-AO markets. {{}}
- Explicitly restate: correlational evidence; affordability is one lever among several. {{}}
