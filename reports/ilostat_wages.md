# ILOSTAT Tier-1 wages (mean monthly earnings -> hourly USD)

Generated: 2026-07-06T02:05:54Z

Tier-1 wage layer: ILOSTAT *average monthly earnings of employees* (SEX total, all economic activities), converted to an hourly USD rate. This is a better alternative to the repo's Tier-2 World Bank GNI/2080 proxy and is written to a SEPARATE artifact (data/ilostat_wages.parquet); data/wages.parquet is untouched.

- Dataflow: `DF_EAR_EMTA_SEX_CUR_NB` (Average monthly earnings of employees by sex and currency).
- Currency: ILOSTAT-published **US$** (CUR_TYPE_USD) preferred; World Bank PA.NUS.FCRF fallback where only local currency is published.
- Hourly = monthly / (4.333 weeks/month x 40 h/week). **[INFERENCE]** 40 h/week is a full-time default (ILOSTAT mean-actual-hours not joined).
- Most recent available year taken per country (range 2019-2025).

Coverage: **38 / 40** target countries have Tier-1 data.

## Tier-1 hourly wages

| country | hourly USD | monthly USD | local/mo | currency | FX (LCU/US$) | year |
|---|---|---|---|---|---|---|
| United States | $36.19 | 6,273 | 6,273 | — | 1.000 | 2025 |
| Austria | $30.74 | 5,328 | 4,923 | — | 0.924 | 2024 |
| Germany | $26.81 | 4,647 | 4,413 | — | 0.950 | 2022 |
| Italy | $20.79 | 3,604 | 3,330 | — | 0.924 | 2024 |
| Spain | $18.98 | 3,290 | 3,040 | — | 0.924 | 2024 |
| United Kingdom | $18.96 | 3,287 | 3,037 | — | 0.924 | 2024 |
| South Korea | $18.28 | 3,168 | 4,091,000 | — | 1,291.447 | 2022 |
| Japan | $16.16 | 2,801 | 307,400 | — | 109.754 | 2021 |
| France | $13.72 | 2,378 | 2,197 | — | 0.924 | 2024 |
| Greece | $12.35 | 2,141 | 1,978 | — | 0.924 | 2024 |
| Poland | $10.51 | 1,821 | 1,683 | — | 0.924 | 2024 |
| Saudi Arabia | $10.38 | 1,799 | 6,748 | — | 3.750 | 2022 |
| Romania | $8.82 | 1,530 | 1,413 | — | 0.924 | 2024 |
| Portugal | $7.31 | 1,268 | 1,171 | — | 0.924 | 2024 |
| Turkey | $4.95 | 859 | 28,173 | — | 32.806 | 2024 |
| China | $4.66 | 807 | 5,436 | — | 6.737 | 2022 |
| Russia | $4.48 | 777 | 57,240 | — | 73.654 | 2021 |
| Brazil | $3.50 | 607 | 3,393 | — | 5.587 | 2025 |
| Mexico | $3.18 | 551 | 10,609 | — | 19.238 | 2025 |
| Thailand | $2.93 | 508 | 16,699 | — | 32.883 | 2025 |
| Colombia | $2.88 | 499 | 2,022,657 | — | 4,053.137 | 2025 |
| South Africa | $2.80 | 485 | 7,980 | — | 16.459 | 2020 |
| Ukraine | $2.65 | 459 | 14,847 | — | 32.342 | 2022 |
| Vietnam | $2.05 | 355 | 8,579,562 | — | 24,164.854 | 2024 |
| Philippines | $1.83 | 316 | 17,605 | — | 55.630 | 2023 |
| Senegal | $1.61 | 279 | 169,276 | — | 606.345 | 2024 |
| India | $1.47 | 255 | 22,220 | — | 87.158 | 2025 |
| Mozambique | $1.23 | 213 | 13,571 | — | 63.851 | 2022 |
| Tanzania | $1.22 | 212 | 549,783 | — | 2,597.900 | 2024 |
| Côte d'Ivoire | $1.19 | 207 | 128,952 | — | 623.760 | 2022 |
| Indonesia | $1.05 | 182 | 2,776,804 | — | 15,236.904 | 2023 |
| Kenya | $0.79 | 137 | 13,933 | — | 101.992 | 2019 |
| Bangladesh | $0.77 | 134 | 15,517 | — | 115.603 | 2024 |
| Angola | $0.74 | 129 | 111,867 | — | 869.844 | 2024 |
| Niger | $0.69 | 120 | 75,079 | — | 623.760 | 2022 |
| Egypt | $0.63 | 109 | 4,954 | — | 45.299 | 2024 |
| Ethiopia | $0.55 | 96 | 4,196 | — | 43.734 | 2021 |
| Nigeria | $0.30 | 52 | 76,489 | — | 1,478.959 | 2024 |

## Coverage

- Tier-1 obtained: 38 countries.
- Missing (no ILOSTAT earnings series): Iran, Morocco.
- All covered countries had an ILOSTAT-published USD value (no World Bank FX fallback needed).

## Notes / assumptions

- [INFERENCE] 40 h/week full-time default drives the hourly conversion; swap for ILOSTAT mean weekly hours actually worked to refine.
- `fx_lcu_per_usd` for USD-published rows is ILOSTAT's implied rate (local monthly / USD monthly), shown for audit; it is not an independent source.
- Most recent year differs by country; earnings are nominal (not deflated).
- Economic-activity aggregate (all activities) and SEX total are used; no industry or sex breakdown is applied.
