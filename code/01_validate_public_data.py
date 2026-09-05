#!/usr/bin/env python3
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "public" / "processed_dismantling_2014_2025.csv"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    df = pd.read_csv(DATA)
    required = {
        "imo_number", "gross_tonnage", "year", "age", "eu_owner",
        "south_asia_dismantling", "itf_foc_flag", "owner_final_flag_mismatch",
        "ln_ldt", "ldt_filled", "ldt_imputed_flag", "ldt_fill_method",
        "ship_type_group", "beneficial_owner_country", "recycling_country",
        "final_flag"
    }
    require(required.issubset(df.columns), f"Missing columns: {sorted(required-set(df.columns))}")
    require(len(df) == 7919, f"Expected 7,919 rows, found {len(df):,}")
    require(df.year.min() == 2014 and df.year.max() == 2025, "Unexpected year range")
    require(df.age.notna().sum() == 7917, "Expected 7,917 non-missing age values")
    require((df.ldt_fill_method == "original").sum() == 3713, "Unexpected original-LDT count")
    require(df.ldt_imputed_flag.fillna(0).astype(int).sum() == 4206, "Unexpected imputed-LDT count")
    for col in ["eu_owner", "south_asia_dismantling", "itf_foc_flag", "owner_final_flag_mismatch"]:
        require(set(df[col].dropna().unique()).issubset({0, 1}), f"{col} is not binary")
    print("PASS: public dismantling dataset validated")
    print(f"Rows: {len(df):,}; years: {df.year.min()}–{df.year.max()}; baseline-complete: {df.age.notna().sum():,}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise

