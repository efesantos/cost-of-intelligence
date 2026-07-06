# UDHR fertility cross-check (genre robustness)

Generated: 2026-07-06T02:00:16Z  |  bootstrap resamples: 10000, seed 0

Second-corpus sensitivity check for the language tax. FLORES-200 is parallel
*news* text; the UDHR is human-translated *legal/declarative* prose with a
fixed preamble + 30-article structure, aligned here by (section, paragraph)
unit id. Fertility = corpus-total tokens in L / corpus-total tokens in English,
same tokenlab paired-bootstrap machinery as the FLORES run. A `genre_flag` marks
any language where |UDHR - FLORES| / FLORES > 15% for the o200k family.

Source: Unicode Consortium UDHR-in-XML (github.com/unicode-org/udhr). UDHR text
is public domain (UN). English is 1.000 by construction.

Coverage: 28 languages, 6 tokenizer families. o200k genre flags: 5 / 28.

## UDHR vs FLORES fertility (o200k family)

| language | UDHR fertility [95% CI] | FLORES fertility | rel. diff | genre flag |
|---|---|---|---|---|
| English | 1.000 [1.000, 1.000] | 1.000 | 0.0% |  |
| Chinese (Simp.) | 1.185 [1.097, 1.331] | 1.249 | 5.1% |  |
| Spanish | 1.229 [1.181, 1.274] | 1.316 | 6.6% |  |
| Arabic | 1.233 [1.113, 1.399] | 1.381 | 10.7% |  |
| Portuguese | 1.272 [1.175, 1.438] | 1.222 | 4.1% |  |
| German | 1.339 [1.248, 1.493] | 1.311 | 2.1% |  |
| Korean | 1.369 [1.323, 1.417] | 1.472 | 7.0% |  |
| Swahili | 1.390 [1.319, 1.469] | 1.486 | 6.5% |  |
| French | 1.393 [1.294, 1.562] | 1.368 | 1.9% |  |
| Italian | 1.426 [1.379, 1.471] | 1.469 | 2.9% |  |
| Russian | 1.456 [1.347, 1.633] | 1.421 | 2.4% |  |
| Indonesian | 1.472 [1.416, 1.527] | 1.246 | 18.1% | **YES** |
| Turkish | 1.496 [1.429, 1.569] | 1.430 | 4.6% |  |
| Persian | 1.498 [1.374, 1.682] | 1.530 | 2.1% |  |
| Hindi | 1.560 [1.507, 1.620] | 1.573 | 0.8% |  |
| Bengali | 1.598 [1.419, 1.732] | 1.697 | 5.8% |  |
| Zulu | 1.618 [1.564, 1.671] | 1.721 | 5.9% |  |
| Tagalog | 1.637 [1.461, 1.755] | 1.683 | 2.8% |  |
| Ukrainian | 1.818 [1.692, 2.029] | 1.747 | 4.1% |  |
| Romanian | 1.819 [1.686, 2.041] | 1.631 | 11.5% |  |
| Polish | 1.823 [1.679, 2.066] | 1.638 | 11.3% |  |
| Japanese | 1.901 [1.716, 2.140] | 1.658 | 14.6% |  |
| Thai | 2.078 [1.869, 2.392] | 1.955 | 6.3% |  |
| Hausa | 2.236 [2.033, 2.547] | 1.550 | 44.2% | **YES** |
| Greek | 2.291 [2.117, 2.574] | 2.131 | 7.5% |  |
| Yoruba | 3.436 [3.055, 3.990] | 2.167 | 58.6% | **YES** |
| Vietnamese | 3.513 [3.224, 3.796] | 1.490 | 135.8% | **YES** |
| Amharic | 6.717 [6.432, 6.998] | 5.779 | 16.2% | **YES** |

## Genre-sensitivity flags (o200k)

- **Vietnamese**: UDHR 3.513 vs FLORES 1.490 (135.8% higher on UDHR).
- **Yoruba**: UDHR 3.436 vs FLORES 2.167 (58.6% higher on UDHR).
- **Hausa**: UDHR 2.236 vs FLORES 1.550 (44.2% higher on UDHR).
- **Indonesian**: UDHR 1.472 vs FLORES 1.246 (18.1% higher on UDHR).
- **Amharic**: UDHR 6.717 vs FLORES 5.779 (16.2% higher on UDHR).

## Genre flags per tokenizer family

| family | languages flagged (>15%) |
|---|---|
| openai_o200k | 5 / 28 |
| openai_cl100k | 6 / 28 |
| llama3 | 6 / 28 |
| qwen2 | 5 / 28 |
| gemma | 4 / 28 |
| aya | 5 / 28 |

## Alignment units per language

Shared (section, paragraph) ids kept after intersecting with English.

| language | UDHR file | shared units |
|---|---|---|
| Amharic | udhr_amh.xml | 50 |
| Arabic | udhr_arb.xml | 59 |
| Bengali | udhr_ben.xml | 60 |
| Chinese (Simp.) | udhr_cmn_hans.xml | 58 |
| English | udhr_eng.xml | 60 |
| French | udhr_fra.xml | 59 |
| German | udhr_deu_1996.xml | 59 |
| Greek | udhr_ell_monotonic.xml | 59 |
| Hausa | udhr_hau_NG.xml | 59 |
| Hindi | udhr_hin.xml | 60 |
| Indonesian | udhr_ind.xml | 60 |
| Italian | udhr_ita.xml | 60 |
| Japanese | udhr_jpn.xml | 58 |
| Korean | udhr_kor.xml | 60 |
| Persian | udhr_pes_1.xml | 58 |
| Polish | udhr_pol.xml | 59 |
| Portuguese | udhr_por_PT.xml | 58 |
| Romanian | udhr_ron_2006.xml | 59 |
| Russian | udhr_rus.xml | 59 |
| Spanish | udhr_spa.xml | 60 |
| Swahili | udhr_swh.xml | 60 |
| Tagalog | udhr_tgl.xml | 60 |
| Thai | udhr_tha.xml | 58 |
| Turkish | udhr_tur.xml | 60 |
| Ukrainian | udhr_ukr.xml | 59 |
| Vietnamese | udhr_vie.xml | 60 |
| Yoruba | udhr_yor.xml | 58 |
| Zulu | udhr_zul.xml | 60 |

## Notes / assumptions

- [INFERENCE] Where the UDHR project ships country/orthography variants, the variant matching the FLORES/panel primary country was chosen (European Portuguese, Nigerian Hausa, modern German 1996, Romanian 2006, monotonic Greek). This affects only which single translation is measured.
- [INFERENCE] Titles ("Article 1") are excluded; only declaration prose paragraphs are tokenized, so cross-language label noise cannot inflate the ratio.
- FLORES por_Latn is variant-ambiguous (see docs/flores_variant_note.md); the UDHR row here uses European Portuguese, so a Portuguese genre flag may partly reflect variant, not genre.
