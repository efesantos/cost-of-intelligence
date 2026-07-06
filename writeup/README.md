# The Cost of Intelligence: a multi-country token affordability index and its link to AI adoption

> **Framing sentence (load-bearing — verbatim):** We extend *The African Language Tax* from cost measurement to affordability measurement and adoption consequences, and from African languages to the Lusophone/Hispanophone Global South.

---

## Abstract

Large language models are priced per token at a single global USD rate, but a token is not a fixed unit of meaning. Because tokenizers split some languages into far more pieces than English to convey the same content, a flat per-token price becomes an unequal per-meaning price — a "Language Tax." Prior work established this tax as a *cost* phenomenon. We extend it in two directions: to *affordability* (how much local labor time a fixed bundle of cognition costs) and to *adoption* (whether affordability tracks real-world model uptake), and from African languages to the Lusophone/Hispanophone Global South.

We measure tokenizer fertility on FLORES-200 (1,012 aligned sentences, 28 languages × 6 tokenizer families, with paired sentence-level bootstrap confidence intervals), combine it with live OpenRouter prices and two independent wage bases (World Bank Tier-2 and ILOSTAT Tier-1), and construct four reusable, family-stratified instruments. The headline is stark: under World Bank PPP wages, 1M English-equivalent tokens per month costs roughly 11 minutes of local work in the United States and roughly 1,620 minutes in Ethiopia operating in Amharic — about a 140× gap.

We then relate our affordability index to the Anthropic Economic Index (N = 23 countries). **This relationship is correlational, not causal.** The raw rank correlation is strong (Spearman ρ = −0.85, p < 0.0001), but affordability is collinear with national income: once GDP per capita (PPP) is controlled, the affordability coefficient collapses to approximately zero (p ≈ 0.92). We report this pre-registered, now well-powered "informative null" plainly — affordability tracks adoption but adds no explanatory power beyond income in this sample.

---

## 1. The token as an economic unit

The token is the atomic unit of large-language-model cost. Providers bill per input token and per output token, and every downstream price — an API call, an agentic workflow, a month of automated drafting — is ultimately a token count multiplied by a per-token rate. That rate is quoted in USD and does not vary by the buyer's country: OpenAI's list price for a model is the same whether the request originates in Lisbon or Luanda.

The problem is that a token is not a unit of *meaning*. Tokenizers are trained predominantly on English-heavy corpora, so they encode English efficiently and fragment other languages into more sub-word pieces to express the same content. The standard measure of this is **fertility**: the number of tokens a tokenizer emits per unit of meaning, benchmarked against a reference language. When English has fertility 1.000 by construction and Amharic has fertility 7.59 under some tokenizers, a speaker conveying the identical sentence pays up to roughly seven and a half times as many tokens — and therefore up to roughly seven and a half times the price — for the same thought.

This converts a flat per-token price into an unequal per-meaning price. The inequality is not a quirk of any single model; it is structural, and it falls hardest on exactly the languages that are already lower-resourced. It compounds with two further disadvantages that have nothing to do with the model itself: speakers of these languages often earn lower wages, and they frequently transact in currencies that buy fewer dollars. A flat global token price, a language that tokenizes expensively, and a low local wage stack multiplicatively. Measuring only the first of these — cost — understates the burden. The economically meaningful quantity is *affordability*: how much of a person's labor time a fixed amount of machine cognition costs. That is the quantity this project constructs and studies.

## 2. Prior art

**Anchor being extended — "The African Language Tax" (arXiv:2606.24460, 2026).** This is the paper we build directly on. It establishes the African tokenizer tax as a cost phenomenon and, crucially, does not stop at token counts: it carries the tax through **FX conversion (§6.3)** and shows how the penalty **compounds with exchange rates (§6.6)**, and it gestures at a labor interpretation with a **one-line wage equivalence (§10.1)** — framing the aggregate cost as on the order of "1,340 annual minimum-wage salaries." We take that single line seriously and develop it into a systematic instrument. What the anchor paper deliberately does *not* do scopes our contribution precisely: it does not build a constructed, multi-country affordability index; it does not link the tax to any adoption or usage data; and it does not cover Portuguese or Spanish. We extend it on exactly those three axes.

**Petrov et al. 2023 (arXiv:2305.15425).** The foundational cross-language tokenizer-tax result: languages differ systematically in tokens-per-text, imposing a cost and context-window penalty. This is the disparity our fertility measurements re-establish on a fresh corpus and tokenizer set.

