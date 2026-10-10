# Adoption analysis results (Task B-7)

> **association, not causation; affordability is collinear with development — we report
> whether the tax adds explanatory power beyond income, not whether it causes non-adoption.**

Panel N = 23 countries. Outcome = log(AEI usage_per_capita_index). Primary regressor = log(work_minutes) (o200k family, PPP wage). Controls = log(GDP per capita PPP), internet penetration %. HC3 robust SEs.

Countries with instruments but no usable AEI value (excluded on missing data, as the plan requires): CHN, ETH, IRN, RUS. The AEI file has 201 geographies, 166 with a positive usage index.

## Primary OLS
```
                            OLS Regression Results                            
==============================================================================
Dep. Variable:                      y   R-squared:                       0.763
Model:                            OLS   Adj. R-squared:                  0.725
Method:                 Least Squares   F-statistic:                     22.94
Date:                                   Prob (F-statistic):           1.56e-06
Time:                                   Log-Likelihood:                -13.982
No. Observations:                  23   AIC:                             35.96
Df Residuals:                      19   BIC:                             40.51
Df Model:                           3                                         
Covariance Type:                  HC3                                         
====================================================================================
                       coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------------
const              -10.1248      6.987     -1.449      0.147     -23.820       3.570
log_work_minutes    -0.0505      0.476     -0.106      0.916      -0.984       0.883
log_gdp_ppp          0.9804      0.554      1.769      0.077      -0.106       2.067
internet_pct         0.0008      0.021      0.037      0.970      -0.041       0.043
==============================================================================
Omnibus:                        0.007   Durbin-Watson:                   2.389
Prob(Omnibus):                  0.996   Jarque-Bera (JB):                0.154
Skew:                           0.036   Prob(JB):                        0.926
Kurtosis:                       2.606   Cond. No.                     8.42e+03
==============================================================================

Notes:
[1] Standard Errors are heteroscedasticity robust (HC3)
[2] The condition number is large, 8.42e+03. This might indicate that there are
strong multicollinearity or other numerical problems.
```

Variance inflation factors: log_work_minutes = 28.8, log_gdp_ppp = 36.6, internet_pct = 4.2. Correlation of log(work_minutes) with log(GDP per capita PPP) = -0.981.

## Secondary: Spearman(work_minutes, adoption) = -0.851 (p = 0.0000)

Partial rank association after residualising both on the controls: rho = -0.054 (p = 0.805).

## Pre-registered robustness checks (plan section 5)

Checks 2 and 3 were run on 2026-10-10, after the primary result was known. They are
the checks the plan specified, unchanged; check 1 was not run (no EF EPI data).

| check | specification | N | coef on log(work_minutes) | HC3 SE | p |
|---|---|---|---|---|---|
| primary | o200k, WB PPP wage, primary mapping | 23 | -0.051 | 0.476 | 0.916 |
| 2. wage-tier swap | WB market-rate wage (GNI Atlas / 2080 h) | 23 | -0.441 | 0.346 | 0.203 |
| 2. wage-tier swap | ILOSTAT mean employee earnings (US$) | 23 | -0.524 | 0.224 | 0.019 |
| 3. alternate mapping | primary + alternate countries, ppp wage | 36 | -0.369 | 0.520 | 0.478 |
| 3. alternate mapping | primary + alternate countries, market wage | 36 | -0.461 | 0.243 | 0.058 |
| 3. alternate mapping | primary + alternate countries, ilo wage | 35 | -0.289 | 0.165 | 0.080 |

Additional check named in this script (not in the plan): tokenizer-family swap, PPP wage, primary mapping.

| family | N | coef | HC3 SE | p |
|---|---|---|---|---|
| llama3 | 23 | -0.736 | 0.432 | 0.088 |
| qwen2 | 23 | -0.296 | 0.347 | 0.395 |
| gemma | 23 | -0.387 | 0.578 | 0.503 |
| aya | 23 | -0.545 | 0.437 | 0.213 |

## Leave-one-country-out influence (check 4, primary coefficient)

- base log(work_minutes) coef: -0.0505
- range on omission: -0.1936 to 0.2728
- any sign flip on omission: True

| dropped | coef | sign flip |
|---|---|---|
| USA | 0.2728 | True |
| PRT | 0.0321 | True |
| MEX | -0.1549 | False |
| FRA | -0.0474 | False |
| KEN | -0.0517 | False |
| NGA | -0.0074 | False |
| ZAF | -0.0622 | False |
| EGY | -0.1727 | False |
| IND | -0.0628 | False |
| IDN | -0.1936 | False |
| VNM | 0.0382 | True |
| THA | -0.1869 | False |
| TUR | -0.0154 | False |
| DEU | -0.0900 | False |
| ITA | -0.0217 | False |
| POL | -0.0722 | False |
| JPN | -0.0780 | False |
| KOR | -0.0246 | False |
| BGD | 0.0069 | True |
| PHL | 0.0316 | True |
| UKR | -0.1820 | False |
| ROU | 0.0359 | True |
| GRC | -0.0682 | False |

## Exploratory decomposition (NOT pre-registered)

Within one tokenizer family, log(work_minutes) = log(fertility) - log(wage) + constant.
Fitting the two terms separately (same controls, HC3) shows which one carries any
association. Read as description only.

| wage basis | log(fertility) coef (p) | log(wage) coef (p) | log(GDP pc PPP) coef (p) |
|---|---|---|---|
| ppp | 0.143 (0.786) | 2.309 (0.199) | -1.228 (0.497) |
| market | 0.295 (0.584) | 0.658 (0.083) | 0.006 (0.992) |
| ilo | -0.217 (0.669) | 0.530 (0.018) | 0.178 (0.626) |

[INFERENCE] With small N the estimates are imprecise, and affordability is strongly
collinear with income (see the VIFs above). Read each coefficient as 'does this term add
explanatory power beyond income in this sample', not as an effect.
