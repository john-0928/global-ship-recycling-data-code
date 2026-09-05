#!/usr/bin/env python3
"""Reproduce public-data results without proprietary statistical packages."""
from pathlib import Path
import math
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "public" / "processed_dismantling_2014_2025.csv"
OUT = ROOT / "precomputed_results"
SRC = ROOT / "source_data"


def design(df, outcome):
    cols = [outcome, "eu_owner", "post_2019", "age", "ln_ldt", "year", "ship_type_group"]
    a = df[cols].dropna().copy()
    a["eu_owner_x_post"] = a.eu_owner * a.post_2019
    parts = [
        pd.Series(1.0, index=a.index, name="constant"),
        a[["eu_owner", "post_2019", "eu_owner_x_post", "age", "ln_ldt"]].astype(float),
        pd.get_dummies(a.year.astype(str), prefix="year", drop_first=True, dtype=float),
        pd.get_dummies(a.ship_type_group.astype(str), prefix="type", drop_first=True, dtype=float),
    ]
    return a, pd.concat(parts, axis=1).astype(float)


def ols_hc1(y, x):
    xx = x.to_numpy(float)
    yy = np.asarray(y, dtype=float)
    inv = np.linalg.pinv(xx.T @ xx)
    beta = inv @ xx.T @ yy
    resid = yy - xx @ beta
    n, k = xx.shape
    meat = xx.T @ ((resid ** 2)[:, None] * xx)
    vcov = (n / (n - k)) * inv @ meat @ inv
    se = np.sqrt(np.maximum(np.diag(vcov), 0))
    return beta, se, n, k


def baseline_models(df):
    labels = {
        "south_asia_dismantling": "South Asia dismantling",
        "owner_final_flag_mismatch": "Owner–final-flag mismatch",
        "itf_foc_flag": "Final ITF flag of convenience",
        "south_asia_mismatch": "South Asia + mismatch",
        "south_asia_match": "South Asia + match",
        "non_south_asia_mismatch": "Non-South Asia + mismatch",
        "non_south_asia_match": "Non-South Asia + match",
    }
    rows = []
    for outcome, label in labels.items():
        a, x = design(df, outcome)
        b, se, n, k = ols_hc1(a[outcome], x)
        j = x.columns.get_loc("eu_owner_x_post")
        rows.append({
            "outcome": outcome, "label": label, "coefficient": b[j],
            "robust_se_hc1": se[j], "ci95_low": b[j] - 1.96 * se[j],
            "ci95_high": b[j] + 1.96 * se[j], "n": n, "k": k,
            "specification": "LPM; year and coarse ship-type FE; age and ln(LDT); HC1 SE",
        })
    return pd.DataFrame(rows)


def annual_interactions(df):
    base_year = 2018
    rows = []
    for outcome in ["south_asia_dismantling", "owner_final_flag_mismatch", "itf_foc_flag"]:
        cols = [outcome, "eu_owner", "age", "ln_ldt", "year", "ship_type_group"]
        a = df[cols].dropna().copy()
        years = sorted(a.year.unique())
        xparts = [pd.Series(1.0, index=a.index, name="constant"), a[["eu_owner", "age", "ln_ldt"]].astype(float)]
        yd = pd.get_dummies(a.year.astype(str), prefix="year", drop_first=False, dtype=float)
        xparts.append(yd.drop(columns=[f"year_{base_year}"]))
        td = pd.get_dummies(a.ship_type_group.astype(str), prefix="type", drop_first=True, dtype=float)
        xparts.append(td)
        for yr in years:
            if yr == base_year:
                continue
            xparts.append(pd.Series(a.eu_owner * (a.year == yr).astype(int), index=a.index, name=f"eu_owner_x_{yr}"))
        x = pd.concat(xparts, axis=1).astype(float)
        b, se, n, _ = ols_hc1(a[outcome], x)
        rows.append({"outcome": outcome, "year": base_year, "coefficient": 0.0, "robust_se_hc1": np.nan, "ci95_low": np.nan, "ci95_high": np.nan, "n": n, "reference_year": True})
        for yr in years:
            if yr == base_year:
                continue
            j = x.columns.get_loc(f"eu_owner_x_{yr}")
            rows.append({"outcome": outcome, "year": yr, "coefficient": b[j], "robust_se_hc1": se[j], "ci95_low": b[j]-1.96*se[j], "ci95_high": b[j]+1.96*se[j], "n": n, "reference_year": False})
    return pd.DataFrame(rows)


