# Original Adélie breeding-census distribution × spatially shared satellite sea-ice fluctuations

**Observation-only macroecological follow-up.** Instead of assuming historical SIC change predicts
future penguin nest counts, compare how the same 30 years of observed coastal SIC are
aggregated under equal site-code weights vs original latest MAPPPD census counts.

Original 39 sites, August–November mean nearshore 0–100 km vs offshore 100–500 km
annual SIC over 1991–2020, source Git blob SHAs pinned. Original latest recorded ADPE
counts (2001–2025 and heterogeneous counting methods/units) produce a *descriptive*
weighting, not a single-year population state.

## Statistics

For original annual SIC X_{site,year}, compare sample SD over 30 annual observations
of a weighted average of the original *raw* percentage-point SIC. Separately, transform
each site's SIC to a standard score (remove that site's 30-year mean and divide by its
sample SD), and calculate the sample SD of the weighted average of these z-scores.
A larger normalized SD indicates more sharing of anomalous environmental fluctuations
across the count-weighted geographic allocation, not a greater realized ecological hazard.

Compare:
- all 39 original source codes equally weighted,
- latest original recorded census counts,
- counts from the same survey method as the site's original 1991–2020 trend analysis,
- fixed original regional proportions with source codes equal-weighted *within* each region,
- exclude two Cape Crozier source codes and re-normalize the remaining 37.

Detrend each source site's SIC with a fixed linear year function as a sensitivity.
As a purely *descriptive* geographic reference, permute the current count weights
among source codes **within each of the five predefined regions** 12,000 times with
a fixed seed. These shuffles do not represent an ecologically justified randomization
test, and the resulting fractions are not causal or population-level p-values.

## Controls and limits

The 39 sites are non-randomly selected with Victoria Land heavily represented by
both source sites and counts. Overlapping physical coastal windows create dependence;
39 entries are not 39 independently sampled climate shocks. Standardizing site variance
makes a hypothetical index; it does not turn physical SIC into bird recruitment,
survival, or the relative risk of colony contraction. Historical observed covariance
may not remain constant under SSP2-4.5 or SSP5-8.5 or under altered sea-ice dynamics.
Even perfectly computed spatial covariance cannot calibrate 2050/2100 nest counts.

All emitted annual portfolios, source sites, within-region shuffle references,
summary, and validation are stored as GitHub Actions artifacts. Source-pinned
expected numerical receipts are required to pass CI. Frozen Paper1/2 and main untouched.
