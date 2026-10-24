# mina

Research program for **penguin breeding-island ecology**, linking a local
long-term discovery system at Palmer Station to Antarctic-wide comparative
macroecology.

## Research program

### Paper 1 — replicated breeding-space contraction

The current submission line is an **Ecology Report**:

**Breeding-space contraction recurs across declining Adélie and chinstrap penguins**

The paper asks whether declining colonial populations merely thin in fixed
proportion across monitored breeding components, or whether relative breeding
composition changes beyond the finite-count and observation-error consequences
of lower abundance.

Evidence is ordered as:

1. **Palmer Adélie discovery:** three stable-roster island populations;
2. **Signy Adélie prospective geographic replication:** frozen before the
   concentration effect was computed;
3. **Signy chinstrap prospective cross-species replication:** separately frozen
   before effect computation.

Across the five population units, effective monitored breeding-component number
declines by **19–83%**. The two prospectively frozen Signy tests remain extreme
under the most severe prespecified 20% multiplicative-CV sensitivity
(Adélie **p = 0.000010**; chinstrap **p = 0.000020**).

The broad abundance–space principle is not claimed as new. The paper's novelty
is the **within-colony fixed-composition count-error test of excess breeding-
component concentration**, followed by prospective geographic and cross-species
replication.

Canonical submission manifest:
`submission/ECOLOGY_REPORT_SUBMISSION_MANIFEST_V1.md`.

### Paper 2 lane — Antarctic-wide breeding-island macroecology

**V38 METHOD CORRECTION (2026-10-24):** APBP source
coordinateUncertaintyInMeters for Adélie colonies is calculated from
mean colony-polygon-vertex-to-centre distance, NOT a reported GPS
measurement-error radius. V38's 14 >250m records therefore cannot
establish 14 imprecise field GPS points; the independent-GPS precision
claim remains HOLD, while SCAR V39 confirms four categorical island
names. Frozen old V38 test/receipt is preserved.
- [V38 repaired original coordinate-metric interpretation](docs/NZ_ROSS_APBP_EXACT_GEOREF_V38_RESULT.md)

**V39 SCAR categorical LANDMASS IDENTITY resolved (post-V37/38):**
Four publisher-original named island groups **Ross / Beaufort / Coulman /
Inexpressible** are independently classified "Island (5)" in the official
SCAR Composite Gazetteer (four distinct authenticated national gazetteer
record IDs). The original colony-site names and 13 concurrent annual
windows remain unchanged. This supports the NOMINAL existence of four
separate islands without promoting original ±1-arcminute colony site
coordinates into accurate mapped nesting positions. V37/38 actual
high-resolution point-location sensitivity remains FAILED. Island
biological r's, the 61.5% same-direction V36 description, and causation
limits remain unchanged.
- [V39 official SCAR island name ID vs nest GPS evidence](docs/NZ_ROSS_SEA_SCAR_CGA_ISLAND_IDENTITY_V39_RESULT.md)
- [V39 four authenticated original gazetteer name SHA receipts](results/NZ_ROSS_SEA_SCAR_CGA_FOUR_ISLAND_IDENTITIES_V39.json)

**V38 NEW MAPPPD v5 original published locality API (21 Oct 2026):** 10
pre-fixed V35 Ross Sea colonies match source MAPPPD v5 site IDs (7 exact
names and 3 abbreviated Coulman names). Independent published WGS84
site *centers* vs original 17,269-polygon highres SCAR source leave
**2 islands with >=5 consecutive source years and 5 shared distinct
island windows** under exact source names/center-contained land.
Beaufort API georeference is offshore but within 2 km; Coulman site
abbreviations are not independent identity proof. Full hypothetical
250m/1000m disk containment gives 0 supported multi-island windows.
Data supplier/source location DOES NOT independently establish field GPS
accuracy; V36 geographic robust inference stays HOLD. Original V36
animal outcomes not re-fitted or reselected.
- [V38 second-source site location and SCAR result](docs/NZ_ROSS_SEA_MAPPPD_V5_GEO_SOURCE_V38_RESULT.md)
- [V38 original JSON location/metadata crosswalk](results/NZ_ROSS_SEA_MAPPPD_V5_GEO_SOURCE_QA_V38.json)

