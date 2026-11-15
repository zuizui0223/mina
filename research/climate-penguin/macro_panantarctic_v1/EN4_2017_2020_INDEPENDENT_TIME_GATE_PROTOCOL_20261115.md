# Antarctic coastal salinity 2019–2020 source-verification gate (2026-11-15)

**Goal:** test whether genuinely measured upper-ocean salinity profiles could independently support or contradict the two unusually low *GLORYS reanalysis* source years, without post-result geographic cherry-picking. This is one source-verification extension of Antarctic macroecology Draft PR #214, not a second manuscript, and does not re-open frozen penguin Paper1/Paper2.

## Fixed original input

- Official [UK Met Office EN4.2.2](https://www.metoffice.gov.uk/hadobs/en4/download-en4-2-2.html) **g10 raw profile** annual ZIPs, 2017, 2018, 2019, 2020; **August, September, October, November** monthly NetCDF members in each annual ZIP. No gridded EN4 objective analysis is substituted for raw observations.
- Existing original 588 sites / 18 source regions from source-verified GLORYS/OSI SAF coordinates, held fixed before inspecting new EN4 salinity values: [588-site source list](source_audit_20261115/source_cohort_climate_support_588_sites.csv).
- Original profiles must pass position QC 1, whole salinity-profile QC 1, individual salinity-level QC 1, true measured corrected depth 0–10 m and physical salinity 28–38. One actual profile may be assigned to only its **nearest** original colony by WGS84 distance and only if within 100 km. For comparison of source coverage **only**, repeat with 20 m and 250 km gates, labelled distinctly.
- Original monthly ZIP member checksums are verified by the original ZIP CRC32 and each uncompressed NetCDF SHA256. Only the 16 selected months' publisher ZIP byte ranges are retrieved; never claim a hash for the complete annual publisher ZIP unless the full archive is downloaded and checked.
- Individual profiles, locations, salinity readings and platform identifiers stay in memory; only **region–calendar-year–month counts, unique platform counts and platform-equal means from supported cells** are saved and uploaded. Do not publish raw Met Office observational records.

## One fixed independent comparison

For each of the 18 source regions and four original months separately, compute the mean measured salinity **with one vote per identified observing platform** rather than one vote per profile (so repeated cruises do not automatically dominate). Require **at least three distinct identified platforms in every one of the four comparison years** for each month. Retain only months satisfying the same condition in 2017, 2018, 2019 and 2020. Require **at least two common qualified months** before contrasting the equal-month 2017–2018 and 2019–2020 average in the *same region*. If no region passes, record an empirical **NO-GO due to true observation support**, not a zero effect or lack of physical ocean freshening.

The four-year contrast is **not** the same estimand as 2019/2020 departures from GLORYS 1993–2018: a matching sign would be local observational support only. Independently measured EN4 inputs may overlap with what GLORYS assimilated, so this is a *direct observation cross-check*, not independently sampled ocean climate experiments.

## Decision boundaries

1. If 0 regions pass the strict 100-km/0–10m comparison: retain the previously established **2019/2020 GLORYS source hold**, with a specific measured lack-of-support denominator. The relaxed depth/distance contrasts are not promoted into the primary result.
2. If 1–17 regions pass: report observed salinity change in those **named, source-supported regions only** with instruments and months as effective denominators; no claim of an 18-region coherent event.
3. If all 18 regions pass, a cross-region sign summary becomes descriptive evidence on raw observations, but the 2017–2020 window does not establish a 28-year synchronized climate mode. Formal attribution to the coincident ERA-Interim→ERA5 forcing switch remains untested.

The script will fail closed on missing original EN4 months, corrupt ZIP member/NetCDF, changed 588-site geography or unknown source status. Its source-free synthetic aggregation tests must pass before accessing the official publisher server. An Actions success means **the source gate ran**, not that the outcome was ecologically or physically confirmed.

## Reproduce

Source code: [en4_2017_2020_raw_salinity_time_gate.py](en4_2017_2020_raw_salinity_time_gate.py). Workflow: [original EN4 2017–2020 raw source gate](../../.github/workflows/penguin-original-EN4-2017-2020-raw-salinity-time-gate.yml). Publisher [EN4 data product](https://www.metoffice.gov.uk/hadobs/en4/download-en4-2-2.html) and Good et al. (2013), DOI 10.1002/2013JC009067. Outputs are a source integrity receipt JSON, region/month QC coverage CSV and an explicitly eligibility-flagged platform-equal four-year comparison CSV, **not raw profiles**.
