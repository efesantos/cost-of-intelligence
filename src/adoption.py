"""Pre-registered adoption analysis (Task B-7).

Tests, CORRELATIONALLY, whether the affordability penalty (work_minutes) is
associated with country-level AI adoption (AEI usage_per_capita_index), beyond
income. The specification is in docs/adoption_analysis_plan.md. That file was committed
in the same commit as the merged outcome data, so git history alone cannot show
it came first; see the plan's "Deviations from pre-registration" section.

Primary spec: log(AEI_pc) ~ log(work_minutes) + log(GDPpc_PPP) + internet_pct,
OLS with HC3 robust SEs. Secondary: Spearman rank correlation (work_minutes, AEI)
and the partial rank association after residualising both on the controls.
Robustness (plan section 5): wage-tier swap (check 2), alternate country mapping
(check 3), leave-one-country-out (check 4); plus a tokenizer-family swap. Check 1
(EF EPI English-proficiency control) is not run: no EF EPI data in the repository.
An exploratory decomposition (fertility vs wage terms) is reported separately and
labelled as not pre-registered.

Fixed framing (verbatim): "association, not causation; affordability is collinear
with development -- we report whether the tax adds explanatory power beyond income,
not whether it causes non-adoption."
"""
from __future__ import annotations

import pathlib
import re

import numpy as np
import pandas as pd
import yaml

import instruments as I

ROOT = pathlib.Path(__file__).resolve().parents[1]
INSTR = ROOT / "data" / "instruments.parquet"
AEI = ROOT / "data" / "aei.parquet"
CONTROLS = ROOT / "data" / "controls.parquet"
MAPPING = ROOT / "config" / "country_language.yaml"
OUT = ROOT / "reports" / "adoption_results.md"


def _summary_text(model) -> str:
    """statsmodels' summary with the run date and time blanked, so the report changes only when
    the results do."""
    return re.sub(r"^(Date|Time):( +)(.+?)(   )", lambda m: f"{m[1]}:{m[2]}{' ' * len(m[3])}{m[4]}",
                  str(model.summary()), flags=re.M)


def build_panel(family: str = "openai_o200k", wage_kind: str = "ppp",
                mapping_kind: str = "primary") -> pd.DataFrame:
    """mapping_kind="primary": each language's primary country (the primary spec).
    mapping_kind="expanded": also each language's alternate countries (check 3)."""
    instr = (pd.read_parquet(INSTR) if mapping_kind == "primary"
             else I.compute(include_alternates=True))
    aei = pd.read_parquet(AEI)[["country", "usage_per_capita_index"]]
    controls = pd.read_parquet(CONTROLS)[["country", "gdp_pc_ppp", "internet_pct"]]
    mapping = yaml.safe_load(MAPPING.read_text())
    pairs = [(lang, m["primary"]) for lang, m in mapping["languages"].items()]
    if mapping_kind == "expanded":
        pairs += [(lang, c) for lang, m in mapping["languages"].items() for c in m.get("alternates", [])]

    # one work_minutes per country = its (first-listed) language, chosen family and
    # wage basis; a country that is primary for some language keeps that language
    rows = []
    for lang, country in pairs:
        sub = instr[(instr.language == lang) & (instr.family == family) & (instr.country == country)]
        if len(sub):
            rows.append({"country": country, "language": lang,
                         "work_minutes": sub.iloc[0][f"work_minutes_{wage_kind}"],
                         "fertility": sub.iloc[0]["fertility"]})
    panel = pd.DataFrame(rows).drop_duplicates("country")
    panel = panel.merge(aei, on="country").merge(controls, on="country")
    panel = panel[(panel.usage_per_capita_index > 0) & (panel.work_minutes > 0) &
                  (panel.gdp_pc_ppp > 0)].dropna(subset=["internet_pct", "work_minutes"])
    return panel


def run_ols(panel: pd.DataFrame):
    import statsmodels.api as sm
    y = np.log(panel["usage_per_capita_index"].values)
    X = pd.DataFrame({
        "log_work_minutes": np.log(panel["work_minutes"].values),
        "log_gdp_ppp": np.log(panel["gdp_pc_ppp"].values),
        "internet_pct": panel["internet_pct"].values,
    })
    X = sm.add_constant(X)
    model = sm.OLS(y, X).fit(cov_type="HC3")
    return model