**2026-10-24 V38 independent APBP geography also FAILS as GPS repair:**
The original 2023 APBP/AntOBIS Darwin Core v2.3 4,055 Event rows/719
locationIDs were source-SHA verified. Only **21/33** NZ original Ross Sea
colony names had an exact APBP locality name/site ID; **14/21** have
publisher-stated source coordinate uncertainty >250 m, and the other
**7/21** diverge by >3 km from the original NZ author colony location.
Therefore ZERO source sites satisfy the pre-frozen precision+identity
criteria, and zero independent original GIS-island annual comparison
windows are recovered. We did not substitute these published positions
for the original uncertain coordinates and did not open nesting outcomes.
APBP may republish the same NZ colony-year records: NOT independent
ecological replication.
- [V38 exact original APBP georeference QA](docs/NZ_ROSS_APBP_EXACT_GEOREF_V38_RESULT.md)
- [V38 all original source positions and precision](results/NZ_ROSS_APBP_EXACT_GEOREF_QA_V38.json)

**2026-10-24 V37 independent SCAR HIGH RESOLUTION geometry STOP:**
Original highres ADD v7.12 Shapefile ZIP 72,864,027 bytes source SHA256
66d82fa69f86eb8dbe8b04f01505cb2129feafec608455459ee4ed19d1dc38d4
contains 17,269 valid source LAND polygons. But published NZ Ross Sea Adélie
colony coordinates are rounded to arcminutes, not new GPS from this map:
only **2 islands / 5 source comparison years** if source point centers
must be on land. Requiring entire original ±0.5' OR ±1' plausible position
rectangle inside one land polygon yields only **1 island / ZERO shared
comparison years** (Cape Royds on Ross). Geography is therefore NOT
independently robust despite a finer map. This does NOT refute actual
nesting on Beaufort/Coulman/Inexpressible, nor alter the V36 61.5%
source-named island result. Original population outcome cells stayed closed.
- [V37 source highres original GIS + positional uncertainty decision](docs/NZ_ROSS_SEA_HIGHRES_PRECISION_V37_RESULT.md)
- [V37 publisher SHA and audited source positions](results/NZ_ROSS_SEA_HIGHRES_PRECISION_V37.json)

**2026-10-24 V36 ORIGINAL NEW ECOLOGICAL RESULT — heterogeneity among
SCAR land-polygon matched Ross Sea Adélie breeding units.** NZ publisher
2026 39-colony aerial census was restricted to four named independent
Ross/Beaufort/Coulman/Inexpressible land polygons, 13 shared original
1983–1992/2001/2004/2005 annual-change starts, and exact SAME-COLONY
paired original nest indices. Equal-year-balanced across-island SAME
DIRECTION = **61.5%** (19/30 pair-window signs; pair-weighted 63.3%).
Fixed 2000 within-island sign shuffles have median 51.3% and
5–95% 33.3–69.2%, placing the observation **inside** the diagnostic
reference range; this is NOT an autocorrelation-robust p-value or a
universal synchrony claim. Pair coefficients diverge sharply:
Ross–Beaufort **r=+0.468** (n11), Ross–Coulman **−0.501** (n5),
Ross–Inexpressible **−0.422** (n5). Other pair overlaps n<5 held.
Exact-polygon-only GIS precision sensitivity FAILS (2 islands, 5
shared years), and omitting Ross leaves only 7 concurrent windows
below the frozen >=8 threshold. This is observed *conditional island
heterogeneity*, not a mechanism or general Antarctic island law.
- [V36 original measured source and qualified ecological interpretation](docs/NZ_ROSS_SEA_GIS_ISLAND_GROWTH_V36_RESULT.md)
- [V36 full frozen 4-island numerical and GIS sensitivity](results/NZ_ROSS_SEA_GIS_PHYSICAL_ISLAND_GROWTH_V36.json)

