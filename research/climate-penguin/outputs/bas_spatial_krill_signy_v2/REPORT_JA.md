# Signy island 2011–2020 krill GAM spatial surfaces: source-verified distance bands

Source: Freer et al. (2025), [BAS UK Polar Data Centre DOI 10.5285/4fd0a1bf-da1a-4021-82eb-2fc513910e32](https://doi.org/10.5285/4fd0a1bf-da1a-4021-82eb-2fc513910e32). Annual source ZIP is verified by original SHA256 (in the script) and the previous source-only gate. Actual 56 GeoTIFFs include 50 annual and 6 decadal products, in EPSG:4326, native **0.083333°** output pixels. Previous Freer 2025 already fitted a hurdle GAM to regional acoustic records and environmental variables; **these predictions are NOT independent acoustic observations**, and since the model includes salinity and ice they cannot independently validate a salinity or sea-ice mechanism.

Fixed native BAS spatial source: 14 previously validated Adélie and Chinstrap GPS **colony reference points**; take latitude/longitude midpoint of all native point bounding box. This is a shared island-area proxy, NOT an actual gentoo nest, penguin landing point, or measured foraging trajectory. Select the same three fixed distance rings before fitting any species effect: 0–50, 50–100, 100–150 km. Extract and retain all annual source binomial probability, conditional Gaussian density, and probability-weighted combined density; average source-valid cells with cosine-latitude cell-area weights. Preserve the original model mask without inventing marine coast classification; all nine series, plus 2013/2015 incomplete-survey exclusion and postresult 2012 sensitivity.

Annual source field Jan–Feb T aligned to BAS stage in season T (Oct T–Feb T+1) without future data. For each species, there are **nine environmental year opportunities**, not 27 independent ocean measurements; all correlations are *post hoc*. Any association could reflect the existing krill GAM's environmental assumptions, lack of independently verified marine space, field weather/ice coverage, temporal lag mismatch, or non-independence of several stages. No climate→future nesting population, N_eff or vegetation causal effect is estimated. The release gate remains NO-GO.

Reproduce via original ZIP and script \`research/climate-penguin/work/climate_penguin/bas_spatial_krill_signy_v2.py\`. This analysis leaves PR189 and PR199 frozen.


## Native TIFF content digest correction, 2026-10-30

RAMADDA regenerates ZIP archives; the container SHA varies across downloads. The full content of the 30 native year-specific TIFFs (2011–2020, three mean products per year) is instead SHA256-verified by iteratively updating the digest with \`basename + NUL + original TIFF bytes\` in year/product order. The frozen payload hash is **\`f4fffbc2b0cbe2dffc5a5728c81f1b46ba9ff99988c6589bb3515d38d2a2fead\`**. The original zip wrapper's hash is recorded but not used as a false drift failure. Any changed native TIFF content is rejected.


## 2026-10-30 numerical outcome (executed, source-pinned)

[GitHub Actions #41067871772](https://github.com/zuizui0223/mina/actions/runs/41067871772): **SUCCESS**. Original BAS raster TIFF byte payloads independently pinned (SHA256 \`f4fffbc2b0cbe2dffc5a5728c81f1b46ba9ff99988c6589bb3515d38d2a2fead\`) despite re-generated ZIP wrapper SHA variability. Five tests passed. Output: **90 annual×model-product×distance records** from 2011–2020 (3 products × 3 fixed geographic distance rings × 10 years). Native EPSG:4326 grid 0.083333° with geometry 121×241 pixels. Shared source-verified Signy 14 colony-reference-point bounding-box midpoint **−60.704025, −45.6275835**, not a measured foraging location.

**Source-predicted probability-weighted krill density**, Pearson r against the same nine observed BAS source breeding seasons' pre-fledging output:

| Geographic proxy | All nine years: Adelie / Chinstrap / Gentoo | Seven source-complete acoustic survey years | Six years after additionally omitting 2012 (posthoc) |
|---|---|---|---|
| 0–50 km | **+0.226 / −0.115 / −0.239** | +0.016 / −0.513 / −0.535 | +0.566 / +0.597 / +0.215 |
| 50–100 km | **+0.167 / −0.112 / −0.259** | +0.033 / −0.528 / −0.592 | +0.706 / +0.802 / +0.204 |
| 100–150 km | **+0.012 / −0.326 / −0.387** | −0.190 / −0.784 / −0.705 | +0.897 / +0.752 / +0.541 |

**This does NOT establish a positive effect by excluding 2012.** The six-year sensitivity was done after observing influential-year behavior in the independent 60,000km² published acoustic index. It is reported to expose instability. The actual n=9 primary is weak/heterogeneous, and source 2013/2015 reduced survey footprint changes the 7-year cohort; no spatial radius can be selected after outcomes. The 2012 high-krill/low-fledgling mismatch remains present in the near-island modelled field. Positive n=6 coefficients cannot be interpreted as a calibrated food limitation or island accessibility mechanism.

Source cell support across years: 0–50 km ~175 original valid predicted-model cells, 50–100 km ~570, 100–150 km ~929; these are **correlated pixels from one fitted model**, not independent samples. Annual values vary with environmental model inputs and the underlying original acoustic data. Raster masks are publisher model-valid, not an independent marine-only coastline mask. The spatial test is *not* independent corroboration of the earlier IMR biomass survey because both incorporate the same acoustic series.

No fitted future CMIP6→krill→fledgling→nest count transfer, nor dynamic habitat/vegetation response, is licensed by these results. Existing frozen Paper1 and Paper2 unchanged.


**Source-provenance note (2026-10-30):** Previous `imr_south_orkney_krill_v1` stage correlations were based on a conflicting 2024 report year table. The raster-based 0–50/50–100/100–150 km GAM predictions and their stage correlations use the original publisher TIFFs, NOT the erroneous IMR numeric sequence; they are unaffected numerically. The legacy input in this band's code was used **only** for full/reduced survey coverage flags, not krill-density numbers. Nonetheless, those acoustic comparisons remain non-independent of the same underlying IMR survey. [Reconciliation](../south_orkney_source_reconciliation_v2/REPORT_JA.md).
