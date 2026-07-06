# Fertility report (FLORES-200 devtest)

Generated: 2026-07-06T00:57:32Z  |  bootstrap resamples: 10000, seed 0

Fertility = corpus-total tokens in language L / corpus-total tokens in English,
per tokenizer family. English is 1.000 by construction. 95% CI from a paired
sentence-level bootstrap. Source: Muennighoff/flores200 (CC-BY-SA-4.0).

## Fertility by language x family

| language | aya | gemma | llama3 | openai_cl100k | openai_o200k | qwen2 |
|---|---|---|---|---|---|---|
| English | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| Chinese (Simp.) | 0.906 | 1.077 | 1.281 | 1.869 | 1.249 | 1.003 |
| Portuguese | 1.287 | 1.228 | 1.472 | 1.476 | 1.222 | 1.450 |
| Spanish | 1.309 | 1.264 | 1.540 | 1.543 | 1.316 | 1.521 |
| French | 1.402 | 1.361 | 1.600 | 1.606 | 1.368 | 1.580 |
| Swahili | 1.243 | 1.612 | 1.931 | 1.954 | 1.486 | 1.936 |
| Arabic | 1.342 | 1.496 | 1.653 | 3.027 | 1.381 | 1.628 |
| Hausa | 1.355 | 1.727 | 1.972 | 1.994 | 1.550 | 1.944 |
| Zulu | 1.400 | 2.023 | 2.187 | 2.213 | 1.721 | 2.188 |
| Yoruba | 2.055 | 2.451 | 2.722 | 2.952 | 2.167 | 2.687 |
| Hindi | 1.583 | 1.863 | 2.522 | 4.759 | 1.573 | 4.415 |
| Amharic | 1.706 | 3.146 | 7.586 | 7.593 | 5.779 | 4.045 |

## Language Tax (surcharge = fertility − 1), o200k family

| language | fertility [95% CI] | surcharge |
|---|---|---|
| English | 1.000 [1.000, 1.000] | +0% |
| Portuguese | 1.222 [1.213, 1.232] | +22% |
| Chinese (Simp.) | 1.249 [1.233, 1.264] | +25% |
| Spanish | 1.316 [1.304, 1.329] | +32% |
| French | 1.368 [1.355, 1.381] | +37% |
| Arabic | 1.381 [1.367, 1.395] | +38% |
| Swahili | 1.486 [1.472, 1.499] | +49% |
| Hausa | 1.550 [1.534, 1.566] | +55% |
| Hindi | 1.573 [1.558, 1.589] | +57% |
| Zulu | 1.721 [1.703, 1.738] | +72% |
| Yoruba | 2.167 [2.129, 2.206] | +117% |
| Amharic | 5.779 [5.711, 5.847] | +478% |

## Sanity checks

- IDENTITY OK: English fertility == 1.000 for every family.
- ORDER OK (aya): French 1.40 < Amharic 1.71
- ORDER OK (gemma): French 1.36 < Amharic 3.15
- ORDER OK (llama3): French 1.60 < Amharic 7.59
- ORDER OK (openai_cl100k): French 1.61 < Amharic 7.59
- ORDER OK (openai_o200k): French 1.37 < Amharic 5.78
- ORDER OK (qwen2): French 1.58 < Amharic 4.05

All configured language × family cells populated.