**V35 new Ross Sea verified landmass support:** Original
39-colony NZ aerial census geocoded to independent source SCAR 2026 coastline
polygon features (original GIS SHA verified). Source-nearest land matches
resolve FOUR physical source-named islands with >=5 strictly consecutive
same-colony annual comparisons: Ross, Coulman, Beaufort, Inexpressible.
There are **13** same-calendar annual starts with >=2 separate candidate
land-polygons, including 7 starts with >=3; only source-count
availability, no biological effects. Ross 4 GIS-resolved subcolonies
are not four islands; original minute-level source coordinates leave
17 near-unique matches provisional, 8 exact, 8 unresolved. This is
enough to separately freeze true island-group census-change analysis,
not a climate or movement mechanism.
- [V35 original coastline polygon & cohort result](docs/NZ_ROSS_SEA_SCAR_ISLAND_GEO_V35_RESULT.md)
- [V35 actual geographic IDs, unmatched sites and years](results/NZ_ROSS_SEA_SCAR_ISLAND_GEO_V35.json)

**V34 2026 Ross Sea source colony-to-named-island geography:** 33 of
39 original Adélie census colony names exactly match author location IDs.
Eight *singular* named island candidates exist; in particular
Ross Island has 6 nested colony census series and Coulman Island 4.
Four original source-named island groups have >=5 same-colony annual
comparison windows, and **14** annual starts contain >=2 concurrent
named-island observations. Strict >=2 colony series in each of 2
named islands occurs in only **4** years (predefined >=6 requirement
FAIL); no within-vs-between COLONY effect is allowed. No raw original
census count values used; source place names still need separate coastline
boundary and method verification.
- [V34 exact publisher geographic ID/coverage audit](docs/NZ_ROSS_SEA_ISLAND_CROSSWALK_V34_RESULT.md)
- [V34 source named island and year support JSON](results/NZ_ROSS_SEA_2026_ISLAND_CROSSWALK_V34.json)

**New 2026 source V33 — Ross Sea 39-colony original aerial census:**
DOI 10.7931/kf06-x745, original February 2026 census XLSX verified against
publisher MD5 and SHA. 39 original colony identifiers × 44 years (1981–2024);
27 colony series have >=5 source observations, 41 source years >=5 monitored
colonies, and 305 same-colony strictly consecutive-year observation
opportunities. Original 2020 observations are **missing surveys**, not zero
breeding pairs. Some monitored colonies are nested on Ross Island; 39
colonies are NOT 39 independent islands. Location XLSX and method PDF
were also publisher-verified. No animal count magnitudes/effects opened.
- [V33 actual 2026 original data and QA](docs/NZ_ROSS_SEA_ORIGINAL_CENSUS_V33_RESULT.md)
- [V33 source + year coverage receipt](results/NZ_ROSS_SEA_39_COLONY_SOURCE_QA_V33.json)

**2026-10-22 V32 regional bootstrap ≠ replicated islands:** Original AADC
western Mac. Robertson Land 2009/10 and 2019/20 XLSX SHA-verified.
Its 1001-row census-estimate sheet lists replicate and regional
O.N.bootstrap.estimates fields, but no verified colony/island IDs.
1000 bootstrap realizations are uncertain versions of source estimates,
NOT 1000 independent islands. This archive cannot directly expand
V31's 2-island Adélie annual comparison into a 1000-island macro law.
- [V32 source-audited spatial grain and stop](docs/AADC_METAPOP_ISLAND_GRAIN_V32_RESULT.md)
- [V32 original SHA/header receipt](results/AADC_METAPOP_2009_2019_SOURCE_GRAIN_V32.json)

**V30–V31 East Antarctic original 2-island result (2026-10-21):**
Original AADC Béchervaise and Verner 1996–2003 Adélie occupied-nest
time series contain documented published fractional numeric census indices.
The earlier V30 integer-only gate STOPPED honestly (only 2/10 common source
years were exact integers). Independent published original field methodology
confirms observer-averaged Béchervaise nest counts; V31 explicitly froze
FLOATING publisher reported occupied-nest **indices**, preserving original
year/island/stage identities without rounding. On all **8 adjacent annual
windows**, original mean-within-source log1p index growth correlation is
**r=+0.754** (LOO +0.516 to +0.863); same direction **5/8** windows,
physical island units **n=2**. This is a genuine positive observational
local-island response, NOT evidence of inter-island migration, sea-ice,
resource effects or Antarctic-wide causality.

