# AEI outcome-variable memo (Task B-6)

Generated: 2026-07-06T01:22:42Z

**Source:** `Anthropic/EconomicIndex`, release `release_2025_09_15`, Claude.ai (Free and Pro),
usage window `2025-08-04_to_2025-08-11`. Ungated. File: `data/output/aei_enriched_claude_ai_2025-08-04_to_2025-08-11.csv`.

## Chosen outcome variable

**`usage_per_capita_index`** at `facet=country`. Per the release's own
`data_documentation.md`: *"Concentration index showing if a geography has more/less
usage than expected based on population share (1.0 = proportional, >1.0 = over-
representation, <1.0 = under-representation)"* — computed as usage share divided by
working-age-population share during the release's enrichment step. It is already
per-capita normalized, so no separate population join is required. This satisfies the
B-6 rule (prefer the release's own per-capita normalized usage measure).

Also retained for robustness/description: `usage_pct` (raw share of global usage) and
`usage_tier` (adoption quartile).

## Coverage: 201 countries with a country-level index.

Top-5 adoption (per-capita index):

| country | usage_per_capita_index |
|---|---|
| Israel | 7.00 |
| Monaco | 4.93 |
| Singapore | 4.57 |
| Australia | 4.10 |
| New Zealand | 4.05 |

Panel countries (the affordability gradient the study links to adoption):

| country | usage_per_capita_index |
|---|---|
| United States | 3.624 |
| Portugal | 2.013 |
| Brazil | 0.926 |
| Kenya | 0.459 |
| South Africa | 0.458 |
| Mexico | 0.400 |
| Egypt | 0.281 |
| India | 0.267 |
| Nigeria | 0.202 |
| Mozambique | 0.095 |
| Angola | 0.046 |

[INFERENCE] The gradient — e.g. Angola near the bottom — is consistent with the
affordability thesis, but B-7 tests it *correlationally* with income controls; this
memo asserts only what the AEI variable measures, not causation.
