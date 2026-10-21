# V28–V30 — First independent North Atlantic seabird macroecological composition analysis

**2026-10-21, original JNCC 2024 revision, real count-magnitude analysis.** Separate research branch/PR from the Antarctic PR197, not a direct replication of the *Ecology* penguin paper PR189. The source is the official Seabird 2000 (1998–2002; Gannet 2003–2005) and Seabirds Count (2015–2021) matched breeding-site dataset, revision 8 July 2024. The exact publisher XLSX (2,570,979 bytes; SHA256 9edf05b8af0a44c3ca770f390120c4b99bcaae3ae35fd844a82982d6ad8116d4) was re-downloaded each time from the [JNCC official release](https://jncc.gov.uk/resources/63f0ea40-485d-46dd-b967-150df90a7b2b). This analysis is an independent JNCC census source rather than digitizing results of several research papers.

## 1. Source sample audit and decisions

Official source has 4 sheets, main 22,131 rows including first 4 header/descriptor rows, plus independent Atlantic Puffin *comparable* table (189 rows), and separate all-record Puffin table. The source cover says NA = insufficient available comparative data (NOT confirmed zero), 3 confidential species omitted, natural-nest gulls only, and five distinct count units AON/AOS/AOT/AOB/IND. No source author percentage-change field was used as a new ecological response.

- Strict original Site.ID, Species, Country, Master site, source latitude-longitude and ORIGINAL two-survey year matching; only rows with the same biological count unit and both literal count fields present. **14,112** individual source site×species comparable rows; **1,485** original source species×Country×Master×unit panels with >=3 uniquely paired child Site.ID values; 17 species, 631 distinct Country×Master networks and 5 count units.
- The V30 frozen parent-overlap rule further removed seven child records with a name exactly equal to their Master-site name where other original children existed (possibly overlapping source aggregate). This left **1,483 structurally eligible panels**, 630 country-master networks and all 17 species and 5 units.
- Opening biological numerical count values only after the V28–V30 source-structure gates and original SHA check, **1,321** panels across 17 species, 604 Country×Master networks and 5 source units had fully compatible discrete totals N0>=2 and N1>=2. **162** otherwise structural panels were excluded for at least one epoch total <2. No fractional counts needed rounding in the frozen V30 cohort. All count-derived outputs are panel-level summaries, not copied source raw observations.
- The biologically conditioned cohort of **959** original panels had a lower measured TOTAL across the same original child Site.ID components in the newer census; 349 had higher total and 13 unchanged. This is NOT the direction of entire UK seabird populations, because the panel represents only two census epochs and matched monitored child sites, not every original territory/colony.
- Data source identifiers, outcomes and source units are NOT island polygon IDs. A Master site is administrative/geographical, not a demographically independent breeding population. Sites can have changing boundaries or adjusted count effort across the 15–23 years. No annual synchrony inference.

## 2. A priori null-corrected concentration estimand

For each parent panel with n eligible same original Site.ID components, let p_i,0 = original earlier adjusted count / old matched-site total, p_i,1 = later adjusted count / newer matched-site total. Simpson concentration C_t = sum_i p_i,t^2 and effective component number N_eff,t = 1/C_t.

**Conditional ideal proportional-allocation reference** at the newer observed total N1 treats each later count unit as a multinomial allocation from fixed original p_i,0. Its expected concentration is exactly:

C_expected = C0 + (1−C0)/N1.

The predeclared corrected residual E = C1 − C_expected measures observed concentration beyond this finite-count benchmark. E>0 is greater concentration; E<0 is a more even distribution than this ideal reference. **This is not an actual model of recruitment, adult migration, breeding colony boundaries, or observation error.** The source reports *totalled adjusted counts*; random allocation is used as a transparent arithmetic null, not proven individual-level stochastic thinning.

Original two-census site-share turnover was measured separately: TV = 0.5 sum_i |p_i,1−p_i,0|. TV detects compositional switching even when total concentration remains unchanged, and it does not imply confirmed ecological site extinction.

## 3. Actual multi-species result

| Fixed primary metric | JNCC source result |
|---|---:|
| Analysis-supported integer-comparable parent panels | **1,321** |
| Same-original-site total count declining panels | **959** |
| Panel fraction with E>0 among declines | **0.62252346 (62.25%)** |
| Median panel E among declines | **+0.0355556** |
| Species-equal mean E across 17 species | **+0.0935594** |
| Species with positive mean E | **14/17 (82.35%)** |
| Prespecified direction test | **PASS (mean>0 and >=2/3 species positive)** |
| Median site-share total variation TV among declining panels | **0.353630** |
| Declining panels with TV>=0.25 AND E<=0 | **23.9833% (230/959 panels)** |

The two distinct phenomena matter: even among declining panels, substantial redistribution (site-share TV>=0.25) need NOT be toward a smaller effective number of breeding sites. This gives a specific cross-taxon conceptual distinction between *redistribution* and *concentration* beyond the finite-count arithmetic. It is ecological description, not confirmed immigration/emigration or site-persistence mechanism.

Country-leave-one-out species-equal means are positive throughout the frozen sensitivity (min **+0.05846** when Scotland omitted; max **+0.10440** when Republic of Ireland omitted). Unequal sample coverage remains important: **758/959** declining panels are Scottish, so raw panel-level percentages are geography-weighted. Species-equal means reduce taxonomy dominance but do not eliminate region, habitat or repeated master-site dependence.

Among 17 species, mean E is positive for 14. Examples (not significance-tested, different source unit families): Arctic Tern +0.1925, Common Gull +0.2050, Black-legged Kittiwake +0.1369, Atlantic Puffin +0.1886; Great Skua −0.0415, Great Black-backed Gull −0.0065 and Black Guillemot −0.0006. These are POST-RESULT secondary contrasts; no general biological trait mechanism is established by ranking species.

## 4. What is and is not scientifically supported

Supported for source-matched observed panel components: multi-taxon excess spatial breeding-count concentration relative to **one idealized finite-count proportional-allocation** reference, plus widespread site-share redistribution not equivalent to increased concentration. This is the first actually large independent seabird census dataset explored in this branch. The result is more general across taxa than the earlier five-penguin colony systems but does not demonstrate a confirmed common social Allee-effect mechanism.

Unsupported or unverified: physical small-island vs large-main-island dependence; seawater barrier/accessibility, ocean currents, marine climate, nest-availability, species interactions, true whole-colony distribution, annual breeding growth synchronicity, dispersal and causal competition. Site.ID identity without a versioned historical boundary crosswalk is not perfect habitat continuity. Different source count units must never be pooled in absolute abundance. Claims about island effects require independent physical land polygon labels BEFORE examining their association with E.

Other potential biases: retrospective source coverage (NA != zero), natural nest sites only for certain gulls, adjusted counts may not obey literal multinomial animal thinning, monitoring location definitions and species-specific observation error, mixed census timing between 1998/2002 and 2015/2021, Master-sites nested in regional geography. No p values or external replication are claimed.

## 5. Durable original evidence

- [V28 exact original workbook inventory](../results/JNCC_REVISED_TWO_CENSUSES_ORIGINAL_V28.json); [V28 source CI](https://github.com/zuizui0223/mina/actions/runs/39517353543)
- [V29 identity/unit/panel support](../results/JNCC_TWO_CENSUS_SITE_PANEL_SUPPORT_V29.json); [V29 original source CI](https://github.com/zuizui0223/mina/actions/runs/39517780964)
- [Frozen V30 contract](../contracts/JNCC_COMPONENT_CONCENTRATION_V30.md)
- [V30 numeric result](../results/JNCC_COMPONENT_CONCENTRATION_V30.json); [V30 original source and synthetic tests CI](https://github.com/zuizui0223/mina/actions/runs/39518780432)
