# Global ship recycling separates economic control, legal registration and environmental burdens

Code-only package, version 1.0 (draft for repository deposit).

## Scope

This package supports the manuscript titled **“Global ship recycling separates economic control, legal registration and environmental burdens.”** It contains analysis code and documentation only. No empirical data, input templates, vessel-level records, figure source data, precomputed result tables or proprietary market series are included.

This package does **not** belong to the earlier 2026–2050 market-conditioned projection and HKC emission-scenario study. Projection, country-allocation and emission-accounting files from that earlier version are intentionally excluded.

## Contents

- `code/01_validate_public_data.py`: checks row counts, years, variables and internal coding consistency.
- `code/02_reproduce_public_analysis.py`: analysis workflow for authorized local inputs.
- `code/03_prepare_restricted_fleet_aggregates.py`: creates non-disclosive aggregates when an authorized Clarksons file is supplied locally.
- `THIRD_PARTY_DATA_NOTICE.md`: restrictions and attribution requirements.
- `ZENODO_METADATA_TEMPLATE.md`: recommended Zenodo fields.

## Quick start

From the package root:

```bash
python code/01_validate_public_data.py
python code/02_reproduce_public_analysis.py
```

Required Python packages are listed in `requirements.txt`. The validation and analysis scripts require an authorized local input file that is not included in this repository.

## Restricted fleet analysis

The active-fleet register used in the manuscript was obtained from the Shipping Intelligence Network of Clarksons Research under licence. It cannot be redistributed. An authorized researcher may place the file outside this public package and run:

```bash
python code/03_prepare_restricted_fleet_aggregates.py \
  --input /path/to/authorized_active_fleet.xlsx \
  --output precomputed_results/restricted_fleet_aggregates
```

The script checks the required columns and writes country/flag/year aggregates only. It does not copy vessel-level Clarksons records into the repository.

## Reproducibility boundary

No empirical data are distributed in this repository. Reproduction requires authorized access to the study inputs. Fleet-age pressure, registered-GT maps and top-20 flag-state coverage additionally require the licensed, study-scope fleet register after the authors' upstream sample screening.

This public release intentionally retains the restricted-data boundary. The broader 66,643-record working fleet file is not itself the manuscript analysis sample; the study-scope screening must be applied before the reported 58,029-record cleaned sample is checked. See `RELEASE_CHECKLIST.md`.

## Citation

The DOI should be inserted into `CITATION.cff`, the manuscript’s Data availability statement and the Code availability statement after the Zenodo record is reserved or published.
