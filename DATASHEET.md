# Datasheet: Cost of Intelligence affordability panel

Structured following *Datasheets for Datasets* (Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daumé III, H., & Crawford, K. (2021). *Communications of the ACM*, 64(12), 86–92).

Every count and date below was read from the committed files on 2026-10-10. Assumptions we made ourselves are tagged `[INFERENCE]`.

---

## Motivation

- **Purpose.** To express the cost of large-language-model (LLM) use in units that mean something to the person paying: minutes of their own work. The panel combines tokenizer fertility (how many tokens a language needs for the same meaning), live per-token prices and national wage data, and links the result to country-level AI adoption. The focus is the Lusophone and Hispanophone Global South, with African and other languages for contrast.
- **Framing.** The panel *extends* "The African Language Tax" (arXiv:2606.24460) from cost to affordability and adoption, and from African languages to Portuguese and Spanish. It does not claim to originate the tokenizer-tax idea (Petrov et al. 2023 established it).
- **Creator and funding.** Elmer Santos. No funding is declared. The build was done with AI assistance (see the README's "Authorship & AI assistance" section).

## Composition

| File | One row is | Rows | Main columns |
|---|---|--:|---|
| `data/fertility.parquet` | a (language, tokenizer family) pair on FLORES-200 | 168 (28 × 6) | `fertility`, `ci_low`, `ci_high`, `n_sentences` (1,012), token totals |
| `data/udhr_fertility.parquet` | the same pair on the UDHR (second genre) | 168 | `fertility`, `flores_fertility`, `rel_diff`, `genre_flag` |
| `data/wages.parquet` | a country (World Bank Tier-2 wage) | 40 | GNI per capita (Atlas US$ and PPP int$), hourly wage at market rate and PPP, `gni_year` |
| `data/ilostat_wages.parquet` | a country (ILOSTAT Tier-1 wage) | 38 | mean monthly employee earnings (US$ and local currency), FX rate, `year`, source survey |
| `data/controls.parquet` | a country (regression controls) | 40 | GDP per capita PPP, internet users (% of population) |
| `data/aei.parquet` | a geography in the Anthropic Economic Index | 201 | `usage_per_capita_index`, `usage_pct`, `usage_tier` |
| `config/prices.yaml` | a (tokenizer family, model tier) price anchor | 10 | model id, input and output US$ per 1M tokens, `retrieved_at` |
| `data/instruments.parquet` | a (language, primary country, family) triple | 140 (28 × 5) | the four instruments under all three wage bases |

- **Languages:** 28 FLORES-200 languages, English as the reference.
- **Tokenizer families:** 6 (OpenAI o200k, OpenAI cl100k, Llama 3, Qwen 2.5, Gemma 2, Aya). Fertility covers all six. Prices, and therefore the instruments, cover five: no cl100k-family model is used as a price anchor.
- **Countries:** 40. Each language has one *primary* country (27 distinct countries) used for the instruments and the adoption regression, plus *alternate* countries (13 more, such as Brazil, Angola and Mozambique for Portuguese) used in sensitivity checks. The mapping is `config/country_language.yaml`.
- **Sample, not census.** Languages were chosen for the Lusophone, Hispanophone and African focus, then widened to give the adoption regression at least 15 countries.
- **Missing data.**
  - ILOSTAT earnings are missing for Iran and Morocco (38 of 40 countries).
  - The Economic Index has no country value for China, Ethiopia, Iran or Russia, so the adoption panel has 23 countries, not 27. Ethiopia, the headline affordability case, is therefore *not* in the adoption regression.
  - 35 of the 201 Economic Index geographies have a usage index of 0 and cannot enter a log regression.
- **Relationships.** Rows link on the FLORES language code, the tokenizer `family` and the ISO 3166 alpha-3 `country` code.
- **Splits.** None. This is a descriptive and analytic panel, not a training resource.
- **Sensitive data.** None. All inputs are national aggregates or public parallel text.

## Sources and tiers

Wage tiers: **Tier-1** is observed earnings data (ILOSTAT). **Tier-2** is a proxy derived from national income (World Bank GNI per capita ÷ 2,080 hours).

| Source | Used for | Access | Licence or terms |
|---|---|---|---|
| FLORES-200 devtest, via the Hugging Face mirror `Muennighoff/flores200` | fertility (1,012 aligned sentences per language) | the canonical `flores_plus` is gated, so the ungated mirror is used | CC BY-SA 4.0 |
| Universal Declaration of Human Rights, Unicode `unicode-org/udhr` XML | second-genre fertility check | `raw.githubusercontent.com/unicode-org/udhr/main/data/udhr/` | no licence file found in the repository; we make no licence claim for these files |
| OpenRouter models API (`https://openrouter.ai/api/v1/models`) | live input and output prices per token | public, no key | OpenRouter terms of service; redistribution of the API responses is not expressly authorised |
| World Bank World Development Indicators API | `NY.GNP.PCAP.CD`, `NY.GNP.PCAP.PP.CD` (Tier-2 wages), `NY.GDP.PCAP.PP.CD`, `IT.NET.USER.ZS` (controls) | public | CC BY 4.0 |
| ILOSTAT SDMX, dataflow `DF_EAR_EMTA_SEX_CUR_NB` | mean monthly earnings of employees in US$ (Tier-1 wages) | public | CC BY 4.0 (the ILO applies it to datasets published on or after 3 May 2023) |
| Anthropic Economic Index, Hugging Face `Anthropic/EconomicIndex`, release `release_2025_09_15` | adoption outcome `usage_per_capita_index` | ungated | data CC BY, code MIT (dataset card) |

## Retrieval dates and vintages

| Source | Retrieved | Data vintage |
|---|---|---|
| OpenRouter prices | **2026-10-10T10:28:15Z** (current); 2026-07-06T01:02:39Z kept for comparison | live list prices on those dates (458 and 340 models listed) |
| World Bank WDI | 2026-07-06 | GNI per capita 2025 (all 40 countries); GDP per capita PPP 2024; internet use 2024 (36) or 2025 (4) |
| ILOSTAT | 2026-07-06T02:05:54Z | latest year per country, 2019 to 2025 (median 2024; Kenya 2019, South Africa 2020, Ethiopia 2021) |
| FLORES-200 | fertility run 2026-07-06T01:52:04Z | FLORES-200 devtest |
| UDHR | 2026-07-06 | `main` branch on that date |
| Economic Index | memo generated 2026-07-06T01:22:42Z | Claude.ai (Free and Pro) usage, one week: 2025-08-04 to 2025-08-11 |

## Preprocessing

- **Fertility.** For each language and family: total tokens over the 1,012 FLORES-200 devtest sentences ÷ total tokens for the aligned English sentences, so English is 1.000 by construction. 95% confidence intervals come from a paired sentence-level bootstrap (10,000 resamples, seed 0). Tokenizers are loaded through the author's `tokenlab` harness (`pip install -e ../tokenlab`, github.com/efesantos/tokenlab), which pins the tokenizer for each family.
- **Prices.** OpenRouter quotes US$ per token; we multiply by 10⁶. One flagship and one small anchor model per family are chosen by the ordered rules in `src/prices.py` (first non-free model whose id matches, exact id preferred). Gemini stands in for the Gemma family's small-tier price and Cohere Command for the Aya family `[INFERENCE]`. The blended price is `p_blend = (input + r·output) / (1 + r)` with `r = 3` `[INFERENCE]`, swept over 1, 3 and 9.
- **Wages.** Tier-2: GNI per capita ÷ 2,080 hours `[INFERENCE]`, in both market terms (Atlas method, current US$) and PPP terms (current international $). Tier-1: ILOSTAT mean monthly earnings of employees in US$ ÷ (40 hours × 4.333 weeks) `[INFERENCE]`.
- **Wage basis and caveat C1.** Tokens sell at one US$ price, so a worker pays at market exchange rates. The market-rate wages are therefore the like-for-like basis for "minutes of work"; dividing a US$ price by a PPP wage understates the burden where local prices are low. All three bases are carried in every instrument row.
- **Raw data kept.** Yes, under `data/raw/` with retrieval timestamps: FLORES sentences, UDHR XML, World Bank and ILOSTAT API responses, and both OpenRouter snapshots. The Economic Index CSV is not committed; `src/aei.py` downloads it from Hugging Face.

## Uses

- **Intended.** Measuring the language tax and what it costs in local work time; comparing affordability across countries, languages and tokenizer families; correlational analysis against adoption (**association, not causation**).
- **To avoid.** Causal claims about adoption. Currency-valuation claims (caveat C1). Any "language X costs Y tokens" claim without naming the tokenizer family (caveat C3). Reading API-price affordability as the cost faced by subscription users (caveat C4).

## Distribution

- **Where.** https://github.com/efesantos/cost-of-intelligence
- **Licences.** Code: MIT. Derived data and figures: CC BY 4.0. Third-party raw files under `data/raw/` are not relicensed and stay under the terms in the Sources table. In particular the FLORES-200 sentences are CC BY-SA 4.0, and the OpenRouter snapshots (`data/raw/prices/`) are kept only so the price anchors can be checked; they are not covered by the CC BY 4.0 data licence.
- **Attribution.** Anyone reusing the derived data should also credit the World Bank, the ILO, the Anthropic Economic Index and FLORES-200 (NLLB Team 2022).

## Maintenance

- **Maintainer.** Elmer Santos, through the repository's GitHub issues.
- **Updates.** Prices are live: `make refresh-prices` takes a new OpenRouter snapshot, saved with its date beside the earlier ones, and `make results` regenerates every derived number, figure and report from the committed data. Each published version of the paper cites a tagged release.

## Known limitations

See `docs/caveats.md` for all seven binding caveats. The ones that matter most for this panel:

- **C1, Law of One Price.** Tokens sell at a single global US$ price, so the panel measures affordability only, never currency valuation. It also means market-rate wages are the like-for-like basis (see Preprocessing).
- **C2, the `r` assumption.** The output-to-input ratio `r = 3` is assumed, not measured; rankings are stable across `r` ∈ {1, 3, 9}.
- **C3, per-family measurement.** Fertility belongs to a tokenizer, not a language. Models sharing a tokenizer family are assumed to share its fertility.
- **C7, output fertility.** The fertility measured on input text is also applied to output tokens. This is unvalidated.
- **FLORES `por_Latn` ambiguity.** FLORES-200 has one Portuguese, so European, Brazilian, Angolan and Mozambican Portuguese share one fertility value. Variant-level fertility is not measured.
- **Wage crudeness.** GNI ÷ 2,080 hours ignores inequality and informal work, and is especially crude for Angola and Mozambique. ILOSTAT covers employees only, so where few workers are formal employees (for example Mozambique) mean earnings can exceed the GNI-based proxy.
- **Mixed vintages.** Prices are from 2026, World Bank wages from 2025 and ILOSTAT earnings from 2019 to 2025, without inflation adjustment.
- **Adoption window and coverage.** The Economic Index outcome is one week of Claude.ai usage, and four panel countries (China, Ethiopia, Iran, Russia) have no value.
