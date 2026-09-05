#!/usr/bin/env python3
"""Create shareable aggregates from an authorized, study-scope Clarksons fleet file.

The proprietary vessel-level input must remain outside the public repository.
Apply the manuscript's upstream ship-type/sample-scope screening before using
this script; a broader working fleet file is not the manuscript input.
"""
from argparse import ArgumentParser
from pathlib import Path
import pandas as pd


def main():
    ap = ArgumentParser()
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--expected-cleaned-n", default=58029, type=int)
    args = ap.parse_args()
    df = pd.read_excel(args.input)
    required = {"ship_name", "build_year", "gt", "flag", "status"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Restricted fleet input is missing: {sorted(missing)}")
    clean = df[df["gt"].notna() & (df["gt"] >= 500)].drop_duplicates(["ship_name", "gt", "build_year"]).copy()
    if len(clean) != args.expected_cleaned_n:
        raise ValueError(
            f"Cleaned fleet contains {len(clean):,} rows, not the manuscript value "
            f"{args.expected_cleaned_n:,}. Confirm that the upstream study-scope screening "
            f"has been applied to the authorized input before this final cleaning step."
        )
    args.output.mkdir(parents=True, exist_ok=True)
    flag = clean.groupby("flag", as_index=False).agg(vessel_count=("flag","size"), total_gt=("gt","sum"))
    flag.sort_values("total_gt", ascending=False).to_csv(args.output / "fleet_gt_by_flag.csv", index=False)
    age = clean.assign(age_2025=2025-clean.build_year).groupby("age_2025", as_index=False).agg(vessel_count=("ship_name","size"), total_gt=("gt","sum"))
    age.to_csv(args.output / "fleet_by_age_2025.csv", index=False)
    status = clean.groupby("status", as_index=False).agg(vessel_count=("ship_name","size"), total_gt=("gt","sum"))
    status.to_csv(args.output / "fleet_by_status.csv", index=False)
    print(f"Wrote restricted-data aggregates from {len(clean):,} cleaned vessels")


if __name__ == "__main__":
    main()