def period_share_changes(df, group_col, output_name):
    d = df[df[group_col].notna()].copy()
    denom = d.groupby("period").ldt_filled.sum().rename("period_total_ldt")
    q = d.groupby(["period", group_col], as_index=False).ldt_filled.sum().merge(denom, on="period")
    q["share_pct"] = 100 * q.ldt_filled / q.period_total_ldt
    wide = q.pivot(index=group_col, columns="period", values="share_pct").fillna(0).reset_index()
    for c in ["2014–2018", "2019–2025"]:
        if c not in wide:
            wide[c] = 0.0
    wide["change_percentage_points"] = wide["2019–2025"] - wide["2014–2018"]
    wide = wide.sort_values("change_percentage_points", ascending=False)
    wide.to_csv(SRC / output_name, index=False)
    return wide


def owner_country_mismatch_changes(df):
    """Figure 2b: within-country mismatch-rate changes; retain countries with n>=50."""
    rows = []
    for country, g in df[df.beneficial_owner_country.notna()].groupby("beneficial_owner_country"):
        if len(g) < 50 or g.period.nunique() < 2:
            continue
        rates = 100 * g.groupby("period").owner_final_flag_mismatch.mean()
        rows.append({
            "beneficial_owner_country": country,
            "n_2014_2025": len(g),
            "mismatch_rate_pct_2014_2018": rates.get("2014–2018", np.nan),
            "mismatch_rate_pct_2019_2025": rates.get("2019–2025", np.nan),
            "change_percentage_points": rates.get("2019–2025", np.nan) - rates.get("2014–2018", np.nan),
        })
    return pd.DataFrame(rows).sort_values("change_percentage_points", ascending=False)


def final_foc_flag_share_changes(df):
    """Figure 2c: changes in count shares within the subset using an ITF FoC flag."""
    d = df[(df.itf_foc_flag == 1) & df.final_flag.notna()].copy()
    denom = d.groupby("period").size().rename("period_foc_vessel_count")
    q = d.groupby(["period", "final_flag"], as_index=False).size().rename(columns={"size":"flag_vessel_count"}).merge(denom, on="period")
    q["share_pct"] = 100 * q.flag_vessel_count / q.period_foc_vessel_count
    w = q.pivot(index="final_flag", columns="period", values="share_pct").fillna(0).reset_index()
    for c in ["2014–2018", "2019–2025"]:
        if c not in w:
            w[c] = 0.0
    w["change_percentage_points"] = w["2019–2025"] - w["2014–2018"]
    return w.sort_values("change_percentage_points", ascending=False)


def recycling_destination_changes_eu(df):
    d = df[(df.eu_owner == 1) & df.recycling_country.notna()].copy()
    years = {"2014–2018": 5, "2019–2025": 7}
    g = d.groupby(["period", "recycling_country"], as_index=False).ldt_filled.sum()
    g["annualized_ldt"] = g.apply(lambda r: r.ldt_filled / years[r.period], axis=1)
    totals = g.groupby("period").ldt_filled.sum().rename("period_total")
    g = g.merge(totals, on="period")
    g["share_pct"] = 100 * g.ldt_filled / g.period_total
    w = g.pivot(index="recycling_country", columns="period", values=["annualized_ldt", "share_pct"]).fillna(0)
    w.columns = [f"{a}_{b}" for a, b in w.columns]
    w = w.reset_index()
    w["change_annualized_ldt"] = w.get("annualized_ldt_2019–2025", 0) - w.get("annualized_ldt_2014–2018", 0)
    w["change_share_percentage_points"] = w.get("share_pct_2019–2025", 0) - w.get("share_pct_2014–2018", 0)
    return w.sort_values("change_share_percentage_points", ascending=False)


def concentration_by_dimension(df):
    rows = []
    for col, label in [("beneficial_owner_country", "Economic control"), ("final_flag", "Legal registration"), ("recycling_country", "Environmental burden")]:
        g = df[df[col].notna()].groupby(col).ldt_filled.sum().sort_values(ascending=False)
        shares = g / g.sum()
        rows.append({"dimension": label, "top1_share_pct": 100*shares.iloc[:1].sum(), "top3_share_pct": 100*shares.iloc[:3].sum(), "top5_share_pct": 100*shares.iloc[:5].sum(), "total_ldt": g.sum(), "number_of_locations": len(g)})
    return pd.DataFrame(rows)


def subgroup_models(df):
    pre = df[df.year <= 2018]
    age_cut = pre.age.median()
    ldt_cut = pre.ldt_filled.median()
    groups = {
        "Older ships": df.age > age_cut,
        "Younger ships": df.age <= age_cut,
        "Larger ships": df.ldt_filled > ldt_cut,
        "Smaller ships": df.ldt_filled <= ldt_cut,
    }
    rows = []
    for label, mask in groups.items():
        for outcome in ["owner_final_flag_mismatch", "south_asia_dismantling", "itf_foc_flag"]:
            a, x = design(df[mask], outcome); b, se, n, _ = ols_hc1(a[outcome], x); j=x.columns.get_loc("eu_owner_x_post")
            rows.append({"group":label,"outcome":outcome,"coefficient":b[j],"robust_se_hc1":se[j],"ci95_low":b[j]-1.96*se[j],"ci95_high":b[j]+1.96*se[j],"n":n,"age_cutoff_pre2019":age_cut,"ldt_cutoff_pre2019":ldt_cut})
    return pd.DataFrame(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True); SRC.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA)
    df["post_2019"] = (df.year >= 2019).astype(int)
    df["period"] = np.where(df.year >= 2019, "2019–2025", "2014–2018")
    df["south_asia_mismatch"] = ((df.south_asia_dismantling == 1) & (df.owner_final_flag_mismatch == 1)).astype(int)
    df["south_asia_match"] = ((df.south_asia_dismantling == 1) & (df.owner_final_flag_mismatch == 0)).astype(int)
    df["non_south_asia_mismatch"] = ((df.south_asia_dismantling == 0) & (df.owner_final_flag_mismatch == 1)).astype(int)
    df["non_south_asia_match"] = ((df.south_asia_dismantling == 0) & (df.owner_final_flag_mismatch == 0)).astype(int)

    base = baseline_models(df); base.to_csv(OUT / "baseline_conditional_differences.csv", index=False); base.to_csv(SRC / "figure2d_baseline_and_combinations.csv", index=False)
    annual = annual_interactions(df); annual.to_csv(OUT / "annual_interactions_2014_2025.csv", index=False); annual.to_csv(SRC / "supplementary_figure2_annual_interactions.csv", index=False)
    owner_country_mismatch_changes(df).to_csv(SRC / "figure2b_owner_country_mismatch_changes.csv", index=False)
    final_foc_flag_share_changes(df).to_csv(SRC / "figure2c_final_foc_flag_share_changes.csv", index=False)
    recycling_destination_changes_eu(df).to_csv(SRC / "figure2a_eu_owned_destination_changes.csv", index=False)
    concentration_by_dimension(df).to_csv(SRC / "figure3c_responsibility_concentration.csv", index=False)
    subgroup_models(df).to_csv(OUT / "age_and_size_subgroup_estimates.csv", index=False)
    print(base[["label","coefficient","robust_se_hc1","n"]].to_string(index=False))


if __name__ == "__main__":
    main()
