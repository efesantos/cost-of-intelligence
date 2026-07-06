# Adoption analysis results (Task B-7)

> **association, not causation; affordability is collinear with development — we report
> whether the tax adds explanatory power beyond income, not whether it causes non-adoption.**

Panel N = 23 countries. Outcome = log(AEI usage_per_capita_index). Primary regressor = log(work_minutes) (o200k family, PPP wage). Controls = log(GDP per capita PPP), internet penetration %. HC3 robust SEs.

## Primary OLS
```
                            OLS Regression Results                            
==============================================================================
Dep. Variable:                      y   R-squared:                       0.763
Model:                            OLS   Adj. R-squared:                  0.725
Method:                 Least Squares   F-statistic:                     22.94
Date:                Mon, 06 Jul 2026   Prob (F-statistic):           1.56e-06
Time:                        03:56:04   Log-Likelihood:                -13.982
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

## Secondary: Spearman(work_minutes, adoption) = -0.851 (p = 0.0000)

## Leave-one-country-out influence (primary coefficient)

- base log(work_minutes) coef: -0.0505
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

[INFERENCE] With small N the estimate is imprecise and collinearity between
affordability and income is expected (VIF reported in the notebook); read the
coefficient as 'does the tax add explanatory power beyond income', not as an effect.
