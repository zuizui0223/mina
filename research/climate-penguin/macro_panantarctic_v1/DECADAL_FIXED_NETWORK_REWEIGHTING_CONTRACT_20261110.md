# Decadal fixed-colony nest reweighting and sea-ice decomposition — pre-output contract v1 (2026-11-10)

This new exploratory lane begins from mina climate PR #206, not the frozen main Paper1/Paper2 analyses. Sources and estimands specified before opening these decadal outcomes.

## Original source and time windows
- Reconstruct 595 MAPPPD colony IDs, 18 regions, and 2,456 observed species×site×year method-fixed nest counts from source-hash-validated existing macro_panantarctic_v1/build.py.
- Reuse the completed OSI SAF original 25-km monthly 0–100-km coastal sea ice: 595 colonies × 1991–2020 × August–November = 71,400 site-month rows. Original verification Actions run 42612067836, artifact 13671496095. This is environmental exposure, not an individual foraging or dispersal route.
- Freeze decades 1991–2000, 2001–2010 and 2011–2020. Compare first→second, second→third, first→third. There is no 1980s climate source in this panel.
- One site must have a true observed census in both windows AND ten source-complete seasonal SIC annual means for each respective window. Never assign unreported species or survey-years zero. Actual recorded zeros stay zero.
- Within each site, species and window, use the median method-consistent recorded nest count to weight the fixed roster; use each decade's ten annual Aug–Nov SIC means for the site's environmental value. The count median is not a same-year continent census.

## Exact estimands and checks
Let paired observed sites be I, site median counts N_it, normalized weight w_it = N_it / sum_j N_jt, decade SIC S_it, and latitude lat_i. Require positive total weight both windows.
- Observed count-weighted latitude c_t = sum_i w_it * lat_i. Southward-positive reweighting distance D = (c_0 - c_1) * 111.195 km; standardize by decade midpoint separation (10 or 20 years).
- Experienced ice E_t = sum_i w_it * S_it percent.
- Symmetric physical effect C = sum_i [(w_i0+w_i1)/2]*(S_i1-S_i0).
- Symmetric nesting reweighting effect R = sum_i [(S_i0+S_i1)/2]*(w_i1-w_i0).
- Check exactly E_1-E_0 = C+R. If C<0 and R>0, R/(-C) describes observational offset fraction, NOT adaptive tracking or movement of individual penguins.
- Provide per-species and region-specific source support, 250-km block counts, paired-site sizes, number of repeated census years, maximum nest weight and effective site number, and leave-one-spatial-block-out range. The latter is a descriptive stability check, not a confidence interval or p-value.
- Regional results with fewer than three paired observed sites or zero total recorded nesting in either decade are flagged unsupported, not represented as ecological zeros.

## Non-identifiable here
- The geographic leading/trailing edge of true species range, local colonization/extinction, individual movements, and full Antarctic population centroid require consistent presence/absence/background survey effort. The identical paired site roster purposely excludes unmonitored regions and new observations; geographic displacement of its *weights* is not physical range displacement.
- Coast-aligned 60% SIC isopleth climate velocity cannot be calculated from colony buffer averages: original full marine grid and coastline contour/alongshore geometry are needed first. Do not invent a kilometer-per-decade climate front.
- Different colony methods have been fixed by the original source reconstruction, but sparse and non-synchronous original census years still prevent unbiased whole-continental abundance inference.
- Regional confounding, space dependence, and a species' different sea-ice niche prevent interpreting SIC exposure compensation as historical climate debt, physiological tolerance, causal warming effect, or any calibrated 2050/2100 prediction.