def leave_one_out(panel: pd.DataFrame) -> pd.DataFrame:
    base = run_ols(panel).params["log_work_minutes"]
    rows = []
    for i, c in enumerate(panel["country"]):
        p = panel.drop(panel.index[i])
        try:
            coef = run_ols(p).params["log_work_minutes"]
            rows.append({"dropped": c, "log_work_minutes_coef": coef,
                         "sign_flip": np.sign(coef) != np.sign(base)})
        except Exception:  # noqa: BLE001
            continue
    return pd.DataFrame(rows)


def vif(panel: pd.DataFrame) -> dict:
    import statsmodels.api as sm
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    X = sm.add_constant(pd.DataFrame({
        "log_work_minutes": np.log(panel["work_minutes"].values),
        "log_gdp_ppp": np.log(panel["gdp_pc_ppp"].values),
        "internet_pct": panel["internet_pct"].values,
    }))
    return {c: variance_inflation_factor(X.values, j) for j, c in enumerate(X.columns) if c != "const"}


def partial_spearman(panel: pd.DataFrame):
    """Rank association of work_minutes and adoption after residualising both
    (in logs) on the controls, as specified in plan section 4."""
    import statsmodels.api as sm
    from scipy.stats import spearmanr
    Z = sm.add_constant(pd.DataFrame({"log_gdp_ppp": np.log(panel["gdp_pc_ppp"].values),
                                      "internet_pct": panel["internet_pct"].values}))
    ry = sm.OLS(np.log(panel["usage_per_capita_index"].values), Z).fit().resid
    rx = sm.OLS(np.log(panel["work_minutes"].values), Z).fit().resid
    return spearmanr(rx, ry)


def decomposition(panel: pd.DataFrame, wage_kind: str) -> dict:
    """EXPLORATORY, not pre-registered. log(work_minutes) = log(fertility) - log(wage)
    + const within one family, so fitting the two terms separately shows which one
    carries any association beyond the controls."""
    import statsmodels.api as sm
    wages = pd.read_parquet(ROOT / "data" / "wages.parquet").set_index("country")
    ilo = pd.read_parquet(ROOT / "data" / "ilostat_wages.parquet").set_index("country")
    col = {"ppp": wages["hourly_wage_usd_ppp"], "market": wages["hourly_wage_usd_market"],
           "ilo": ilo["hourly_wage_usd_ilo"]}[wage_kind]
    X = sm.add_constant(pd.DataFrame({
        "log_fertility": np.log(panel["fertility"].values),
        "log_wage": np.log(panel["country"].map(col).values),
        "log_gdp_ppp": np.log(panel["gdp_pc_ppp"].values),
        "internet_pct": panel["internet_pct"].values,
    }))
    m = sm.OLS(np.log(panel["usage_per_capita_index"].values), X).fit(cov_type="HC3")
    return {k: (m.params[k], m.pvalues[k]) for k in ("log_fertility", "log_wage", "log_gdp_ppp")}


def _fmt(model) -> str:
    c, se, pv = (model.params["log_work_minutes"], model.bse["log_work_minutes"],
                 model.pvalues["log_work_minutes"])
    return f"{c:.3f} | {se:.3f} | {pv:.3f}"