Three separate publisher monitoring networks (NOAA King George/Livingston
Gentoo +0.635, BAS Bird Island/Maiviken Gentoo +0.562, AADC
Béchervaise/Verner Adélie +0.754) have positive nearby-island
growth associations; these are selectively assembled, in different eras
and measurement units, so **not** an inferential meta-analysis or island
distance law. Broader APBP V27 consistency failed 10/22 direction strata;
V26 shows interregional synchrony changes over time.
- [V30/V31 original true-island comparison and critical methodology](docs/AADC_BV_OCCUPIED_NEST_V30_V31_RESULT.md)
- [V30 strict-integer source QA and STOP](results/AADC_BV_INTEGER_NEST_SUPPORT_V30.json)
- [V31 author-numeric nest-index result](results/AADC_BV_OCCUPIED_NEST_INDEX_GROWTH_V31.json)

**New AADC V28–V29 TRUE PHYSICAL ISLAND data:** Publisher-original XLSX
for Béchervaise, Verner and Petersen Adélie occupied nests was verified by
SHA256. Post-1990 directly monitored incubation-stage original source has
10 matched Béchervaise–Verner seasons and 8 consecutive annual comparisons,
passing the preregistered source gate. All three islands share only 5 source
seasons and 1 adjacent-year comparison: full three-island synchrony is NOT
estimable from that record. Nearby-source season coverage is real, but
not a panregional test. A separate original 1991–2019 Béchervaise demographic
and weather/nearshore ice table was verified, but measures only one region.
- [AADC original source and year support](docs/AADC_THREE_ISLAND_SOURCE_V28_V29_RESULT.md)
- [V29 source year counts](results/AADC_THREE_ISLAND_SEASONS_V29.json)

**2026-10-21 V27 genuine pan-regional database-based synchrony result:**
Unlike earlier land/ice-constrained V6, V27 uses the upstream original
SCAR–AntOBIS APBP Pygoscelis nest censuses directly. Exact same-month,
same-method, consecutive-season visits yielded **394 measured changes**
at original source sites. The frozen macroscopic source-support gate passed:
**22** evaluable species×year spatial concordance strata from **19 years,
50 source sites, 8 polar 250km blocks**, Adélie (17) and Gentoo (5).
Mean within-block minus between-block growth-sign concordance was
**+0.10852**, but only **10/22** strata showed a positive difference,
below the fixed two-thirds consistency rule. **Pan-regional directional
support failed**, not a biological null. A post-result Adélie versus
Gentoo description differs but is underpowered/unconfirmed and is NOT
a novel species-specific mechanism. Neither source sites nor grid
blocks equal physical islands.
- [V27 original APBP macro result](docs/APBP_PANREGIONAL_SYNCHRONY_V27_RESULT.md)
- [V27 full source and numeric receipt](results/APBP_PANREGIONAL_SYNCHRONY_V27.json)

**V26 FIXED-BIRD-COLONY ROBUSTNESS:** Replacing V25's varying 5–7 Bird Island
colony mean with the EXACT FIVE baseline 1982/83 observed colony names
for all 33 original annual growth windows preserves the period pattern:
early (<1997) Bird–Signy r=**+0.576** (14 windows), modern (>=1997)
r=**−0.141** (19), full historical r=+0.191. Under leave-one-window
removal the earlier r stays positive (+0.104 to +0.697) and modern r
stays negative (−0.206 to −0.047), as a descriptive sensitivity only.
Hence additions to the Bird colony monitoring roster do not alone create
the V25 pattern. BUT original nest/pair count-date median seasonal gap
is **12.5 days early vs 29.0 days late**; survey-stage/CCAMLR protocol
confounding remains, and there are only TWO physical islands.
No temporal ecological change point, shared prey mechanism or island law
was causally identified.
- [V26 source-backed fixed-component result](docs/BAS_BIRD_SIGNY_FIXED_ROSTER_V26_RESULT.md)
- [V26 exact numerical receipt](results/BAS_BIRD_SIGNY_FIXED_ROSTER_V26.json)

**V25 extends remote-island Gentoo synchrony across long monitoring history:**
BAS Bird Island–Signy annual nesting changes, using the same fixed seven
Bird colony IDs, show r=**+0.166 across 33 valid original consecutive-year
windows (1982–2018 start years)**. The correlation changes markedly with
period: **before 1997 r=+0.547 (14 windows)**, **from 1997 r=−0.144
(19 windows)**, versus the V23 short 2011–2018 r=−0.334 (8 windows).
The full-history leave-one-year-out r ranges **−0.048 to +0.244**, and
Signy monitoring conformed to CEMP from 1996/97. Thus the V23 near/far
gradient is **temporally nonstationary**, not an established immutable
distance law or proven climate transition.
- [V25 original historical biological result](docs/BAS_BIRD_SIGNY_LONG_HISTORY_V25_RESULT.md)
- [V25 long-term SHA-verified numerical receipt](results/BAS_BIRD_SIGNY_LONG_HISTORY_V25.json)

