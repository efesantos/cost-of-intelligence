# Sensitivity battery (Task B-9)

Every headline `work_minutes` number with its range across modelling choices.
Bundle = 1M English-equivalent tokens/month. Family = o200k unless noted.

## (1)+(2) r ratio x wage basis (o200k)

| country | r=1,mkt | r=1,ppp | r=3,mkt | r=3,ppp | r=9,mkt | r=9,ppp |
|---|---|---|---|---|---|---|
| USA | 9 | 9 | 11 | 11 | 13 | 13 |
| PRT | 32 | 18 | 41 | 24 | 47 | 27 |
| BRA | — | — | — | — | — | — |
| AGO | — | — | — | — | — | — |
| MOZ | — | — | — | — | — | — |
| KEN | 527 | 168 | 685 | 218 | 780 | 248 |
| NGA | 1066 | 157 | 1386 | 204 | 1578 | 232 |
| ETH | 4061 | 1245 | 5279 | 1619 | 6010 | 1843 |

## (3) per-family spread (r=3, PPP work_minutes)

> Note: this spread bundles TWO effects — the family's tokenizer fertility AND its
> representative anchor model's price (e_real = (1e6/p_blend)/fertility uses that
> family's live model price). So a large spread is the *deployment* reality (which
> model+tokenizer you are routed to), not fertility alone. A fertility-only lottery
> is in reports/fertility_report.md.

| country | min | max | min family | max family | max/min |
|---|---|---|---|---|---|
| USA | 0 | 11 | llama3 | aya | 30.66× |
| PRT | 1 | 25 | llama3 | aya | 26.81× |
| KEN | 9 | 218 | llama3 | openai_o200k | 23.59× |
| NGA | 7 | 238 | llama3 | openai_o200k | 33.70× |
| ETH | 54 | 1619 | qwen2 | openai_o200k | 29.76× |

## (4) input-only vs output-only pricing (PPP work_minutes)

| country | input-only | output-only | ratio |
|---|---|---|---|
| USA | 3 | 14 | 4.00× |
| PRT | 7 | 29 | 4.00× |
| KEN | 67 | 268 | 4.00× |
| NGA | 63 | 251 | 4.00× |
| ETH | 498 | 1992 | 4.00× |

## Not yet swept (flagged)
- FLORES+ vs UDHR fertility genre check (needs UDHR corpus ingest).
- Wage-tier swaps (Tier 1 ILOSTAT / Tier 3 minimum wage) — only World Bank Tier-2
  is populated in this run; the pipeline supports the column when tiers are added.