**Token price indices consumed, not invented.** Silicon Data's SDLLMTK, BenchLM, inferencepriceindex.com, and Epoch AI all track token-price signals over time. We consume live prices in that spirit; we do not claim to have created a token price index. Our contribution sits downstream of price, in the fertility × wage combination.

**Stanford AI Index.** Its quality-adjusted "cost of intelligence" deflation is the method lineage for treating machine cognition as a deflating, quality-adjusted quantity rather than a fixed good.

**UBS Prices & Earnings / the Big Mac "minutes of work" tradition.** This is the lineage for our affordability construction — expressing a good's price as minutes of local labor. We borrow the *affordability* method only; we explicitly reject the currency-valuation inference that those indices license (see Caveat C1).

**Anthropic Economic Index — McCrory et al. 2025 (arXiv:2511.15080).** The source of our adoption outcome: country-level model usage derived from real traffic. **Clio (arXiv:2412.13678)** is the prior privacy-preserving usage-analysis method underpinning that class of measurement.

What is new here is therefore not a new measurement paradigm but an extension of an existing one: a constructed cross-country affordability index, two reusable instruments built from it, a first link to adoption data, and Lusophone/Hispanophone coverage. Each of these novelty claims is held as **[INFERENCE until the final prior-art check]** — provisional until a last pass confirms none has already been published.

## 3. The four instruments

All four instruments are family-stratified: every quantity carries a tokenizer-`family` argument, because there is no universal "token" (Caveat C3). Let `fertility` be the meaning-adjusted tokens-per-sentence ratio relative to English (English ≡ 1.000), and let `p_blend` be the blended USD price per million tokens.

**Blended price.** Providers price input and output tokens differently, so we collapse them:

```
p_blend = (1·input + r·output) / (1 + r)
```

with `r` the assumed output-to-input token ratio. **[INFERENCE]** We set `r = 3` as an assumption, not a measured usage figure, and sweep it in sensitivity analysis (Caveat C2). For the o200k anchor model (OpenAI gpt-4o at $2.5/M input, $10/M output), `p_blend = (2.5 + 3·10)/4 = $8.125/M`.

**3.1 — `e_real` (real tokens per dollar).** The real intelligence exchange rate: how many English-equivalent tokens ("Etok") one USD buys in a given language, after paying the fertility penalty:

```
e_real = (1e6 / p_blend) / fertility        [Etok per USD]
```

Dividing by fertility is the key move: a language that needs twice as many tokens per meaning gets half as much real cognition per dollar.

**3.2 — Intelligence Wage (`IW`).** The real cognition an hour of local labor buys:

```
IW = e_real · hourly_wage                    [Etok per hour of work]
```

`IW` places the token price and the local wage on the same axis: it is high where cognition is cheap and wages are high, and low where cognition is expensive (high fertility) and wages are low.

**3.3 — Work-minutes affordability index.** The inverse-facing, headline instrument: minutes of local work to afford a standard monthly bundle:

```
work_minutes = (bundle · fertility · p_blend / 1e6) / wage · 60
```

with `bundle = 1M English-equivalent tokens/month`. **[INFERENCE]** The 1M-token bundle is an arbitrary yardstick chosen for legibility; `work_minutes` is exactly linear in `bundle` (unit-tested), so a reader who prefers a different monthly budget can rescale linearly without re-running anything.

**3.4 — Language Tax (surcharge).** The multiplicative premium a language pays over English:

```
surcharge = fertility − 1
```

reported as a percentage. It is the cleanest single expression of the tokenizer penalty, independent of wages or prices.

## 4. Data & method

Every input is live-pulled and date-stamped, and the pipeline is built to be reproducible end-to-end.

**Fertility (FLORES-200).** We measure fertility on the FLORES-200 devtest split — 1,012 sentences aligned across languages — over **28 languages × 6 tokenizer families**: OpenAI o200k, OpenAI cl100k, Llama 3, Qwen 2.5, Gemma 2, and Aya. For each language–family pair we compute tokens per sentence relative to English on the aligned sentences and attach **paired sentence-level bootstrap 95% confidence intervals** (seed 0). English is fixed to 1.000 by construction, and the identity check (English-vs-English fertility = 1.000) passes, confirming the alignment and ratio logic.

**Prices (OpenRouter, live).** Per-token prices were retrieved live from OpenRouter on **2026-07-06**. For each tokenizer family we use a representative anchor flagship model; for o200k that anchor is OpenAI gpt-4o at $2.5/M input and $10/M output. Prices are blended via `p_blend` with `r = 3` (swept in sensitivity).

