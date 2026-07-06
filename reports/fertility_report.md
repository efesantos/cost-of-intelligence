# Fertility report (FLORES-200 devtest)

Generated: 2026-07-06T01:52:04Z  |  bootstrap resamples: 10000, seed 0

Fertility = corpus-total tokens in language L / corpus-total tokens in English,
per tokenizer family. English is 1.000 by construction. 95% CI from a paired
sentence-level bootstrap. Source: Muennighoff/flores200 (CC-BY-SA-4.0).

## Fertility by language x family

| language | aya | gemma | llama3 | openai_cl100k | openai_o200k | qwen2 |
|---|---|---|---|---|---|---|
| English | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| Chinese (Simp.) | 0.906 | 1.077 | 1.281 | 1.869 | 1.249 | 1.003 |
| Indonesian | 1.075 | 1.110 | 1.538 | 1.548 | 1.246 | 1.539 |
| Portuguese | 1.287 | 1.228 | 1.472 | 1.476 | 1.222 | 1.450 |
| German | 1.186 | 1.256 | 1.582 | 1.586 | 1.311 | 1.559 |
| Spanish | 1.309 | 1.264 | 1.540 | 1.543 | 1.316 | 1.521 |
| Turkish | 1.118 | 1.403 | 1.402 | 1.921 | 1.430 | 1.624 |
| French | 1.402 | 1.361 | 1.600 | 1.606 | 1.368 | 1.580 |
| Japanese | 0.903 | 1.182 | 1.511 | 2.266 | 1.658 | 1.403 |
| Italian | 1.341 | 1.347 | 1.638 | 1.641 | 1.469 | 1.626 |
| Korean | 1.270 | 1.640 | 1.488 | 2.367 | 1.472 | 1.630 |
| Russian | 1.254 | 1.379 | 1.616 | 2.462 | 1.421 | 1.755 |
| Polish | 1.304 | 1.463 | 1.891 | 1.914 | 1.638 | 1.765 |
| Vietnamese | 1.952 | 1.374 | 1.392 | 2.444 | 1.490 | 1.435 |
| Romanian | 1.361 | 1.555 | 1.868 | 1.875 | 1.631 | 1.859 |
| Swahili | 1.243 | 1.612 | 1.931 | 1.954 | 1.486 | 1.936 |
| Arabic | 1.342 | 1.496 | 1.653 | 3.027 | 1.381 | 1.628 |
| Hausa | 1.355 | 1.727 | 1.972 | 1.994 | 1.550 | 1.944 |
| Tagalog | 1.456 | 1.789 | 2.026 | 2.050 | 1.683 | 2.033 |
| Persian | 1.336 | 1.452 | 1.522 | 3.256 | 1.530 | 2.577 |
| Zulu | 1.400 | 2.023 | 2.187 | 2.213 | 1.721 | 2.188 |
| Ukrainian | 1.320 | 1.654 | 1.642 | 2.965 | 1.747 | 2.498 |
| Thai | 0.989 | 1.842 | 2.185 | 4.343 | 1.955 | 2.542 |
| Yoruba | 2.055 | 2.451 | 2.722 | 2.952 | 2.167 | 2.687 |
| Hindi | 1.583 | 1.863 | 2.522 | 4.759 | 1.573 | 4.415 |
| Greek | 1.643 | 2.289 | 2.232 | 5.121 | 2.131 | 4.898 |
| Bengali | 1.567 | 2.686 | 5.758 | 5.799 | 1.697 | 5.026 |
| Amharic | 1.706 | 3.146 | 7.586 | 7.593 | 5.779 | 4.045 |

## Language Tax (surcharge = fertility − 1), o200k family

| language | fertility [95% CI] | surcharge |
|---|---|---|
| English | 1.000 [1.000, 1.000] | +0% |
| Portuguese | 1.222 [1.213, 1.232] | +22% |
| Indonesian | 1.246 [1.235, 1.258] | +25% |
| Chinese (Simp.) | 1.249 [1.233, 1.264] | +25% |
| German | 1.311 [1.299, 1.322] | +31% |
| Spanish | 1.316 [1.304, 1.329] | +32% |
| French | 1.368 [1.355, 1.381] | +37% |
| Arabic | 1.381 [1.367, 1.395] | +38% |
| Russian | 1.421 [1.406, 1.436] | +42% |
| Turkish | 1.430 [1.416, 1.445] | +43% |
| Italian | 1.469 [1.455, 1.483] | +47% |
| Korean | 1.472 [1.457, 1.488] | +47% |
| Swahili | 1.486 [1.472, 1.499] | +49% |
| Vietnamese | 1.490 [1.476, 1.504] | +49% |
| Persian | 1.530 [1.514, 1.546] | +53% |
| Hausa | 1.550 [1.534, 1.566] | +55% |
| Hindi | 1.573 [1.558, 1.589] | +57% |
| Romanian | 1.631 [1.616, 1.647] | +63% |
| Polish | 1.638 [1.621, 1.656] | +64% |
| Japanese | 1.658 [1.639, 1.677] | +66% |
| Tagalog | 1.683 [1.666, 1.701] | +68% |
| Bengali | 1.697 [1.679, 1.714] | +70% |
| Zulu | 1.721 [1.703, 1.738] | +72% |
| Ukrainian | 1.747 [1.731, 1.764] | +75% |
| Thai | 1.955 [1.931, 1.979] | +95% |
| Greek | 2.131 [2.109, 2.155] | +113% |
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
