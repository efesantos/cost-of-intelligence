# Adoption analysis results (Task B-7)

> **association, not causation; affordability is collinear with development — we report
> whether the tax adds explanatory power beyond income, not whether it causes non-adoption.**

Panel N = 9 countries. Outcome = log(AEI usage_per_capita_index). Primary regressor = log(work_minutes) (o200k family, PPP wage). Controls = log(GDP per capita PPP), internet penetration %. HC3 robust SEs.

## Primary OLS
```
                            OLS Regression Results                            
==============================================================================
Dep. Variable:                      y   R-squared:                       0.842
Model:                            OLS   Adj. R-squared:                  0.747
Method:                 Least Squares   F-statistic:                     9.740
Date:                Mon, 06 Jul 2026   Prob (F-statistic):             0.0157
Time:                        03:26:54   Log-Likelihood:                -4.3544
No. Observations:                   9   AIC:                             16.71
Df Residuals:                       5   BIC:                             17.50
Df Model:                           3                                         
Covariance Type:                  HC3                                         
====================================================================================
                       coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------------
const               -2.4840     41.541     -0.060      0.952     -83.902      78.934
log_work_minutes    -0.6891      2.530     -0.272      0.785      -5.647       4.269
log_gdp_ppp          0.6968      2.988      0.233      0.816      -5.160       6.554
internet_pct        -0.0224      0.031     -0.712      0.476      -0.084       0.039
==============================================================================
Omnibus:                        1.660   Durbin-Watson:                   3.316
Prob(Omnibus):                  0.436   Jarque-Bera (JB):                0.783
Skew:                          -0.225   Prob(JB):                        0.676
Kurtosis:                       1.627   Cond. No.                     1.63e+04
==============================================================================

Notes:
[1] Standard Errors are heteroscedasticity robust (HC3)
[2] The condition number is large, 1.63e+04. This might indicate that there are
strong multicollinearity or other numerical problems.
```

## Secondary: Spearman(work_minutes, adoption) = -0.683 (p = 0.0424)

## Leave-one-country-out influence (primary coefficient)

- base log(work_minutes) coef: -0.6891
- any sign flip on omission: True

| dropped | coef | sign flip |
|---|---|---|
| USA | 0.2710 | True |
| PRT | -0.7346 | False |
| MEX | -0.7929 | False |
| FRA | -0.8492 | False |
| KEN | 0.4550 | True |
| NGA | 0.4612 | True |
| ZAF | -2.2305 | False |
| EGY | -1.3133 | False |
| IND | -0.4885 | False |

[INFERENCE] With small N the estimate is imprecise and collinearity between
affordability and income is expected (VIF reported in the notebook); read the
coefficient as 'does the tax add explanatory power beyond income', not as an effect.
