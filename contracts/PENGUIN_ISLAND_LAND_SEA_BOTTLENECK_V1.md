# Antarctic penguin island macroecology — hypothesis + outcome-blind data contract v1

**Date:** 2026-10-18. **Repo:** `zuizui0223/mina`; completely separate from frozen *Ecology* manuscript PR #189. **Status:** independent APBP data have NOT been downloaded, parsed for numerical outcomes, or modelled on this branch before this specification was committed.

## Question with a uniquely Antarctic, island-specific mechanism

**Does the finite availability of suitable land nesting substrate modify the response of island-breeding penguins to marine sea-ice/access fluctuations, and does that relationship depend on nesting substrate ecology?**

Provisional title: **Two spatial bottlenecks in Antarctic penguin breeding: island nesting substrate × marine access**.

Hypothesis is explicitly a *proposed* effect, not supported empirical result: **the same marine anomaly may cause different breeding population trajectories where terrestrial ice-free habitat is scarce versus abundant**. A large *island land area* is not equivalent to accessible *ice-free rock within a suitable coastal nesting zone*. Antarctic peninsulas and ice-covered high-latitude islands are not assumed equivalent to low-altitude rocky islands.

### Opposing falsifiable hypotheses (to evaluate AFTER source QA)

- **H0, marine/climate-only:** After regional-year effects, location, pre-period population size, site-specific trajectories and observation protocol/quality are accounted for, available terrestrial nesting habitat does not modify colony-level marine anomaly response (`beta_nesting_area_x_marine_anomaly = 0`).
- **H1, dual land–sea constraint:** Among repeatedly sampled terrestrial-nesting penguin colonies, objectively mapped ice-free coastal rock area moderates the impact of anomalous marine access (sea ice / distance to polynyas / offshore open water). Prespecified direction: colonies with more accessible bare-rock nesting opportunity are **less sensitive to adverse marine-access anomalies**; effect is evaluated within marine-climate regions, not from unadjusted latitude gradients. The sign may fail and must not be rescued by choosing a different distance/metric after results.
- **H2, guild-specific bottleneck contrast:** Emperor penguins generally nest on sea ice and land-nesting Adélie/chinstrap/gentoo use mostly terrestrial ice-free coastal surfaces; any apparent positive area-buffering interaction should be weaker or absent for the emperor *where geographic/environmental overlap and comparable survey records exist*. Not a strict negative control if overlap is inadequate; some Adélie may nest on fast ice. Macaroni/king are included in source QA but fitted only where count/year support is sufficient.
- **H3, geographic island interaction:** To call a land-capacity interaction *island biogeography*, distinguish mapped standalone islands from contiguous continental mainland/peninsula coasts at matched latitude, broad marine environment and observation history. The `island x nesting capacity x adverse marine anomaly` effect is the island-specific estimand; a general peninsula-wide response alone is **not** evidence for island exceptionalism.

These contrasts build on, and do not rediscover, known uneven metapopulation recovery, penguin colony geography (Santora et al. 2020 DOI 10.1111/geb.13144), site fidelity (Matthiopoulos et al. 2005 DOI 10.1111/j.1365-2656.2005.00970.x), Beaufort nesting land release and resightings (LaRue et al. 2013 DOI 10.1371/journal.pone.0060568), or annual regional forcing (Che-Castaldo et al. 2017 DOI 10.1038/s41467-017-00890-0). **Novelty is unconfirmed** until a systematic literature check of identical interaction designs.

## Primary original public DATABASES (direct source, not manually extracted figures)

1. **APBP / SCAR–AntOBIS version 2.3**, stable Darwin Core Archive, 2023, DOI **10.48361/zftxkr**; GBIF key `f7c30fac-cf80-471f-8343-4ec5d8594661`; official `https://ipt.biodiversity.aq/archive.do?r=mapppd_count_data&v=2.3`. Source reports **4,055 Event core**, **4,768 Occurrence** and **4,750 ExtendedMeasurementOrFact** rows from 1892 through February 2022, six named penguin species. Attribution CC BY 4.0. Download through original official publisher, archive actual ZIP SHA and `meta.xml` schema. Treat as the initially *pinned* population source. Never infer nest count from an occurrence record without a verifiable nest-count unit and linkage.
2. **MAPPPD v4.4 live portal** `https://penguinmap.com/mapppd/`, as of 2026-10-18 advertises count releases through 2024/25 for 4 species. Obtain only a publicly identified exact bulk count export and archive its version/hash; this is a *future temporal update/holdout*, **not** retroactively substituted for APBP v2.3 in the primary analysis.
3. **SCAR Antarctic Digital Database (ADD)**, rock outcrops and coastline polygons `https://data.bas.ac.uk/items/e74543c0-4c4e-4b41-aa33-5bb2f67df389/`, as of 2026 edition 21. Use shapefile/GeoPackage with original version, polygon source and CRS. Island class is derived by georeferenced land connectivity, not by whether a site name contains the word "Island". Spatially ambiguous islets/connected islands excluded or sensitivity stratified. Contemporary ADD rock is a **static habitat indicator**, not historical ice-free land change in the 1980s; do not call it observed capacity increase.
4. **NOAA/NSIDC sea ice CDR G02202 v6**, DOI **10.7265/b18j-z797**, annual/monthly 25-km polar stereographic series 1978–present. Differentiate land/shoreline spillover from offshore concentration; compute marine-access anomalies in predeclared near/offshore annuli and independently chosen breeding season windows; do not assume an ice raster pixel over colony land measures feeding access. Anomaly baseline and site-year units require documented resolution and date.
5. **Optional confounder sources later**, only if archived: ERA5 temperature, snowfall, MODIS chlorophyll, coastal polynya area, benthic submarine canyon/bathymetry, krill fishing, HPAI occurrence, annual survey method/effort; no uncontrolled covariate fishing or arbitrary PCA after outcomes.