def main() -> None:
    from scipy.stats import spearmanr
    panel = build_panel()
    n = len(panel)
    model = run_ols(panel)
    rho, pval = spearmanr(panel["work_minutes"], panel["usage_per_capita_index"])
    prho, ppval = partial_spearman(panel)
    loo = leave_one_out(panel)
    v = vif(panel)
    aei_all = pd.read_parquet(AEI)
    missing = [lang_c for lang_c in
               sorted(set(pd.read_parquet(INSTR)["country"]) - set(panel["country"]))]

    lines = [
        "# Adoption analysis results (Task B-7)",
        "",
        "> **association, not causation; affordability is collinear with development — we report",
        "> whether the tax adds explanatory power beyond income, not whether it causes non-adoption.**",
        "",
        f"Panel N = {n} countries. Outcome = log(AEI usage_per_capita_index). "
        "Primary regressor = log(work_minutes) (o200k family, PPP wage). Controls = "
        "log(GDP per capita PPP), internet penetration %. HC3 robust SEs.",
        "",
        f"Countries with instruments but no usable AEI value (excluded on missing data, as the plan "
        f"requires): {', '.join(missing) if missing else 'none'}. "
        f"The AEI file has {len(aei_all)} geographies, {int((aei_all.usage_per_capita_index > 0).sum())} "
        "with a positive usage index.",
        "",
        "## Primary OLS",
        "```",
        _summary_text(model),
        "```",
        "",
        "Variance inflation factors: " + ", ".join(f"{k} = {x:.1f}" for k, x in v.items()) +
        f". Correlation of log(work_minutes) with log(GDP per capita PPP) = "
        f"{np.corrcoef(np.log(panel.work_minutes), np.log(panel.gdp_pc_ppp))[0, 1]:.3f}.",
        "",
        f"## Secondary: Spearman(work_minutes, adoption) = {rho:.3f} (p = {pval:.4f})",
        "",
        f"Partial rank association after residualising both on the controls: rho = {prho:.3f} "
        f"(p = {ppval:.3f}).",
        "",
        "## Pre-registered robustness checks (plan section 5)",
        "",
        "Checks 2 and 3 were run on 2026-10-10, after the primary result was known. They are",
        "the checks the plan specified, unchanged; check 1 was not run (no EF EPI data).",
        "",
        "| check | specification | N | coef on log(work_minutes) | HC3 SE | p |",
        "|---|---|---|---|---|---|",
        f"| primary | o200k, WB PPP wage, primary mapping | {n} | {_fmt(model)} |",
    ]
    for kind, label in (("market", "WB market-rate wage (GNI Atlas / 2080 h)"),
                        ("ilo", "ILOSTAT mean employee earnings (US$)")):
        pk = build_panel(wage_kind=kind)
        lines.append(f"| 2. wage-tier swap | {label} | {len(pk)} | {_fmt(run_ols(pk))} |")
    for kind in ("ppp", "market", "ilo"):
        pe = build_panel(wage_kind=kind, mapping_kind="expanded")
        lines.append(f"| 3. alternate mapping | primary + alternate countries, {kind} wage | "
                     f"{len(pe)} | {_fmt(run_ols(pe))} |")
    lines += ["", "Additional check named in this script (not in the plan): tokenizer-family swap, "
              "PPP wage, primary mapping.", "",
              "| family | N | coef | HC3 SE | p |", "|---|---|---|---|---|"]
    for fam in ("llama3", "qwen2", "gemma", "aya"):
        pf = build_panel(family=fam)
        lines.append(f"| {fam} | {len(pf)} | {_fmt(run_ols(pf))} |")

    lines += ["", "## Leave-one-country-out influence (check 4, primary coefficient)", "",
              f"- base log(work_minutes) coef: {model.params['log_work_minutes']:.4f}",
              f"- range on omission: {loo['log_work_minutes_coef'].min():.4f} to "
              f"{loo['log_work_minutes_coef'].max():.4f}",
              f"- any sign flip on omission: {bool(loo['sign_flip'].any()) if len(loo) else 'n/a'}",
              "", "| dropped | coef | sign flip |", "|---|---|---|"]
    for _, r in loo.iterrows():
        lines.append(f"| {r['dropped']} | {r['log_work_minutes_coef']:.4f} | {r['sign_flip']} |")

    lines += ["", "## Exploratory decomposition (NOT pre-registered)", "",
              "Within one tokenizer family, log(work_minutes) = log(fertility) - log(wage) + constant.",
              "Fitting the two terms separately (same controls, HC3) shows which one carries any",
              "association. Read as description only.", "",
              "| wage basis | log(fertility) coef (p) | log(wage) coef (p) | log(GDP pc PPP) coef (p) |",
              "|---|---|---|---|"]
    for kind in ("ppp", "market", "ilo"):
        pk = build_panel(wage_kind=kind)
        d = decomposition(pk, kind)
        lines.append(f"| {kind} | " + " | ".join(f"{d[k][0]:.3f} ({d[k][1]:.3f})" for k in
                                                 ("log_fertility", "log_wage", "log_gdp_ppp")) + " |")
    lines += ["", "[INFERENCE] With small N the estimates are imprecise, and affordability is strongly",
              "collinear with income (see the VIFs above). Read each coefficient as 'does this term add",
              "explanatory power beyond income in this sample', not as an effect."]
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} (N={n})")
    print(f"  log(work_minutes) coef = {model.params['log_work_minutes']:.4f} "
          f"(HC3 p = {model.pvalues['log_work_minutes']:.4f})")
    print(f"  Spearman rho = {rho:.3f} (p = {pval:.4f})")


if __name__ == "__main__":
    main()
