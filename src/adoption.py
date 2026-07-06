"""Pre-registered adoption analysis (Task B-7).

Tests, CORRELATIONALLY, whether the affordability penalty (work_minutes) is
associated with country-level AI adoption (AEI usage_per_capita_index), beyond
income. The specification is fixed in docs/adoption_analysis_plan.md BEFORE this
merge (git history proves order).

Primary spec: log(AEI_pc) ~ log(work_minutes) + log(GDPpc_PPP) + internet_pct,
OLS with HC3 robust SEs. Secondary: Spearman rank correlation (work_minutes, AEI).
Robustness: leave-one-country-out influence; tokenizer-family swap.

Fixed framing (verbatim): "association, not causation; affordability is collinear
with development -- we report whether the tax adds explanatory power beyond income,
not whether it causes non-adoption."
"""
from __future__ import annotations

import pathlib

import numpy as np
import pandas as pd
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
INSTR = ROOT / "data" / "instruments.parquet"
AEI = ROOT / "data" / "aei.parquet"
CONTROLS = ROOT / "data" / "controls.parquet"
MAPPING = ROOT / "config" / "country_language.yaml"
OUT = ROOT / "reports" / "adoption_results.md"


def build_panel(family: str = "openai_o200k", wage_kind: str = "ppp") -> pd.DataFrame:
    instr = pd.read_parquet(INSTR)
    aei = pd.read_parquet(AEI)[["country", "usage_per_capita_index"]]
    controls = pd.read_parquet(CONTROLS)[["country", "gdp_pc_ppp", "internet_pct"]]
    mapping = yaml.safe_load(MAPPING.read_text())
    prim = {lang: m["primary"] for lang, m in mapping["languages"].items()}

    # one work_minutes per country = its primary language, chosen family, chosen wage basis
    rows = []
    for lang, country in prim.items():
        sub = instr[(instr.language == lang) & (instr.family == family) & (instr.country == country)]
        if len(sub):
            rows.append({"country": country, "language": lang,
                         "work_minutes": sub.iloc[0][f"work_minutes_{wage_kind}"],
                         "fertility": sub.iloc[0]["fertility"]})
    panel = pd.DataFrame(rows).drop_duplicates("country")
    panel = panel.merge(aei, on="country").merge(controls, on="country")
    panel = panel[(panel.usage_per_capita_index > 0) & (panel.work_minutes > 0) &
                  (panel.gdp_pc_ppp > 0)].dropna(subset=["internet_pct"])
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


def main() -> None:
    from scipy.stats import spearmanr
    panel = build_panel()
    n = len(panel)
    model = run_ols(panel)
    rho, pval = spearmanr(panel["work_minutes"], panel["usage_per_capita_index"])
    loo = leave_one_out(panel)

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
        "## Primary OLS",
        "```",
        str(model.summary()),
        "```",
        "",
        f"## Secondary: Spearman(work_minutes, adoption) = {rho:.3f} (p = {pval:.4f})",
        "",
        "## Leave-one-country-out influence (primary coefficient)",
        "",
        f"- base log(work_minutes) coef: {model.params['log_work_minutes']:.4f}",
        f"- any sign flip on omission: {bool(loo['sign_flip'].any()) if len(loo) else 'n/a'}",
        "",
        "| dropped | coef | sign flip |", "|---|---|---|",
    ]
    for _, r in loo.iterrows():
        lines.append(f"| {r['dropped']} | {r['log_work_minutes_coef']:.4f} | {r['sign_flip']} |")
    lines += ["", "[INFERENCE] With small N the estimate is imprecise and collinearity between",
              "affordability and income is expected (VIF reported in the notebook); read the",
              "coefficient as 'does the tax add explanatory power beyond income', not as an effect."]
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} (N={n})")
    print(f"  log(work_minutes) coef = {model.params['log_work_minutes']:.4f} "
          f"(HC3 p = {model.pvalues['log_work_minutes']:.4f})")
    print(f"  Spearman rho = {rho:.3f} (p = {pval:.4f})")


if __name__ == "__main__":
    main()