## Exact first-stage stop rules, before modelling

A. Stage 1 downloads only **one** APBP v2.3 original DWCA archive, stores full original `sha256` and file list, `meta.xml` declared row/link schema, empirical original row counts, column names and strictly labelled counts of **eligible** species/site/year/measurement records. Source date/vantage and quality metadata must be preserved with each record; sites versus whole islands must remain separate IDs.

B. **Never treat absence of a count as zero**, or interpret absence from the APBP known-site database as unoccupied suitable terrestrial nesting ground. Preserve duplicate event sources and count types. Nest counts, adult counts and chick counts are different estimands. Main longitudinal endpoint is observed breeding pairs/nests at comparable site/year, not adult survival, recruitment, community takeover or dispersal.

C. Eligibility for candidate temporal trajectories must require exact site ID, species, comparable nest/breeding-pair type, distinct survey years; label confidence from original quality metadata (N1–N5); do not automatically select whichever duplicate count increases effect significance. Prespecify two strategies: one observation per site/year/type prioritizing strict measured accuracy and date; or explicit observation-error model retaining replicated surveys. Both logged and sensitivity checked. One-day observation timing can systematically bias breeding count by species.

D. If the version-locked source is unreachable, returns HTML rather than zip, has missing declared relational keys, or lacks reliable nest count labels, mark `HOLD_SOURCE_OR_MEASUREMENT`. Do not invent availability, assume the user can authenticate elsewhere, or quietly replace the source. Dataset update version is NOT a priori chosen based on favorable estimated effects.

E. Climatic exposure and island polygon linkage must be independently verified. Stage 1 NEVER computes a positive ecological slope, climate × habitat effect, species difference, p-value or causal claim. Only after the island/habitat/marine matched data assembly is complete will the model be fitted.

## Stage 2 estimand — once data support and quality gates are open

Let colony-site `i` for species `s` in breeding year `t` have true breeding nests `N_ist`. Site-by-year observed counts `y_ist` have survey-specific method and N1–N5 precision measurement model. Let `R_i` be *independently* measured coastal ice-free rock availability, `A_i` island versus mainland class, and `M_it` the mean-centered anomaly of offshore ice/foraging access.

Fit a hierarchical latent site log-abundance growth:
`g_ist = log N_i,s,t - log N_i,s,t-1`, **only where sequential site-year support exists**; for irregularly spaced counts, use an annual latent state-space model rather than naively dividing log growth by elapsed years or treating missing years as zero.
`g_ist = alpha_{s,region,t} + beta_s M_it + gamma_s M_it × log(1+R_i) + delta_s M_it × log(1+R_i) × A_i + site_i + error_it`, with environmental nuisance effects and survey error. The `delta` term tests an island-specific expression of habitat buffering beyond ordinary climate sensitivity. Do not pretend `gamma`/ `delta` identify anthropogenic rock exposure or individual migration. Spatially blocked regional holdouts, leave-one-island-cluster-out tests and leave-one-publisher-source-out robust checks protect against pseudoreplication.

**Crucial counterfactual:** To support a *substrate bottleneck*, show the interaction explains out-of-sample growth differences beyond a marine-only model **and** survives matched comparable coast/latitude, nonland-nesting guild checks, and observation quality corrections. Without independent time-varying rock exposure this remains a conditional spatial effect modification, **not proof that new nesting habitat caused changes**. Map land connectivity, distinct site structure and 25-km sea-ice grids must be checked before analysis.

## Time and isolation safeguards

- Single frozen Ecology PR189 scientific source stays untouched; the current branch is an independent macroecological study.
- APBP covers known surveyed colonies; event count is **not** 4,055 independent island populations or 4,055 colonizations.
- There is no source-backed claim yet about the number of island species, how many repeated nest histories exist, or sign/significance of any association.
- All data license attribution and third-party original event citations preserved; no first-party creation of the publisher's data claimed.
