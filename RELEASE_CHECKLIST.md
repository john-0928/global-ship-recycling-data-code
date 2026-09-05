# Release checklist

## Required before reserving the final public DOI

- [ ] Add final author names, ORCID identifiers and affiliations to `CITATION.cff` and the Zenodo metadata.
- [ ] Confirm that no processed NGO Shipbreaking Platform vessel-level records are present.
- [ ] Add the exact version/access date of the ITF flag-of-convenience list.
- [ ] Add the exact version/access date of the European List of ship-recycling facilities.
- [ ] Confirm that the facility-location source table used for Figure 3a is not present.
- [ ] Document the upstream study-scope screening applied to the broader Clarksons working file before the final GT and duplicate-record checks, so an authorized user can reproduce the reported 58,029-vessel sample.
- [ ] Confirm that source tables for fleet-age pressure and top-20 flag-state GT coverage are not present.
- [ ] Correct the Figure 2 caption: panel b shows changes in the owner–final-flag mismatch rate by beneficial-owner country (countries with at least 50 observations), not changes in the share dismantled in South Asia. Panel c shows changes in each registry's share within vessels using an ITF flag of convenience.
- [ ] Test the scripts only in an authorized private environment containing the required inputs; do not copy inputs or outputs into this release.
- [ ] Replace all DOI placeholders after Zenodo reserves the DOI.
- [ ] Check that no Clarksons vessel-level file or market-series workbook is inside the upload archive.

## Current package status

This is a code-only release. It contains no dismantling records, fleet records, source tables or computed outputs. Reproduction requires authorized access to the study inputs. The broader 66,643-record working file should not be treated as the final manuscript analysis sample.
