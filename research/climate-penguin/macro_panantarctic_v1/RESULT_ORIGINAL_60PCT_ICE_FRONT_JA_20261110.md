# 南極3種の繁殖巣数再配分と実衛星60%海氷等値線の南北移動 — 原本検証結果

**2026-11-10｜Draft PR #214｜source-backed observational macroecology, not causal attribution or a climate-debt inference.**
Original full-grid success: https://github.com/zuizui0223/mina/actions/runs/42791019321 (full-grid source SHA and 36-sector/strict colony-pair result). Physical sector CSV/JSON in workflow artifacts ID 13751339305 / 13751339300.

## 新しい発見（同じ物差しではないが、同じ年代で二つの地理構造が測れた）

**1991–2000 → 2011–2020:** Original EUMETSAT OSI SAF v3.1 sea-ice concentration 60%-isoline **meridional** displacement, 36 geographically fixed 10° longitudinal sectors: **17 southward, 19 northward**, spatial-sector median **−7.258 km over 20 years** (positive = poleward), range **−72.670 to +46.185 km**. The September-only fixed sensitivity: 17 southward / 19 northward; median **−3.352 km** (range **−104.612 to +56.900 km**). These longitude sectors share adjacent marine ice fields, and the median is not a population-weighted climate velocity or coast-parallel route length.

The **fixed same-colony** observed breeding-count weighted latitudinal centroid shifted **+88.411 km** among strict 26 Adélie sites (≥2 observed original census years in each decade). The 60% marine isocontour's meridional displacement averaged across the same sites' five longitude sectors, with **early recorded nest counts as weights**, was **+29.671 km**. For chinstrap strict 12 sites (two sectors), nesting reweighting **+6.065 km** vs sector-supported physical **−2.691 km**. For gentoo strict 12 sites (two sectors), nesting reweighting **+1.021 km** vs physical **−4.640 km**. All three strict site rosters obtained physical sector support, but the latter two species sample only two 10° sectors and two original regions each.

**Do NOT interpret the arithmetic differences as a measure of whether the species is 'ahead of' or 'behind' climate.** Count-weighted latitude shifts redistribute weights among historically observed land nesting sites. Marine 60% ice isocontour shifts are offshore physical gradients, neither verified preferred penguin nesting/foraging niches nor coastline-following climate velocities. No individual migration, settlement, biological ice threshold, true distribution boundary, or climate debt was estimated.

## Source-independent achievement and code repair record

- Source 120 original 25km monthly EASE2 NetCDF files (1991–2020, August–November) from the official THREDDS host. Every SHA256 exactly matched the earlier completed 595-site original-source receipt, action https://github.com/zuizui0223/mina/actions/runs/42612067836. Original reference marine mask frozen at 1993-09 per original source atlas. The two decade fields have **153,319 jointly source-valid marine EASE2 pixels**.
- Independently re-aggregated the exact original native 1993-09 ocean-cell pixel IDs at all **595/595 colony source sites**. Source original 100km buffer site SIC means match to **maximum absolute difference 0.000000 pp**. No changed climate source or pixel membership was introduced.
- First full-grid workflow https://github.com/zuizui0223/mina/actions/runs/42790192231 obtained 1 large connected ~995–1025-vertex 60% isoline component spanning all **36/36** longitude sectors in each decade and in both Aug-Nov and September. It nonetheless rejected every component because a later-added code check demanded a mathematically closed polygon, even though the frozen contract required a long **connected** original marine contour spanning >=24 sectors, not a perfectly closed ring.
- Frozen-output geometry diagnosis https://github.com/zuizui0223/mina/actions/runs/42790802452 isolated this inconsistency **before examining physical or biological movement scores**; acceptance was corrected by removing only this extraneous closure test. The threshold 60%, original source SHAs, strict native ocean mask, 36x10° sector definition, colony source roster, Aug-Nov primary and September secondary, and decadal dates were unchanged. The rectified source + unit test workflow #42791019321 succeeded.
- Physical indicator is the median latitude of the largest geographically continuous native marine isocontour in each 10° sector. Interpolated longitude uses circular sin/cos to avoid longitude seam artifacts. This is a true original 2D sea-ice contour, **not** a 595-colony-site-only interpolation. It does **not** implement SCAR ADD coastal contour traversal or an individual foraging location.

## Three decade-pair marine-front results (all 36 10° sectors)

