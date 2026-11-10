# Region independence and same-sector physical–biological mismatch diagnostic (2026-11-11 JST)

Follow-on **post-result diagnostic**, not prospective preregistration. The single primary lead-lag test is already frozen in FROZEN_THREE_DECADE_CLIMATE_LEGACY_GATE_20261111.md. This check interprets geographical support and the alternative physical/biological phase mismatch; it does not change exposure windows, sea-ice threshold, or cherry-pick regions.

Source archive only:
- Previous 3-decade original site×species roster and outcome (successful original-run 42844104869, artifact 13776484021); exact same 19 ADPE / 12 CHPE / 12 GEPE sites, >=2 real census years every 1991–2000, 2001–2010, 2011–2020 decade. No missing counts converted to true zeros.
- Original EUMETSAT gridded 60%-SIC physical front 10-degree sectors, Aug-Nov primary and September sensitivity (successful run 42791019321, artifact 13751339305). Do not download 120 original climate files again.
- Original fixed regions, colony longitude sectors and original 250-km blocks maintained as supplied; no novel population or geographic source.

### 1. Why an earlier climate correlation appears in pooled region-demeaned site means
For three fixed comparisons (preceding SIC to later nest change, concurrent SIC to later nest change, and impossible future SIC to earlier nest change):
- List each species×original source region with n observed sites (singleton explicitly noninformative).
- For n>=3, report **within-region**, equal-site Pearson r and slope in log1p median nests per +10 SIC percentage points; for n==2 output covariance and standardized sign only, never infer "region r" as if n=2 independent replicates; for n==1 no correlation.
- Compute each region's numerator sum of (site SIC change – regional mean) × (site nest log change – regional mean). Its share of the pooled region-demeaned numerator can be negative or greater than 100%; it is **not** a causal fractional attribution.
- For each species require >=3 original regions with >=3 sites apiece, >=5 independent 250-km blocks and stable sign under each leave-one-region-out on the frozen earlier-period comparison for even a *candidate geographically transferable* time-memory signature. Otherwise label GEOGRAPHY_UNSTABLE_OR_UNDERPOWERED. A regional correlation of n=2 is not independent empirical replication.

### 2. Like-for-like geographical comparison without inventing actual individual movement
- On the SAME three-decade site roster, partition source colonies into their original fixed 10-degree longitude sectors.
- Within a sector with >=2 actually surveyed colony sites and positive combined recorded decade-median nest count in each of the two periods, compute the **southward latitudinal shift of colony nest weights normalized within this sector** (one source method, identical site roster; not a true distribution edge).
- Join the sector's ORIGINAL source-gridded 60% sea-ice isoline latitudinal shift over the same chronological transition (1990s→2000s and 2000s→2010s). Report two signed km values per sector, raw arithmetic difference, and sign agreement only when both magnitudes exceed a prechosen 1km numerical descriptive tolerance; below that mark direction indeterminate rather than inventing perfect concordance.
- To even describe cross-sector trend agreement as a pooled result require >=5 informative nonidentical 10-degree sectors across >=3 source regions for each species; otherwise label NO_MACRO_SECTOR_REPLICATION and present raw geographic cases only. Sectors/colonies are spatially autocorrelated, not true replicates. Do not interpret the marine 60% front as breeding/future climate preference, and do not call the difference "climate debt" or "lag distance".
- Do not fit regression p-values, new thresholds, reference years or temperature dependence. Stop after reporting supported sector counts and regional influence.

Goal: decide whether the original +0.480 earlier climate relation and apparent population vs physical-front phase differences represent a replicated multi-region signature, or a geography-dependent descriptive mismatch. An unsupported outcome is informative and does not negate the robust descriptive original colony weight shift.
