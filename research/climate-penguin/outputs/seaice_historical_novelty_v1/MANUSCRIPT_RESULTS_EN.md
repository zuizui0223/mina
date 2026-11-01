# Results draft — Threshold-free multidecadal sea-ice novelty at sampled Adélie penguin breeding sites

## Question

Can source-matched CMIP6 future seasonal sea-ice climatologies move below the historical range observed at the same breeding sites **without** requiring a postulated demographic hazard cutoff of 60–80% SIC? Do sampling geography and unequal recorded breeding counts change the macroecological exposure summary?

## Original sources and time-scale-matched reference

We reconstructed 30 annual August–November coastal satellite sea-ice concentration (SIC) values (1991–2020) for each of 39 geographically biased Adélie penguin census site codes (1,170 site-years). Each site's observed multidecadal baseline was represented by 11 overlapping rolling 20-year climatologies (1991–2010 to 2001–2020). The median observed range of these *overlapping* climatologies was only **0.848 percentage points**. These windows are not independent draws or a statistical interval; future 20-year averages are classified as physically outside the sampled historical range if they are lower than the smallest rolling 20-year observed mean. We further assessed exceedance by 2 and 5 percentage points and alternative 10/15-year historical rolling-window minima.

Three source-matched CMIP6 models (ACCESS-CM2, BCC-CSM2-MR and CESM2) were delta-adjusted to the observed 1995–2014 seasonal sea-ice mean at each original site, for SSP2-4.5 and SSP5-8.5 in 2041–2060 and 2081–2100. The denominator for census-weighted summaries was the sum of the most recently recorded original MAPPPD counts at the 39 sites (1,074,279), which are not a temporally synchronized census or a single consistent unit of breeding population size.

## Physical exposure across scenarios

| Scenario | Period | Across-model share of census-count weight with future SIC below its historical 20-y lower bound | Share at source codes below the bound in all three models | Common 3-model share at least 2 pp below | Common 3-model share at least 5 pp below |
|---|---|---:|---:|---:|---:|
| SSP2-4.5 | 2041–2060 | 39.1–43.4% | 35.5% | 0.0% | 0.0% |
| SSP2-4.5 | 2081–2100 | 40.4–75.1% | 39.7% | 22.8% | 0.2% |
| SSP5-8.5 | 2041–2060 | 40.7–48.1% | 39.7% | 20.7% | 0.0% |
| SSP5-8.5 | 2081–2100 | **48.8–85.9%** | **39.7%** | **35.7%** | **22.8%** |

The magnitude of these percentages is sensitive to the narrow observed envelope and coarse coastal model grids. Importantly, even when a site remains above an illustrative 77.5% SIC level, its modeled future 20-year climatology can fall outside the range of its own observed historical 20-year means. Under SSP5-8.5 in 2081–2100, the model-specific fraction of present census weight meeting both conditions ranged from **12.4% to 59.5%**. Thus, not crossing a region-wide low-SIC threshold does **not** imply climatic stationarity.

## Cape Crozier and count-weighted geography

The two original Cape Crozier count codes together contributed 242,681 of the recorded counts (22.6%). Their lowest observed 20-year mean SIC values were **79.85% (CRZE)** and **80.39% (CRZW)**. The three model futures under SSP5-8.5 in 2081–2100 were **67.75–73.80%** and **68.30–74.35%**, respectively, placing both sites **6.05–12.09 percentage points** below their site-specific historical 20-year minima under all three models. This result avoids the unvalidated 77.5% hazard threshold; it establishes no demographic response. The two source codes do not represent independently replicated climate-model exposure cells.

**Count concentration behind the stricter climatological-novelty result.** The eight original site codes below their historical rolling 20-year minimum by **at least 5 percentage points in all three models** represented 245,092 latest recorded counts, or **22.815%** of the fixed 39-site census-weight denominator. Cape Crozier's two source codes alone supplied 242,681 of those recorded counts (**99.016%** of this strict-novelty count-weighted index). The other 37 study sites contributed only **2,411** counts (**0.224%** of the 39-site denominator) to the all-three-model strict-novelty subset. With the more permissive historical 20-year minimum criterion and no 5-pp margin, the intersection represented **425,953** recorded counts, of which Cape Crozier contributed **56.97%**, rather than 99%. Thus, multiple source sites can show projected historical SIC novelty while the apparently large **strict count-weighted climate exposure** can be almost wholly driven by one large breeding area. This is a fixed-current-census spatial weighting result, not predicted loss of 245,092 nesting pairs or a site-level biological treatment effect.

The study-region mean SIC change in SSP5-8.5 late century differed according to geographic weighting: **−6.54 to −11.19 percentage points** across the 39 site codes with equal site weights, versus **−1.68 to −4.05 percentage points** after weighting by their original latest recorded census counts. A high-SIC relative refugium can therefore still experience climate conditions beyond its own historical multidecadal envelope, while current census concentration near comparatively stable high-SIC areas reduces the count-weighted mean change compared with a simple site mean.

## Interpretation boundary and limitations

