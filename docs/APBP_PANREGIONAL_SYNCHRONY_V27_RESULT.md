# V27 — Pan-regional Penguin nest-change spatial synchrony, original APBP data

**Executed 2026-10-21 from the original 2023 SCAR–AntOBIS APBP sampling database, DOI 10.48361/zftxkr**, not from figures in previous publications. The source-Darwin-Core V2 join CSV exact SHA256 75c98ad9174f6ca8b88ae915adb8bb39de5d279099b45ce1ae7d1b2e25d5ba59 was verified in [real original-source GitHub Actions #39516149973](https://github.com/zuizui0223/mina/actions/runs/39516149973) with five synthetic fixture tests. The first CI attempt failed a deliberately invented January austral-year fixture, fixed without changing data, sample, method or support gates. Original ecological effects were exposed only after the source-support thresholds specified in [V27 contract](../contracts/APBP_SPATIAL_SYNCHRONY_V27.md) passed.

## Actual source scope
- Original 4,750 APBP linked ExtendedMeasurementOrFact records, including previously documented 3,370 observed typed Pygoscelis NEST measurements. Original source is an extensive **compilation of field/satellite censuses**, not 4,750 independent survey systems.
- Excluded all **214** duplicate source site×species×breeding-season groups (520 original rows), without choosing a favorable survey. **1,726** unique original site/species/season records remained after V6-compatible source month and geographic checks, before forming interannual pairings.
- Strict same original site×species, genuinely consecutive breeding season, same December/January/February original calendar month and identical nonempty original samplingProtocol gives **394** year-to-year recorded nest changes (Adélie **299**, Gentoo **64**, chinstrap **31**). There were **71** month mismatches and **5** protocol unknown/changed consecutive pairs excluded; 375 of the 394 valid changes share nonempty exact source reference text, the other 19 do not.
- Frozen simultaneous spatial comparison gate passed: **23** source-qualified species×start-year strata, **19** distinct years, **2** species, **8** independent EPSG3031 250km spatial grid blocks and **50** distinct original source-site IDs. Numeric nonzero direction gate leaves **22** evaluable species×start-year strata in those 19 years. Neither 50 source sites nor 8 grid blocks are known to be 50 or 8 distinct physical islands. Species supported in the stratum comparison are Adélie **17** and Gentoo **5**; chinstrap has no spatially supported stratum despite 31 eligible transitions.

## Frozen spatial concordance result

An eligible stratum contains both within-the-same-250km-block and between-block original site-pair opportunities in the **same species and annual census-change year**. Biological response is sign of observed strictly adjacent original nest-count log1p change; genuine unchanged counts do not enter a concordance denominator. Each species×year stratum receives equal weight, preventing the one largest block from dominating.

| Primary exploratory statistic | Original data result |
|---|---:|
| **Unweighted mean within-block minus between-block same-direction frequency** | **+0.1085196052** |
| Fixed contrast direction positive | **10/22** strata (45.45%) |
| Fixed contrast direction negative | **9/22** strata |
| Difference exactly zero | **3/22** strata |
| Leave-one-original-start-year-out mean difference | **+0.0818716 to +0.1304827** |
| **Prespecified consistency threshold** | **At least 2/3 positive strata — FAIL** |

**Scientific decision: NO_SUPPORTED_PANREGIONAL_SPATIAL_CONCORDANCE_DIRECTION.** Although the mean difference is positive, a minority (10/22) of independent species×year comparison strata have positive contrast; a few large positive strata drive the average. One 2007 Adélie stratum has difference exactly +1.0, but there are negative and zero outcomes in other years. The result **does not** support a consistent spatial-synchrony law beyond a single study system. It is neither a null demonstration nor an island-barrier effect.

### Secondary source description, not a prospectively confirmed species difference

- Adélie: **17 strata**, mean contrast **+0.1805865**, 10 positive, 5 negative, 2 zero.
- Gentoo: **5 strata**, mean contrast **−0.1365079**, 0 positive, 4 negative, 1 zero.
- Chinstrap: no eligible matched-year within/across-grid comparison stratum.

This contrast was computed **after reviewing the primary original effects**, and the Gentoo temporal-spatial sampling is severely sparse. It is a hypothesis-generating species-specific pattern, **NOT** evidence that Adélie and Gentoo differ biologically in spatial synchrony. Any cross-species test requires independent monitoring with comparable sampling protocols, sites, seasons and physical island identity.

## Ecological and methodological interpretation

- The V26 two-island period effect is not a stable geographic law; V27 expands to 8 spatial grids and 19 years and fails its own frozen sign-consistency requirement. Do not claim it reproduced the 1997 change: source periods, nested source IDs, species and survey programmes differ.
- A 250-km grid block is not a physical island. Within-block site pairs may represent one island; between-block site pairs may cross oceanic regions or the Antarctic continent. The source does not measure a water barrier, actual territory/rock capacity or individual dispersal, and no environmental variable is used here.
- Same **calendar month** and equal samplingProtocol *text* are important checks but are not full breeding stage or observer consistency; survey references can repeat across multiple sites/years. Each original site-pair is nonindependent of other pairs. No p-value was produced, and no mechanism of marine winter climate, sea-ice/krill, island size, conspecific attraction, predation or competition was fitted.
- APBP V27 reused the upstream original source family that was also used by V6, so these do not constitute independent biological replications. The earlier V6 land×sea×island effect remains unsupported; do not retune its scale or merge it into the frozen Ecology PR189.

## Research disposition and next source need

**Stop APBP V27 at its original frozen results.** The primary scientific gap remains a multi-island, multi-region breeding-count network with verified identity, matched original nest stages, annual repeated sampling and independently measured weather/marine conditions. The existing BTO/JNCC Seabird Monitoring Programme is a potential *taxonomically independent* globality check, but its bulk record-level and site boundary crosswalk access remains conditional; it is not an Antarctic island replication. CCAMLR CEMP A3 biological population monitoring is more directly Antarctic but record-level access has not been authenticated in this repo. Verify legal source access/overlap and source ID continuity before any new macro confirmation.

- [Frozen V27 contract](../contracts/APBP_SPATIAL_SYNCHRONY_V27.md)
- [Complete source-authenticated numeric result](../results/APBP_PANREGIONAL_SYNCHRONY_V27.json)
- [Original run and synthetic tests SUCCESS](https://github.com/zuizui0223/mina/actions/runs/39516149973)
- [Publisher original data citation](https://doi.org/10.48361/zftxkr)
