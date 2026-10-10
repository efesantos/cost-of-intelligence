# Sensitivity battery (Task B-9)

Every headline `work_minutes` number with its range across modelling choices.
Bundle = 1M English-equivalent tokens/month. Family = o200k unless noted.

## (1)+(2) r ratio x wage basis (o200k)

| country | r=1,mkt | r=1,ppp | r=3,mkt | r=3,ppp | r=9,mkt | r=9,ppp |
|---|---|---|---|---|---|---|
| USA (eng) | 9 | 9 | 11 | 11 | 13 | 13 |
| PRT (por) | 32 | 18 | 41 | 24 | 47 | 27 |
| BRA (por) | 90 | 42 | 117 | 55 | 134 | 62 |
| AGO (por) | 333 | 97 | 433 | 126 | 493 | 143 |
| MOZ (por) | 1673 | 619 | 2175 | 805 | 2476 | 916 |
| KEN (swh) | 527 | 168 | 685 | 218 | 780 | 248 |
| NGA (hau) | 889 | 131 | 1156 | 170 | 1316 | 194 |
| NGA (yor) | 1243 | 183 | 1616 | 238 | 1840 | 271 |
| ETH (amh) | 4061 | 1245 | 5279 | 1619 | 6010 | 1843 |

## (3) per-family spread (r=3, PPP work_minutes)

> Note: this spread bundles TWO effects — the family's tokenizer fertility AND its
> representative anchor model's price (e_real = (1e6/p_blend)/fertility uses that
> family's live model price). So a large spread is the *deployment* reality (which
> model+tokenizer you are routed to), not fertility alone. A fertility-only lottery
> is in reports/fertility_report.md.

| country | min | max | min family | max family | max/min |
|---|---|---|---|---|---|
| USA (eng) | 1 | 11 | qwen2 | aya | 20.83× |
| PRT (por) | 1 | 25 | qwen2 | aya | 18.50× |
| BRA (por) | 3 | 58 | qwen2 | aya | 18.50× |
| AGO (por) | 7 | 133 | qwen2 | aya | 18.50× |
| MOZ (por) | 46 | 848 | qwen2 | aya | 18.50× |
| KEN (swh) | 14 | 218 | qwen2 | openai_o200k | 15.98× |
| NGA (hau) | 10 | 170 | qwen2 | openai_o200k | 16.61× |
| NGA (yor) | 14 | 238 | qwen2 | openai_o200k | 16.80× |
| ETH (amh) | 54 | 1619 | qwen2 | openai_o200k | 29.76× |

## (4) input-only vs output-only pricing (PPP work_minutes)

| country | input-only | output-only | ratio |
|---|---|---|---|
| USA (eng) | 3 | 14 | 4.00× |
| PRT (por) | 7 | 29 | 4.00× |
| BRA (por) | 17 | 67 | 4.00× |
| AGO (por) | 39 | 155 | 4.00× |
| MOZ (por) | 248 | 991 | 4.00× |
| KEN (swh) | 67 | 268 | 4.00× |
| NGA (hau) | 52 | 210 | 4.00× |
| NGA (yor) | 73 | 293 | 4.00× |
| ETH (amh) | 498 | 1992 | 4.00× |

## (5) three wage bases side by side (o200k, r=3)

> World Bank Tier-2 is GNI per capita / 2080 h, in market US$ (Atlas) or PPP int$;
> ILOSTAT Tier-1 is mean monthly employee earnings in US$ / (40 h x 4.333 weeks).
> Token prices are one global US$ price (caveat C1), so the market-rate columns are
> the like-for-like basis; PPP divides a US$ price by a PPP wage.

| country | WB market | WB PPP | ILOSTAT | market/PPP |
|---|---|---|---|---|
| USA (eng) | 11 | 11 | 13 | 1.01× |
| PRT (por) | 41 | 24 | 81 | 1.75× |
| BRA (por) | 117 | 55 | 170 | 2.15× |
| AGO (por) | 433 | 126 | 803 | 3.44× |
| MOZ (por) | 2175 | 805 | 486 | 2.70× |
| KEN (swh) | 685 | 218 | 919 | 3.14× |
| NGA (hau) | 1156 | 170 | 2533 | 6.79× |
| NGA (yor) | 1616 | 238 | 3541 | 6.79× |
| ETH (amh) | 5279 | 1619 | 5089 | 3.26× |

## Other sensitivity axes (separate reports)
- **FLORES vs UDHR fertility** genre check: see `reports/udhr_crosscheck.md`
  (a second, legal-prose corpus). Portuguese/Spanish/French are stable (<7%);
  several languages (e.g. Vietnamese, Yoruba, Hausa) are strongly genre-sensitive.
- **Wage-tier swap in the adoption regression** (pre-registered check 2): see
  `reports/adoption_results.md`. ILOSTAT coverage notes: `reports/ilostat_wages.md`.