**V24 NOAA independent SST check closed by original nonfinite field:**
The fixed July–September prebreeding ERSSTv6 original regional 2° SST subset
contains one nonfinite original value at the **Signy region grid cell in
September 2011**. Bird and Maiviken each had 9/9 required winters,
Signy 8/9. The predefined full eight-window marine environmental
correlation could not be fit without imputation and was **STOPPED**.
V23 original three-BAS near/far Gentoo growth gradient remains supported
as an **exploratory description**, with no marine/sea-ice/wind cause.
- [V24 actual NOAA SST source STOP and interpretation](docs/NOAA_ERSSTV6_GENTOO_WINTER_V24_RESULT.md)
- [V24 source geometry, hashes, missing-data receipt](results/NOAA_ERSSTV6_BAS_GENTOO_WINTER_V24.json)

**2026-10-21 V23 ORIGINAL BAS GENTOO NEAR/FAR PATTERN:** On the same 8
annual-change start years (2011–2018), BAS-sourced Bird Island and Maiviken
South Georgia monitoring show positive growth alignment **r=+0.514**;
distant BAS Signy with Bird Island **r=−0.334** and Maiviken **r=−0.668**.
The fixed near-minus-mean-far contrast is **+1.015** (leave-one-window-out
+0.709 to +1.296). This is a real descriptive result at **3 physical landmasses**,
with nested Bird colonies, different source stage measures, and just 8
adjacent-year windows—not a distance, sea-ice or predator causal effect.
The positive V22 near coefficient had already been observed when V23
was frozen, so the comparison is explicitly exploratory.
- [V23 numeric original result](results/BAS_GENTOO_NEAR_VS_FAR_V23.json)
- [V23 source-based interpretation and next hypothesis](docs/BAS_GENTOO_NEAR_FAR_V23_RESULT.md)

**V22 actual local island-boundary ecology:** Seven stable Bird Island Gentoo
colony census components and the Maiviken monitoring site on the
South Georgia main island yield **r=+0.562** among 10 annual nest-count
growth windows, with **7/10 same-direction changes** (2009–2018).
This is genuine original-publisher data from two independent island landmasses
under one broad BAS monitoring institution, not a climatic causal estimate.
Within Bird Island 21 dependent colony-pair growth r values have median +0.611.
- [V22 source-backed result and interpretation](docs/BAS_BIRD_MAIVIKEN_GENTOO_V22_RESULT.md)
- [V22 exact numeric receipt](results/BAS_BIRD_MAIVIKEN_GENTOO_NEST_GROWTH_V22.json)

**2026-10-20 V21 new original island–main-island comparator:** BAS historical Bird Island
Gentoo original colony file: **252** rows, SHA256 b1abc3c3...;
BAS Maiviken on the South Georgia *main island*: **12** source rows,
SHA256 8eef8ba0.... These were downloaded and verified in Actions;
the updated 2026 Bird Island v2 exists but its original file was NOT
opened. The original colony/date/count schema supports a frozen
V22 same-year incubating nest comparison, conditional on adequate
season and colony coverage. This is NOT continental mainland Antarctica.
- [V21 actual source QA and decision](docs/BAS_BIRD_MAIVIKEN_V21_SOURCE_RESULT.md)
- [V21 source receipt](results/BAS_SOUTH_GEORGIA_GENTOO_V21_SOURCE_QA.json)

