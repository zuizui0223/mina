# V30–V31 — Genuine East Antarctic Adélie occupied-nest index covariation across two islands

**Completed 2026-10-21.** Original AADC EDS 1103 official publisher workbook `population_counts_BI.xlsx`, DOI [10.26179/5c9bf6704cf70](https://doi.org/10.26179/5c9bf6704cf70), exact raw SHA256 `8377fd17d4d84ccb791229ebdf5926605ae34aeffd0c1a21a0a7ae75d4facdf6`. The frozen 1990–2004 source sample is *Adélie occupied nests*, **not adults, chick counts, inferred unobserved sites or the older time-corrected photo records**.

## 1. The genuine measurement-unit discovery and frozen scientific response

V28 retrieved the original public AADC package and V29 froze **10 explicit common source seasons** (1991 and 1996–2004) for **two different physical islands**, Béchervaise and Verner; eight truly adjacent annual changes start 1996–2003. Petersen has only five common seasons and one adjacent change, therefore cannot contribute to a comparable three-island analysis.

V30, frozen before original magnitudes, required exact nonnegative **INTEGER** census counts. It failed honestly: among 20 real measured island×year cells (10 seasons × two islands) **10 were Excel numeric fractional values**, 10 exact integers. Fractional cells: Béchervaise **8 of 10** years; Verner **2 of 10**. Both integer-compatible in only 1997 and 2003, **zero strictly adjacent years**. No V30 ecological r was fitted. [V30 exact source and categorical quality receipt](../results/AADC_BV_INTEGER_NEST_SUPPORT_V30.json).

Critically, official [AADC occupied-nest field methods](https://data.aad.gov.au/metadata/records/breeding_success_BI) explicitly report that Béchervaise's *several field observers each counted colony nests multiple times*, and counts close within 10% were **averaged**. Thus literal fractional published numbers need not be mistakes; demanding every publisher's estimate be exactly an integer was too narrow a measurement interpretation. Original [AADC three-island dataset documentation](https://researchdata.edu.au/adelie-penguin-population-islands-mawson/701463) separately confirms post-1990 occupied-nest counts on about 2 December and warns pre-1990 records could be time-corrected. The detailed averaging protocol is documented for Béchervaise, **not independently confirmed for Verner**.

A **distinct V31 measurement specification** was fixed AFTER V30's invalid integer gate but BEFORE any V31 numerical effect: use the publisher's original finite nonnegative floating-point **reported occupied-nest INDEX** unchanged, not rounded/converted to physically independent nesting adults. The island/site/season/8-window roster and direct observed stage remained IDENTICAL to frozen V29/V30, and all original year/source hashes matched. Every one of the 10 common numeric source seasons passed the index definition. This transparency avoids portraying V30 as biological evidence that only 2 years were monitored.

## 2. V31 original ecological result

| Fixed original observation comparison | Result |
|---|---:|
| Matched Béchervaise–Verner original seasons | **10** |
| Adjacent annual count-index change starts | **1996–2003, n=8** |
| **Pearson r of within-island annual log1p reported nest-index changes** | **+0.7539596** |
| Leave-one-annual-start-year-out r range | **+0.5157217 to +0.8627967** |
| Both source indices moved in the same direction | **5/8** windows |
| Mean arithmetic offset fraction of recorded index count changes | **0.1116680** (11.2%) |
| Independent physical-island units | **2** |

The positive correlation survives each single-annual-window deletion, although only five of eight annual changes share direction; the magnitude of shared larger changes contributes to r. The small mean algebraic cancellation index is **not** direct movement or proof that colonies redistribute. No p-values or independent marine climate effects were computed.

**Supported narrow observation:** Across a separate real nearby island pair in **East Antarctica**, reported Adélie breeding-stage occupied-nest indices fluctuate together at least somewhat through the 1996–2004 paired period. The exact magnitude is sensitive to how estimated fractional nest counts were generated. Authoritative Béchervaise observer averaging is known; equivalent detailed Verner effort/stage verification remains incomplete. These data cannot prove ecological coupling, recruitment, individual dispersal, competition, prey forcing, wind or sea-ice dependence.

## 3. Cross-programme spatial perspective (deliberately NOT a meta-analysis)

All three source-authenticated nearby-landmass penguin monitoring pairs currently available in mina have **positive descriptive annual nesting-count changes**, but species, count unit, years and sampling design differ:

| Separate publisher monitoring system | Species | Exact annual growth windows | Local pair r |
|---|---|---:|---:|
| NOAA US AMLR: King George – Livingston (South Shetlands) | Gentoo | 14 | **+0.6349** |
| BAS: Bird Island – Maiviken (South Georgia island/main-island) | Gentoo | 10 | **+0.5622** |
| AADC: Béchervaise – Verner (East Antarctic offshore islands) | Adélie | 8 | **+0.7540** |

This is an intriguing **three-region ecological pattern** rather than an independently sampled predictive generality law: these pairs were assembled during iterative exploration, measured different nests/pairs or time windows, and are not replicated islands within each contrast. Do not average these three r values, attach a p-value, claim every Antarctic seabird does this, or infer that an oceanic island boundary CAUSES shared growth.

**Checks against overgeneralization:** V27 original APBP three-species nest census analysis across eight 250-km regions **FAILED** the predeclared consistent within-region synchrony gate (positive within-minus-between contrast in only 10/22 matched species×year strata). V25–V26 original fixed-colony Bird–Signy comparison changed from **+0.576 early (<1997)** to **−0.141 later**, and source count-date phenology offsets changed too, so synchrony is clearly not stationary across arbitrary periods or globally attributable to distance. V24 independent NOAA ERSSTv6 winter SST trial was STOPPED due a nonfinite source value and gave NO marine cause.

## 4. Decision and next source need

**V31 scientific decision: EXPLORATORY_SINGLE_NEARBY_ISLAND_NEST_INDEX_COVARIATION_NONCAUSAL.** In contrast to repeatedly fitting unsupported land/sea interaction models, the data now support a *bounded* new cross-region observational statement: local annual breeding changes can be positively associated across true island boundaries, while geographic and historical generality are unresolved.

For a new Antarctic island-ecology manuscript, the outstanding unit is a **network of independent, contemporaneously surveyed physical island pairs** with source colony/method continuity, measured environmental and marine accessibility differences, true nil returns, and ideally marked-bird movements. Neither 2 observed islands nor 3 retrospectively selected pairs establish migration, stable physical distance laws, or island-specific causal mechanisms. Preserve Ecology Paper1 PR189 unchanged.

## Exact artifacts and evidence

- [Frozen source-quality V30 contract](../contracts/AADC_BV_ISLAND_NEST_GROWTH_V30.md) and [fixed V30 numerical STOP](../results/AADC_BV_INTEGER_NEST_SUPPORT_V30.json), [V30 successful source CI](https://github.com/zuizui0223/mina/actions/runs/39530567566).
- [Original method-corrected V31 contract](../contracts/AADC_BV_CONTINUOUS_OCCUPIED_NEST_INDEX_V31.md), [V31 result](../results/AADC_BV_OCCUPIED_NEST_INDEX_GROWTH_V31.json), [official-publisher source CI](https://github.com/zuizui0223/mina/actions/runs/39531089392).
- [V27 independent APBP broad comparative negative source result](APBP_PANREGIONAL_SYNCHRONY_V27_RESULT.md).
- [V20 NOAA gentoo nearby pair original result](NOAA_BAS_GENTOO_GROWTH_SYNCHRONY_V20_RESULT.md), [V22 BAS southern Georgia island pair result](BAS_BIRD_MAIVIKEN_GENTOO_V22_RESULT.md), and [V26 period sensitivity](BAS_BIRD_SIGNY_FIXED_ROSTER_V26_RESULT.md).