**Wages (two independent bases, both reported).** We deliberately report two wage bases and treat neither as "the" answer:

- **World Bank Tier-2** — GNI per capita divided by 2,080 annual hours, available for all 40 countries in market and PPP terms.
- **ILOSTAT Tier-1** — actual mean employee earnings in market US$, available for 38 of 40 countries.

The two bases diverge most for the poorest countries: ILOSTAT mean earnings run higher than the GNI/2080h proxy at the low end, so affordability looks worse (more work-minutes) under ILOSTAT there. Because the wage-basis choice materially changes the headline for exactly the countries the study is about, we show both and let the reader see the spread rather than picking one.

**Adoption outcome (Anthropic Economic Index).** The adoption measure is the country-level `usage_per_capita_index` from the September 2025 Anthropic Economic Index release. After matching to countries with fertility, price, and wage data, the analysis panel is **N = 23 countries**.

Figures referenced below — `fig_fertility_heatmap`, `fig_language_tax`, `fig_work_minutes`, `fig_wage_basis_comparison`, and `fig_adoption_scatter` — are generated from these inputs.

## 5. Results

### 5.1 Fertility and the tokenizer lottery

The fertility measurements (`fig_fertility_heatmap`) reproduce and sharpen the known cross-language disparity. Relative to English at 1.000, the penalty rises steeply for lower-resourced languages, and — the striking part — it depends heavily on *which tokenizer* a user is routed to. We call this the **tokenizer lottery**: the same meaning, in the same language, costs a wildly different number of tokens depending on the model family behind the endpoint.

Amharic is the extreme case. Its fertility ranges from **1.71× under Aya** (a tokenizer with strong multilingual coverage) to **7.59× under Llama 3 and OpenAI cl100k** — roughly a fourfold spread for identical content, driven entirely by tokenizer design. A user has essentially no visibility into, and often no control over, which tokenizer processes their request, yet it can quadruple their bill.

Expressed as the **Language Tax** (`surcharge = fertility − 1`) under the o200k anchor (`fig_language_tax`), the penalties over English are: Amharic **+478%**, Yoruba **+117%**, Zulu **+72%**, Hindi **+57%**, Hausa **+55%**, Swahili **+49%**, and — importantly for the Lusophone focus — Portuguese **+22%** (fertility ≈ 1.22× under o200k). Portuguese is far from the worst case, but a 22% structural surcharge on every token, before any wage or FX effect, is not negligible for a language with hundreds of millions of speakers across three continents.

### 5.2 The affordability headline, under both wage bases

Fertility alone understates the burden. The `work_minutes` instrument (`fig_work_minutes`) folds in the local wage, and the result is a far larger spread than fertility could produce on its own. Under the o200k anchor and **World Bank Tier-2 PPP wages**, the minutes of local work required for 1M English-equivalent tokens per month are:

| Country (language) | Work-minutes / month |
|---|---:|
| United States (English) | ≈ 11 |
| Portugal (Portuguese) | ≈ 24 |
| Mexico (Spanish) | ≈ 53 |
| Egypt (Arabic) | ≈ 72 |
| South Africa (Zulu) | ≈ 112 |
| Kenya (Swahili) | ≈ 218 |
| Nigeria (Yoruba) | ≈ 238 |
| Ethiopia (Amharic) | ≈ 1,620 |

Ethiopia-on-Amharic costs roughly **140× more work-minutes** than the United States-on-English for the identical bundle of cognition. Only a fraction of that gap is fertility; most of it is the multiplicative stacking of a high tokenizer tax onto a low wage. This is the sense in which affordability, not cost, is the economically load-bearing quantity.

The wage-basis choice matters most exactly here, at the bottom of the table (`fig_wage_basis_comparison`). Under **ILOSTAT Tier-1** actual mean earnings, the poorest countries look worse still: Ethiopia rises to ≈ **5,090** work-minutes and Nigeria to ≈ **2,533**, while Portugal moves the other way to ≈ **81** minutes. We report both bases side by side and claim neither as definitive. The honest summary is that the direction of the finding — a very large, income-driven affordability gradient — is robust to the wage basis, while the *magnitude* for the poorest countries is basis-dependent by a factor of a few.

### 5.3 The Lusophone/Hispanophone cut