**V20 real exploratory outcome (2026-10-20):** Using exact original
NOAA/BAS source bytes, **14 positive same-year Gentoo within-site annual
changes across three physical islands** were analyzed without pooling
incomparable census/pair count levels. Nearby NOAA King George–Livingston
log-growth correlation r=+0.635, while NOAA-to-BAS Signy r=+0.124 and
−0.028. Within-rookery NOAA Gentoo–chinstrap growth also correlated
(r=+0.626 Copacabana and +0.714 Cape Shirreff). Only **4/14**
annual change windows had all three islands growing or shrinking in
the same direction. Geographic proximity and survey-provider effects
are *confounded*; this is NOT independent evidence of climate, prey,
competition, or island-capacity mechanisms. Do not state a new Antarctic
island law or select time ranges after inspecting results.
- [V20 empirical result, hard alternatives, source-hashed reproduction](docs/NOAA_BAS_GENTOO_GROWTH_SYNCHRONY_V20_RESULT.md)
- [V20 saved actual numeric receipt](results/NOAA_BAS_GENTOO_GROWTH_SYNCHRONY_V20.json)

**V18–V19 NEW source-backed panel:** Official NOAA 0185113 provides
38 austral-season years and five census columns from monitored
Copacabana (King George Island) and Cape Shirreff (Livingston Island).
An independently source-hashed BAS Signy gentoo stage-resolved CSV has
43 original records. All three island sources have **16 original
austral seasons** with numeric-lexical census/pair fields and **14
consecutive-year windows**. This passes the frozen structural years gate,
but NOAA original species census numbers are **NOT yet shown
equivalent to BAS breeding pairs**, and only 3 physical islands exist.
No biological count effect or island mechanism has been fitted.
- [V18/V19 new publisher-original source panel and decision](docs/NOAA_BAS_THREE_ISLAND_SOURCE_SUPPORT_V18_V19.md)
- [V18 original source hashes and headings](results/NOAA_BAS_ISLAND_STAGE_SOURCE_QA_V18.json)
- [V19 exact comparable-year support](results/NOAA_BAS_THREE_ISLAND_SEASON_SUPPORT_V19.json)

**V17 cross-guild within-site annual change STOP:** Of 137 uniquely co-dated
site/species-pair/season observations in the ASI source, 25 qualifying
consecutive-year comparisons passed the 21-day census-stage constraint. They
came from only **11 original site IDs in two ASI regions (CW 14, SH 11)**,
not the predeclared minimum three. Blue-eyed shag accounts for 23/25
cross-guild comparisons. No original Count magnitudes or biological
correlations were opened or fitted; further test requires genuinely
independent island-level stage-resolved monitoring.
- [V17 result and decision](docs/ASI_CROSSGUILD_TEMPORAL_V17_RESULT_AND_DECISION.md)
- [V17 numeric support](results/ASI_CROSSGUILD_SAME_SITE_YEAR_GROWTH_V17.json)

**V16 new, source-authenticated ASI cross-guild panel:** The distinct 2013
Antarctic Site Inventory Ecological Archives original CSV has 1,124 census
rows. A strictly same-site/date, ASI-source, nest-only and accuracy-filtered
join yields **99 penguin × flying-seabird same-day census events across
37 source site IDs and three regions**. Source Region collisions (two
original Site_ID labels, 12 rows) were conservatively dropped. Two-penguin
same-day comparisons have 53 events across three regions and FAIL their
prospectively frozen gate. This is source feasibility, **not** a fitted
cross-guild ecological mechanism or independently surveyed physical islands.
- [V16 original source result and decision](docs/ASI_ORIGINAL_COSURVEY_V16_RESULT_AND_DECISION.md)
- [V16 machine-readable source support](results/ASI_ORIGINAL_SAME_DAY_NEST_COSURVEY_V16.json)

**2026-10-20 V15 biotic-interaction feasibility is also CLOSED.** Original AADC
Adélie×south-polar-skua co-searches gave **1,061 same-site/season pairs
across 96 island geographic sites**, but only **8 pairs / 8 sites in one
region** had matching exact reported survey date; the fixed comparator
Adélie×snow-petrel had **701 pairs across 89 sites**, but one co-dated pair.
Matching source obs_number fields are not a validated shared visit/observer
identifier across independently compiled source books. Thus this is
**a sample-support STOP, not a fitted species-interaction effect**. The prior
Southwell paper created multiple species×sites×season records from heterogeneous
source references. No new Antarctic predator-resource mechanism follows.

- [V15 original co-survey support and decision](docs/AADC_PENGUIN_SKUA_COSEARCH_V15_RESULT_AND_DECISION.md)
- [V15 source-only numerical receipt](results/AADC_PENGUIN_SKUA_COSEARCH_SUPPORT_V15.json)

