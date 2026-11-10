# Original 1993–2020 GLORYS historical ocean extension — source gate

**Purpose**: extend original monthly *reanalysis* salinity and surface potential temperature to the
1993–2020 observed penguin breeding-count era, using exactly the same 8 fixed original wet
native 1/12-degree pixels from the existing 2011–2020 study. Do not change the selected
biological site×species comparisons or count methods.

## Frozen source

- Copernicus GLORYS12V1, dataset GLOBAL_MULTIYEAR_PHY_001_030, 202311 monthly timeChunked
  Zarr URL from pinned \`ocean_monthly_manifest.json\`.
- 8 actual breeding site codes taken from 13 source-backed ADPE-vs-other pairs.
- Frozen native \`ocean_grid_support.csv\` x/y cells selected **before** analysis, all within 25 km.
- Period 1993–2020, August–November monthly, surface layer ~0.494 m.
- Two original source variables: \`so\` (model surface salinity); \`thetao\` (potential temperature).
- Require **320 matched site-month rows from 2011–2020** to reproduce the frozen values
  with maximum absolute difference <=1e-5. Treat changed reanalysis source as a stop,
  not an unnoticed merge. Source input Git blob SHA values checked.

This extension does not imply independent observations of SST or salinity; GLORYS assimilates
observations and runs ocean dynamics. Counting year/month order cannot be inferred from
an annual nest-count label; the subsequent modeling must flag sites with unknown count month.

CI run and original CSV artifact are necessary before claiming source retrieval succeeded.
Do not convert climate exposure to future nest numbers without temporal and site-out
demographic validation.