Extending beyond African languages to Portuguese and Spanish is one of the study's contributions **[INFERENCE until final prior-art check]**. The Lusophone cut is instructive precisely because Portuguese is a moderate-tax language (+22% under o200k) spoken across very different wage regimes — Portugal, Brazil, Angola, Mozambique. The same +22% tokenizer surcharge translates into very different affordability outcomes depending on the local wage: Portugal at ≈ 24 PPP work-minutes sits an order of magnitude below the Sub-Saharan Lusophone economies. The tokenizer tax is shared across the language community, but the affordability burden is not — it is redistributed by wage and FX. This is the mechanism the affordability framing is designed to make visible, and it is invisible to a cost-only account. (FLORES `por_Latn` does not distinguish European from Brazilian or Angolan Portuguese; that variant ambiguity is a limitation on the fertility component, noted in §9.)

## 6. Adoption analysis

The load-bearing extension is to ask whether affordability tracks real-world adoption. It was **pre-registered before the outcome data were merged** — the git history proves the ordering — so the specification below was fixed in advance rather than chosen after seeing the result.

**Fixed correlational framing (stated up front, not buried):** this is *association, not causation*. Affordability is collinear with development; we report whether the Language Tax adds explanatory power beyond income, not whether it causes non-adoption.

**Outcome:** the Anthropic Economic Index (Sept 2025) country-level `usage_per_capita_index`. **Panel:** N = 23 countries. **Primary specification:**

```
log(AEI) ~ log(work_minutes) + log(GDP_pc_PPP) + internet_pct,   OLS, HC3 errors
```

**Result.** The raw association is strong and highly significant: **Spearman ρ(work_minutes, adoption) = −0.85 (p < 0.0001)** — countries where a bundle of cognition costs more local labor use these models much less per capita (`fig_adoption_scatter`). But in the OLS with a GDP-per-capita-PPP control, the coefficient on `log(work_minutes)` **collapses to approximately zero (p ≈ 0.92)**. Affordability is so tightly collinear with national income that, once income is in the model, affordability adds essentially no independent explanatory power.

This is exactly the **pre-registered "informative null,"** now well-powered at N = 23. It is not a failed result; it is a clean one. To calibrate the spread the outcome captures: the AEI usage index is 3.62 for the United States, 2.01 for Portugal, and 0.046 for Angola (near the bottom of roughly 194 countries) — a spread of nearly two orders of magnitude that our affordability index ranks well but does not explain independently of income.

**What we may and may not conclude.** We may say: affordability and adoption move together strongly, and the affordability index is a good *ranking* proxy for who adopts. We may **not** say: the Language Tax *causes* non-adoption, or that lowering the tax would raise adoption, because in this sample affordability is statistically indistinguishable from income as a predictor. Disentangling the two would require exogenous variation in the tax (e.g., a tokenizer change holding income fixed) that this observational panel does not contain.

## 7. Robustness

**UDHR genre cross-check.** Fertility is measured on FLORES, a written, formal register. To bound register sensitivity we recompute fertility on a second corpus — the Universal Declaration of Human Rights, a distinct legal-prose genre. For the languages central to the Lusophone/Hispanophone focus, fertility is **genre-stable**: Portuguese, Spanish, and French differ by less than 7% relative to their FLORES values. Several other languages are strongly genre-sensitive, however — Vietnamese +136%, Yoruba +59%, and Hausa +44% on UDHR versus FLORES. The tax is therefore largely genre-robust *for the languages we most rely on*, but not universally, and we do not claim genre-invariance where the data contradict it. (This is a partial probe of the formal-vs-chat gap, not a resolution of it — see Caveat C6.)

**Sensitivity battery.** All headline numbers are reported with their range across modelling choices in `reports/sensitivity.md`. We sweep the blend ratio `r ∈ {1, 3, 9}`, all three wage bases (market, PPP, ILOSTAT), input-only and output-only pricing, and per-family anchors. The affordability ranking is stable across the `r` sweep; input-only vs output-only pricing scales every country by a constant factor (4.00×), so it shifts levels without changing rankings. The large affordability gap is not an artifact of any single modelling choice.

**Per-family reporting.** Because there is no universal token (C3), the per-family spread is reported explicitly rather than pooled. That spread bundles two distinct effects — the family's tokenizer fertility *and* its representative anchor model's live price — so a large per-family range reflects the *deployment* reality of which model-plus-tokenizer a user is routed to, not fertility alone. A fertility-only version of the lottery is reported separately so the two effects are never conflated.

## 8. Caveats

Four caveats are load-bearing enough to restate here; all seven are in `docs/caveats.md` as binding commitments, not disclaimers.