This is an alternative **physical exposure envelope**, not a validation or replacement of a biological cutoff. Historical 20-year climatologies are highly overlapping and the available 30-year period is short; the 2/5 percentage-point thresholds are transparent sensitivity margins, not inferred hazards or confidence bounds. The nested 10/15-year historical window and annual minimum comparisons use different temporal averaging lengths and are deliberately retained only as sensitivity checks. Site selection over-represents Victoria Land, sea-ice values share pixels, CMIP6 coastal cells are coarse, and each of the three models contributes only one realization. Census weights refer to different survey years (2001–2025) and incompatible count methods/targets. Neither future Adélie population decline, occupancy, breeding failure, competition, salinity response nor vegetation change is projected.

## Figures

**Main**: (A) empirical distribution of historical site-specific 20-year SIC lower bounds and current census-count weight; (B) model-specific 2041–2060 / 2081–2100 site-weighted versus latest-record-count-weighted physical SIC changes; (C) scenario sensitivity with three-model ranges for physical novelty beyond historical 20-y minimum, then 2 pp and 5 pp, alongside the common three-model intersection. Distinguish the present-census exposure index from a numerical forecast of future colony size.

**Supplement**: source 39×30 annual SIC; 11/16/21 historical rolling windows for 20/15/10 years; full 936 site×scenario×baseline×model climate values; native CMIP6 grid IDs and distances; exact model-overlap site sets, observed latest count method/year, and comparison with the exploratory hypothetical 60–80% boundary.

**Reproducible sources**: [GitHub Actions source-verified successful run](https://github.com/zuizui0223/mina/actions/runs/41261450601), artifact ID 13064883160; original code: \`research/climate-penguin/work/seaice_historical_novelty_v1/build.mjs\`.


## Three-species observation-geography extension (supplementary, original source-verified)

The fixed original long-term source contains **54 site-by-species series** across the same **39 distinct geographic breeding-site codes**: 39 Adélie, 7 chinstrap and 8 gentoo series. This is **not 54 independent climatic sites**, and the last two species are sampled only within South Shetland Islands and the central-western Antarctic Peninsula.

Applying the identical source-pinned historical rolling 20-year SIC range and CMIP6 SSP5-8.5 late-century physical exposures to the *original long-term breeding locations*, the observed site-code counts with future SIC below their local historical multidecadal minima were:

| Species | Original site codes | ACCESS-CM2 | BCC-CSM2-MR | CESM2 | Same original site codes in all 3 models |
|---|---:|---:|---:|---:|---:|
| Adélie | 39 | 28 | 24 | 25 | **15** |
| Chinstrap | 7 | 3 | 6 | 7 | **2** |
| Gentoo | 8 | 4 | 8 | 8 | **4** |

Under the stricter **5-percentage-point** margin, all-model-common counts were **8/39**, **2/7** and **4/8**, respectively. These are source-backed **geographical sample supports** for exposure, *not* the species-wide fraction of occupied colonies and not comparative physiological climate sensitivity or demographic forecasting. Multiple species at the same location reuse identical satellite SIC and the same CMIP6 cell; apparent differences arise from the small, geographically biased species-site samples. Historical annual census series are not a consistent site-independent measure of future nesting abundance.

[Verified original source replay and archived site×species rows](https://github.com/zuizui0223/mina/actions/runs/41261833552), artifact 13065143256. Preserve as supplementary geographic context, not an independent replication of the main 39-site Adélie result.


## Observed disjoint-decade physical-change sensitivity (1 November 2026)

To evaluate whether threshold-free coastal sea-ice novelty was driven by the narrow range of 11 highly overlapping historical 20-year climatologies, we reconstructed **three disjoint 10-year observed SIC means at each of the 39 original Adélie census sites** (1991–2000, 2001–2010, 2011–2020). The median site-specific maximum *downward change between adjacent historical 10-year averages* was **1.494 percentage points**.

Under SSP5-8.5 in 2081–2100, all three CMIP6 models projected SIC mean declines from the observed 1995–2014 baseline exceeding each site's largest recorded historical downward decadal step at **13/39 sites**, representing **35.68%** of the fixed, noncontemporaneous current census count weight. When the modeled reduction was required to exceed the historical step by an additional 2 or 5 percentage points, the common subsets decreased to **10 sites / 27.21%** and **8 sites / 22.81%**, respectively. As an independent conservative indicator, the future mean being 5 points below all three observed disjoint-decade means also identified **8 sites / 22.81%**.

At Cape Crozier, the largest measured adjacent-decade drops were only 0.173 and 0.244 percentage points for two census codes, compared with model-based late-century declines of about 6–12 points. Together, these two codes contributed **99.016% of current census counts** in the strict 8-site model-common subset. This is not biological mortality, population decline, or a random geographic risk test.

**Limitation:** the historical steps compare two 10-year means while modeled changes refer to future 20-year mean conditions. Neither the averaging scale nor time gap is identical, and only two original historical transitions are available per colony. It is a physical-magnitude sensitivity test, not a statistical return-period estimate or a calibrated ecological threshold.

[Original method and results](../seaice_nonoverlap_decade_v1/REPORT_JA.md) · [source-verification CI](https://github.com/zuizui0223/mina/actions/runs/41274472286).