| Years | Aug–Nov southward / northward sectors | Aug–Nov median southward km over interval | Full-sector range km | September-only median km |
|---|---:|---:|---:|---:|
| 1991–2000 → 2001–2010 | 23 / 13 | +5.553 | −127.036 to +116.244 | +11.426 |
| 2001–2010 → 2011–2020 | 20 / 16 | +4.272 | −98.667 to +88.515 | −10.436 |
| 1991–2000 → 2011–2020 | 17 / 19 | **−7.258** | **−72.670 to +46.185** | **−3.352** |

This is **not** a monotonic circumpolar poleward movement through all periods. The median across sectors is a nonlinear summary and need not add across consecutive decade pairs, even when sector-year fields are physically comparable. Geographic season/sector directions vary; the physical pattern cannot be used as a uniform temperature-driven pressure to which the species must necessarily respond.

## Species-strict 1990s → 2010s overlap (two or more original count years at each endpoint)

| Species | Original paired sites | Regions | 250km blocks | 10° marine sectors | Nest-weighted latitude shift, km | 60% front meridional change weighted by early nest counts, km |
|---|---:|---:|---:|---:|---:|---:|
| Adélie | 26 | 4 | 7 | 5 | **+88.411** | **+29.671** |
| Chinstrap | 12 | 2 | 3 | 2 | +6.065 | −2.691 |
| Gentoo | 12 | 2 | 4 | 2 | +1.021 | −4.640 |

- In the strict Adélie source cohort the largest sampled site carries **48.759%** of early nest-count weight and **43.148%** of late weight; therefore the count-weighted Antarctic-wide network centroid is highly nonuniform and cannot be called a representative species-range centroid.
- Previous fixed-site PR #214 v1 result: Adélie +88.411 km within 26 repeated-census sites, leave-one-250km-block-out **+38.885 to +125.826 km**, leave-one-original-region-out **+65.609 to +102.815 km**. These are diagnostic ranges, not a spatial bootstrap confidence interval or unbiased continent-wide displacement.
- Previous explicit region decomposition: among Adélie strict sites, +88.411 km = **between-source-regions +32.843 km + within-source-region sites +55.568 km**. Observed site abundance changes occur at more than one spatial grain; this does not establish range advance, fitness or dispersal.
- The strict source counts are historic median nest counts in each decade, **not** simultaneous total breeding individuals. The 595-site original MAPPPD atlas is known breeding-site records, not standard-effort absence across all Antarctica. Missing original site-year and species records cannot create occupancy/range extension or extinction.

## Ecological synthesis and next relevant evidence

**Supported by original data:**
1. Across a geographically very broad 25km original marine satellite grid, the illustrative 60% SIC isoline has **opposite meridional movement directions among longitude sectors**, so a single 'Antarctic sea-ice environment moves south' speed is not a robust descriptor for 1990s–2010s.
2. Observed same-colony Adélie nesting abundance was redistributed southward among the **fixed 26-site monitored network**; this is largely distinct from what the uncalibrated marine 60% isoline alone describes.
3. Independent species ecology, coastal source geography and survey temporal support matter: the 12 chinstrap and 12 gentoo strict sites each occupy only two source longitude sectors, so no pan-Antarctic movement rule follows.

**Not supported:** southern range-edge shift, true colonization and vacancy, 'Adélie follows/gets ahead of climate', fish/diet niche transition across Antarctica, causal warming exposure-to-demography coefficient, sea-ice front coast-parallel speed, 2050/2100 biological distribution forecasts.

A real coast-parallel isocontour measure requires explicit Antarctic coastline / marine accessibility topology, and a species distribution tracking test requires occupancy and effort or validated comparable site coverage in both eras, not only colony positives. Leave physical and biological quantities as distinguishable panels in the working macro paper. No post-result threshold optimization.

## Provenance

- Source and endpoint contract: ICE_EDGE_GRIDDED_SOURCE_CONTRACT_20261110.md.
- Exact full-grid original physical source code: compute_original_60pct_marine_front.py.
- Unit tests: test_original_60pct_marine_front.py.
- Data provenance geometry diagnosis: inspect_60pct_source_geometry.py.
- Cohort and strict census source: analyze_decadal_fixed_network_reweighting.py and DECADAL_REWEIGHTING_RESULT_JA_20261110.md in the same PR.
- Full source CI: https://github.com/zuizui0223/mina/actions/runs/42791019321 (success); artifacts 13751339300, 13751339305.
- Official data attribution: EUMETSAT OSI SAF, Global sea ice concentration climate data record 1978–2020 (v3.1, 2025), doi:10.15770/EUM_SAF_OSI_0023, CC BY 4.0.
- The existing main/paper 1/paper 2 and older manuscript v0.6 are unchanged; these results remain separate exploratory macro analysis within Draft PR #214.