**C1 — Law of One Price: affordability, not currency valuation.** LLM tokens sell at a single global USD price, so there is no cross-country price dispersion in the good itself. The Big-Mac/UBS "the currency is over- or under-valued" inference is therefore **invalid** here — those indices work because the same good carries different local prices, which tokens do not. What varies is the buyer's ability to pay (wage) and the quantity of tokens their language needs (fertility). We measure **affordability only** and make no claim about exchange-rate misalignment.

**C2 — The `r` assumption.** The blended price uses an assumed output-to-input ratio `r = 3`. **[INFERENCE]** This is our assumption, not a measured usage figure; it is swept in sensitivity, and any result whose sign or ranking depended on `r` would be flagged. None of the headline rankings do.

**C3 — Per-family: there is no "the" token.** Fertility is a property of a specific tokenizer. Every instrument carries a `family` argument, and cross-family comparisons are made only like-for-like. Any claim of the form "language X costs Y tokens" is incomplete without naming the family.

**C7 — Output-fertility assumption.** Fertility is measured on parallel input/reference text, but the blended price effectively applies that same per-language fertility to output tokens as well. **[INFERENCE — future work]** Model outputs may carry a different length/fertility profile per language; we have not validated this, and disclose it as a known limitation rather than an established property of the index.

## 9. Limitations

Beyond the caveats, four limitations bound the strength of the claims.

**Sample size and power.** The adoption panel is N = 23 countries. Even with a strong raw correlation, 23 observations is a small sample for separating two collinear regressors, and the informative null should be read as "affordability does not beat income *in this sample*," not as a definitive statement about the population of all countries.

**Collinearity with income.** As reported, affordability and GDP per capita are so tightly related that the primary specification cannot attribute adoption to one over the other. This is a structural feature of observational data, not a fixable modelling choice; it is precisely why we refuse a causal reading.

**FLORES `por_Latn` variant ambiguity.** FLORES provides a single `por_Latn` Portuguese that does not distinguish European, Brazilian, and Angolan variants. The Lusophone fertility component is therefore measured on an undifferentiated Portuguese, and variant-level fertility claims are correspondingly weaker than the cross-language ones.

**Wage-tier crudeness.** Both wage bases are national aggregates — a GNI-derived hourly proxy and a mean-earnings figure. Neither captures within-country inequality, the informal sector, or the specific sub-populations most likely to use these tools. The wage-basis divergence at the bottom of the table (§5.2) is itself evidence that the wage input is the least settled part of the pipeline.

## 10. Policy and economics closing

Strip the machinery away and the question is simple: *whose wages buy how much cognition?* A flat global token price is quietly regressive. It charges the same dollars-per-token to everyone, but because lower-resourced languages tokenize more expensively and are spoken disproportionately in lower-wage economies, the real price of a unit of machine thought — measured in a person's own labor time — varies by more than two orders of magnitude. Our headline puts a number on it: the same monthly bundle of cognition that costs an American worker roughly 11 minutes costs an Ethiopian working in Amharic roughly 1,620 minutes, about 140× more.

This connects to both halves of the Fellows framing. On the **AI safety** side, the relevant question is *who gets access to safe, capable frontier models at all*. If the affordability of frontier cognition is stratified this steeply, then the populations facing the highest tax are also the ones most likely to fall back on cheaper, less-aligned, or unmonitored alternatives — a distributional safety problem, not only an equity one. On the **economics** side, the study speaks to diffusion and adoption: the affordability index ranks adoption almost perfectly (ρ = −0.85), which makes it a useful descriptive instrument for *who is adopting*, even though — and this is the disciplined conclusion — it cannot, in this sample, be separated from income as an explanation of *why*.

For the Lusophone/Hispanophone markets specifically, the affordability lens reframes the opportunity. Portuguese carries a moderate +22% tokenizer tax that is shared across Portugal, Brazil, Angola, and Mozambique — but the affordability burden is redistributed by wage and FX so that the same surcharge is nearly free in Lisbon and heavy in Luanda. A tokenizer improvement that halved the Portuguese tax would deliver its largest *affordability* gains precisely to the lowest-wage speakers, even though every speaker pays the same per-token price. That is a lever policymakers and model builders can actually pull, and it is visible only once cost is converted into affordability.

We close on the correlational discipline that governs the whole writeup: affordability is one lever among several — payment rails, subscription access, language coverage, and local wages all move adoption too. What we have shown is that the Language Tax, carried through to affordability, tracks adoption tightly and stratifies access severely. What we have *not* shown, and are careful not to claim, is that it causes non-adoption. The contribution is to have extended a cost measurement into an affordability measurement, linked it to real adoption data, and reported the null as honestly as the headline.