**Current result, 2026-10-20: the original-data V14 macroanalysis is complete
and reproduced, with no supported guild × island-area result.** Source access
is resolved. The previous statement that demographic outcomes were still
unopened is superseded by the executed V6, V8 and V14 analyses.

The new AADC source join contains **7,785 geographic sites and 33,107 original
eight-species search records**. V14 compares the seven flying seabird species:
**6,956 direct P/A records, 368 sites (295 islands + 73 continental outcrops),
1,581 site/species histories, and 8 held-out 250 km blocks**. Nonreporting is
never coded as absence; repeat seasons do not count as additional islands.

Primary equal-region Brier scores (lower is better) are **0.310378** for the
survey/species/geography baseline, **0.356245** with area and land class,
and **0.359034** with nesting-guild interactions. Only **3/8** regions improve
with guild terms, below the frozen **6/8** requirement. CREVICE island and
continental area IQRs do not overlap. Thus predictive support failed and the
island-specific three-way interpretation fails the frozen overlap rule;
this is not a demonstrated zero ecological effect.

All five original workbooks were retrieved and verified again; V13 input CSVs,
included rows and all **115** original numerical result fields reproduce
exactly. Reporting now distinguishes ordinary-row, history-weighted and
equal-region scores. **27 focused V11–V14 tests pass.**

The broader programme still asks how marine resources and terrestrial or
sea-ice breeding substrate jointly structure Antarctic breeding populations.
The first V6 land/sea model and V8 habitat-mosaic test also failed their
frozen support criteria. V14 is closed without changing guilds, weights or
spatial thresholds to seek a positive result. The frozen Ecology manuscript
is separate; no positive Antarctic-wide mechanism is claimed.

Canonical current state and full numerical evidence:
- [V14 result, interpretation and next state](docs/AADC_GUILD_ISLAND_AREA_V14_RESULT_AND_DECISION.md)
- [V14 numerical result](results/AADC_GUILD_ISLAND_AREA_SPATIAL_CV_V14.json)
- [Exact source/model reproduction](results/AADC_V14_REPRODUCTION_20261020.json)

Earlier programme design and atlas provenance:
- `contracts/MINA_RESEARCH_PROGRAM_V1.json`
- `docs/ANTARCTIC_BREEDING_ISLAND_MACROECOLOGY_V1.md`

---

## Independent Palmer phenotype reassembly lane

A separate short-paper lane now asks where the conspicuous Palmer
breeding-site phenotype comes from.

The frozen ecological result is hierarchical:

- across the full assemblage, morphology-to-site predictability is dominated by
  species identity;
- within Adélie penguins, fixed island morphology effects are small;
- structural island contrasts repeatedly reverse among years;
- same-year island classification is modestly above chance
  (**balanced accuracy 0.448**), while leave-one-year-out transfer falls almost
  to the three-island chance reference (**0.342** vs **0.333**).

The biological interpretation is therefore **species sorting plus temporal
reassembly**, not a persistent within-species island ecotype.

This lane is independent of frozen Paper 1 and the Antarctic-wide Paper 2
programme. It does not reopen either paper and does not make an ODSP methods
claim.

Canonical files:

- `contracts/PALMER_PHENOTYPE_REASSEMBLY_PAPER_V1.json`
- `results/PALMER_PHENOTYPE_REASSEMBLY_RESULT_V1.json`
- `docs/PALMER_PHENOTYPE_REASSEMBLY_MANUSCRIPT_SPINE_V1.md`

---

## Current ecological claim

For a spatially structured breeding population, total abundance and relative
spatial composition are distinct state descriptions.

The null model uses each observed annual population total as the **latent
expected annual total**, fixes one time-invariant vector of breeding-component
shares, and then simulates counts under the frozen Poisson / Gamma–Poisson
observation-error family. It therefore includes both the finite-count tendency
for small components to disappear as abundance declines and independent count
noise.

The observed decline in effective breeding-component number is more negative
than that null in all five studied population units:

