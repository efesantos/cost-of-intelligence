# Adoption Analysis Pre-Registration (Task B-7)

**Status: COMMITTED before data merge.** This document is fixed *before* the affordability
index is joined to any adoption outcome. The git history of this repository is the proof of
temporal order: the commit that adds this file predates the commit that produces the merged
analysis dataset. Nothing below may be edited after the merge except to record deviations in a
clearly marked "Deviations from pre-registration" section.

---

## 1. Purpose and framing

We test whether a country's **affordability penalty** for LLM tokens (the Stream B
Affordability Index, in local work-minutes to buy a fixed English-equivalent token bundle) is
associated with **lower LLM adoption**, after controlling for development.

**Fixed correlational-framing sentence (verbatim, non-negotiable):**

> This is an association, not causation; affordability is collinear with development — we report
> whether the tax adds explanatory power beyond income, not whether it causes non-adoption.

This sentence must appear, unchanged, in every write-up of the B-7 result (paper, slides,
README). The analysis is explicitly **correlational and NOT causal**. We make no counterfactual
or interventional claim.

---

## 2. Data

- **Outcome (dependent variable):** country-level LLM adoption, taken from the Anthropic
  Economic Index (McCrory et al. 2025, arXiv 2511.15080; HF dataset `Anthropic/EconomicIndex`),
  expressed per capita. Denoted `AEI_pc`. Exact vintage/version of the dataset is live-pulled and
  date-stamped at merge time: `{{AEI dataset version + pull date recorded in B-7 run log}}`.
- **Primary regressor:** `work_minutes`, the Affordability Index value per country (Instrument 3),
  computed in Task B-5. Value is `{{computed in B-5}}`, date-stamped to the price pull.
- **Controls:** `GDPpc_PPP` (GDP per capita, PPP), `internet_penetration`.
- **Country coverage / N:** target **N ≥ 15 countries**. Countries are the Lusophone/Hispanophone
  Global South set defined in B-5 plus any additional AEI-covered countries meeting the
  data-completeness rule (all covariates present). Final N is recorded at merge: `{{N recorded in B-7}}`.

All variables entering in logs are strictly positive by construction; any country failing this is
listed in the run log with the reason for exclusion (pre-specified: exclude only on missing data,
never on outcome value).

---

## 3. Primary specification (fixed before merge)

```
log(AEI_pc) ~ log(work_minutes) + log(GDPpc_PPP) + internet_penetration
```

- **Estimator:** OLS.
- **Standard errors:** heteroskedasticity-robust, **HC3** (chosen for small-N robustness).
- **Primary coefficient of interest:** the coefficient on `log(work_minutes)`. Directional
  hypothesis: negative (worse affordability → lower adoption). We report the point estimate, HC3
  SE, and the two-sided p-value. The pre-registered *inferential* claim is confined to this one
  coefficient.

[INFERENCE — our assumption] Log-linearity of `AEI_pc` in the regressors is an assumption of the
functional form, not an established fact; §5 robustness partially probes it.

---

## 4. Secondary analysis (fixed before merge)

- **Spearman rank correlation** between `work_minutes` and `AEI_pc` (and, separately, the partial
  rank association after residualizing on the controls). Chosen as a **small-N-robust,
  distribution-free** cross-check on the OLS sign and to guard against leverage from a single
  country. Reported with its p-value.

---

## 5. Pre-specified robustness checks (fixed before merge)

All of the following are decided now, before seeing the merged data, to prevent specification
search:

1. **Add EF-EPI English-proficiency control.** Re-fit the primary spec with an EF EPI English
   proficiency index added, since proficiency plausibly confounds both fertility burden and
   adoption.
2. **Swap wage tiers.** Re-compute `work_minutes` under the alternate wage series (e.g.
   minimum-wage vs. mean/median hourly) and re-fit. Tests sensitivity to the wage input.
3. **Alternate country mapping.** Re-run under the alternate language→country assignment (e.g.
   variant-level pt-AO/pt-MZ handling vs. pooled Lusophone) to check that borderline mappings do
   not drive the result.
4. **Leave-one-country-out (LOCO) influence check.** Re-fit the primary spec N times, dropping one
   country each time; report the range of the `log(work_minutes)` coefficient and flag any single
   country whose removal flips the sign or crosses the significance threshold.

A result is described as "robust" only if the sign of the primary coefficient is stable across all
four checks. Any instability is reported, not suppressed.

---

## 6. Reproducibility

- **Random seeds:** any resampling/bootstrap uses fixed seed `SEED = 20260707` (recorded in code;
  swept over `{20260707, 20260708, 20260709}` only for the LOCO/bootstrap stability display, never
  to select a headline number).
- **Order guarantee:** this file is committed before the merge script runs; `git log` establishes
  the pre-registration timestamp.
- **Run log:** B-7 writes a dated run log capturing dataset versions, N, seeds, and all coefficients.

---

## 7. What would count as evidence

- **For the hypothesis:** negative, statistically discernible `log(work_minutes)` coefficient that
  survives §5 and a concordant negative Spearman association — reported strictly as *the
  affordability tax adds explanatory power beyond income*, never as causal.
- **Against:** coefficient near zero or positive, or one that vanishes once income/proficiency are
  controlled. This is a publishable, honest null and will be reported as such.
