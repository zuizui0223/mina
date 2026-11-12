# EN4 raw ocean-profile source support gate for Antarctic salinity synchrony

Date: 2026-11-12 JST. Single-thread exploratory source validation for existing 588-colony 18-region climate study, Draft PR #214. This task is raw in-situ observation coverage, not another marine model or a new paper.

## Hypothesis to check only after observational support

The existing Copernicus GLORYS12V1 1993–2020 physical marine climate panel showed a nearly salinity-only PC2 (33.377% pooled 3-variable variance). Its 18 original reporting regions shared ~52.1% of region-standardized PC2 annual variability, versus 19.7% for thermal/ice PC1; the salinity regional common-year component was ~50.6% after detrending. The source was publisher-verified and observation-year controls passed, but all salinity came from one assimilative reanalysis product. The next high-value task is to check whether the observed raw instrument profile record supports a comparable geographical and temporal signal.

## Product independent of analysis pipeline but NOT necessarily independent observations

Use official UK Met Office Hadley Centre EN.4.2.2 quality-controlled monthly original in-situ profile files (Argo, GTSPP, WOD, CTD and other instruments), not EN4 1° interpolated objective analysis. Official yearly publisher ZIP for 2015:
https://hadleyserver.metoffice.gov.uk/hadobs/en4/data/en4-2-1/EN.4.2.2/EN.4.2.2.profiles.g10.2015.zip
Official product and profile QC documentation:
https://www.metoffice.gov.uk/hadobs/en4/en4-0-2-profile-file-format.html
https://hadleyserver.metoffice.gov.uk/hadobs/en4/

EN4 raw profiles are a separate source and processing product but their instruments can also have been assimilated into GLORYS. Do not label independent physical experiments or definitive external validation. The original EN4 profile data are offered under a non-commercial government licence; do not re-upload raw yearly ZIP or redistribute individual observations. Archive only source URL/SHA256, aggregate geographically masked coverage and explicitly QC-qualified derived summaries for non-commercial research.

## Original geographical gate and QC frozen before profile readout

- Only source colony coordinates that already passed original GLORYS nearest 25km marine wet-cell gate: exactly 588 real site IDs across 18 original reporting regions, from full source geography run 42957439858. No borrowed coordinates, no species pseudoabsences, no salinity measured at the colony.
- Original profile processing from year 2015 (a source-format and spatial-coverage pilot, not a temporal synchrony test), months August–November. Read raw monthly original profile NetCDF from EN4 yearly ZIP; verify source URL, downloaded bytes SHA256, monthly file names, no source data imputation.
- Profile must have real southern latitude <=−55°, finite latitude/longitude, POSITION_QC == 1, PROFILE_PSAL_QC == 1, and at least one actual level with 0–10m corrected depth, finite practical salinity 28–38, and PSAL_CORRECTED_QC == 1 for that exact level. Choose shallowest such genuinely measured level and preserve original depth. Secondary 0–20m support reported separately (not a replacement if 0–10 sparse). No interpolation from deeper data to 0m, no EN4 objective analysis, no use of salinity if level/profile/QC says reject.
- Use WGS84 ellipsoid geodesic distance (KD-tree chord only for candidate selection), assign each source QC accepted profile to one nearest of the original 588 marine-eligible colony site IDs, with source region and 250km source block. Report <=100km (matches prior original SIC buffer radius), and broader <=250km (availability only, not a comparison to 100km GLORYS coast); profile observations should never count once for each nearby colony. Report profile/region/month support separately.
- Surface 0–10m EN4 profiles are not GLORYS 0.5m uppermost native grid and cannot be used as identical observational depth. EN4 profile uneven availability cannot be turned into one 28-year region×year panel unless each region+year+month meets an explicit source threshold.
- No official 18-region synchronization test until 2015 pilot proves in-situ coverage and source QC structure is understood. In later 1993–2020 full 112-month raw observation extraction, time density gates and different data origins (pre-/post-Argo expansion) must be controlled.
- This source pilot is not a significance test. It can return NO-GO or sparse regional support. If publisher retrieval or EN4 QC fails, log precisely rather than pretending objective analysis is a raw observation.

## Deliverable now
An actually completed GitHub Action with official 2015 yearly ZIP source URL, ZIP SHA256, four monthly original file headers/dimensions, spatial coverage (all original 18 source regions and reported <=100/250km counts), observed upper-level source-depth and QC audit. If support is strong, the next phase can reuse this code for more years; if sparse, use a high-coverage gridded observational analysis only as a weaker product-sensitivity and make the raw observation limitation explicit.