- Palmer Cormorant Adélie: **3.54 → 2.86** (**−19%**), CV20 p = **0.038**;
- Palmer Humble Adélie: **4.62 → 2.28** (**−51%**), CV20 p = **0.000010**;
- Palmer Litchfield Adélie: **5.78 → 1.00** (**−83%**), CV20 p = **0.000010**;
- Signy Adélie: **3.08 → 1.94** (**−37%**), CV20 p = **0.000010**;
- Signy chinstrap: **4.44 → 2.19** (**−51%**), CV20 p = **0.000020**.

Palmer is explicitly the **discovery system**. Its public colony codes are
treated as monitored census components, not verified fixed GIS polygons. The
confirmatory weight rests on the two prospectively frozen Signy tests.

The endpoint is inverse-Simpson effective component number, a Hill-number
measure of relative concentration. It can fall while every monitored component
remains occupied. It is therefore **not** occupied-site richness, physical
breeding area, genetic effective population size (Ne), or genetic effective
number of breeders (Nb).

The closest general literature includes positive abundance–occupancy
relationships, geographic range contraction, and marine-fish
proportional-density versus basin models. Accordingly, mina does **not** claim
that abundance and spatial extent are newly separable. The transferable result
is narrower: a discrete breeding-component composition can depart systematically
from proportional thinning, and that departure can be tested conditional on
the observed abundance trajectory.

## Ecological framing

mina treats penguin breeding islands as **externally subsidized breeding
patches**. Food resources are primarily marine; breeding surfaces are discrete
and terrestrial. Regional marine processes can therefore impose a shared
demographic direction while local snow, geomorphology, colony history and
remaining nest-space organization shape vulnerability.

Direct biotic interactions are not assumed absent. They are treated as
localized and testable rather than as the default explanation for whole-island
trajectories.

## Submission status

The canonical submission is **Ecology Report v0.5**.

Current package:

- manuscript: `submission/MANUSCRIPT_ECOLOGY_REPORT_V0_5.md`
- cover letter: `submission/COVER_LETTER_ECOLOGY_REPORT_V3.md`
- main captions: `submission/FIGURE_CAPTIONS_ECOLOGY_REPORT_V0_4.md`
- supplementary caption: `submission/SUPPLEMENT_ECOLOGY_REPORT_V0_4.md`
- copy fields: `submission/ECOLOGY_SUBMISSION_COPY_FIELDS_V2.md`
- readiness audit: `submission/SUBMISSION_READINESS_ECOLOGY_REPORT_V3.md`
- reviewer stress test:
  `submission/PRE_SUBMISSION_REVIEWER_STRESS_TEST_ECOLOGY_V1.md`
- scientific freeze: `contracts/ECOLOGY_REPORT_SUBMISSION_V3.json`

The old Ecosphere, JBI and integrated manuscripts are **provenance only** and
must not be treated as parallel submissions. The integrated JBI line is formally
superseded.

## Development state

The Ecology Report scientific content is **frozen**. Before initial submission,
do not add:

- new ecological endpoints;
- alternative concentration metrics;
- tuned thresholds or time windows;
- additional error models selected after outcome inspection;
- extra species as post-result rescue analyses;
- new mechanism claims.

Allowed work is limited to reference completion, copyediting, journal
formatting, author metadata, archival metadata, figure QA, and clarification
from the Palmer data providers about colony-code continuity.

The remaining submission blockers are author-controlled metadata: author order,
affiliations, corresponding author, funding/acknowledgments, CRediT roles,
conflict-of-interest statement, complete AI-tool inventory, overlap statement,
and ORCIDs if requested.

## Reproduce

Install:

```bash
python -m pip install -e ".[dev,figures]"
```

Fetch the frozen census:

```bash
python scripts/fetch_lter_census.py build/adelie_census.csv
```

Primary analyses:

```bash
mina-lter --census build/adelie_census.csv --out build/lter.json
mina-colony-network --census build/adelie_census.csv --out build/colony.json
mina-hierarchical-variability --census build/adelie_census.csv --out build/hierarchy.json
mina-neff-momentum --census build/adelie_census.csv --out build/neff_momentum.json
```

The manuscript figure workflow additionally exports pinned APBP/MAPPPD site
metadata and regenerates Figure 1–5 data before rendering PNG and PDF outputs.

## Provenance

The project began as a biological follow-up to the frozen ODSP Palmer Penguins
audit. ODSP remains the methodological provenance source; all current biological
development and manuscript work belongs in `mina`.
