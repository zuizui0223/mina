# JNCC × UK island mammalian predator niche: original-data V33–V36 decision (2026-10-27)

**Status:** 2017 primary mammal source recovered, independently built source-only 9,688-island link and exploratory reported-status models completed; **strict cross-island seabird-refuge hypothesis does not meet the prespecified sample gate.** PR #201 remains **DRAFT**. No adjusted JNCC bird counts or V30 concentration E were used in V33–V36. No seabird movement, predator effect, ecological occupancy probability or causal contrast was fitted.

## 1. What independent original sources are actually available

The RSPB UK Islands 2014 GIS API returned **9,688** source points, all with unique integer \`lowid\` and WGS84 coordinates. Its fields include high- and low-water island area, original archipelago group, population and ferry access. This is an island **point inventory**, not a physical polygon or quantified predator field survey.

The exact publisher supplement for Stanbury et al. (2017) ESM5, SHA256 \`3d876a92e68122f8594b320e0794a54c5e8c7306c5a0e6252cbc24776ce1d1c5\`, contains two header rows and **9,688** island status records, linked to the RSPB GIS with **9,688/9,688 original \`lowid\` matches**. Only 8,632 original names match literally after normalization, hence direct key matching was essential.

**Publisher original four-way status legend:** 1 = Confirmed, 2 = Probable, 3 = Possible/incidental, **0 = Assumed OR known absent**, not verified surveyed absence. Historic dates and actual survey effort for all original island status labels are not demonstrated. No missing island status is converted to confirmed unoccupied.

The previously quoted source denominator “506 islands >10 ha” is reproduced only using **low-water (MLWS)** island area, **506 islands**, NOT the high-water (MHWS) area, **401 islands**. For low-water >10-ha islands:
- American mink original confirmed/probable: **113/506 = 22.33%** (source published approximately 23%);
- Brown rat original confirmed/probable: **106/506 = 20.95%** (source published approximately 21%).

This independent denominator cross-check validates the original workbook parsing. It does not validate each animal's presence at the breeding site or in 1998–2005 or 2015–2021.

Primary sources: [RSPB public GIS](https://services1.arcgis.com/h1C9f6qsGKmqXsVs/arcgis/rest/services/Islands_database/FeatureServer/0), [Stanbury original supplement](https://media.springernature.com/original/springer-static/esm/art%3A10.1007%2Fs10344-017-1084-7/MediaObjects/10344_2017_1084_MOESM5_ESM.xlsx), [Stanbury article DOI](https://doi.org/10.1007/s10344-017-1084-7).

## 2. Original-data predator reported-status model (V34)

Fixed source-only features: log(1 + island high-water area, ha), log(1 + 2014 human residents), any ferry service. Penalized logistic regression \`C=1.0\`, standard-scaled numeric inputs and five \`GroupKFold\` held-out *source-defined archipelago* groups; compare Brier against the fold's training-prevalence baseline, separately model “confirmed only” and “confirmed/probable.” The complement includes unverified absent labels and thus is a **reporting-status comparator**, never surveyed ecological nonoccurrence.

| Published original mammal status label | Positive source islands / 9,688 | 5-fold equal-mean held-out Brier gain (positive = better) | Folds better than baseline |
|---|---:|---:|---:|
| Mink confirmed | 1,507 | -0.001198 | 3/5 |
| Mink confirmed/probable | 2,404 | -0.006366 | 1/5 |
| Brown rat confirmed | 1,582 | -0.000284 | 4/5 |
| Brown rat confirmed/probable | 1,648 | +0.001377 | 3/5 |

Sample class balance is uneven by original archipelago (largest group is ~34.6% of all island points). Some held-out folds contain **zero positive source labels**. The source-only models do **not** establish a portable ecological niche from only area, human population and ferry access, and do not identify predator establishment, true absence, extinction, survival or causes of predation.

**Specific data-quality problem:** The original ESM5 labels **1,494 mink** and **1,520 brown rat** as “confirmed” among **7,025 islands smaller than 0.1 ha high-water area**. Do **not** interpret this as direct modern field confirmation of persistent populations on that many tiny rocks; source coding provenance/group inheritance, categorization and geometry/time differences must be audited independently. Changing the island-area subset to optimize apparent niche effects is not allowed.

Authentic Actions [V34 real-source run](https://github.com/zuizui0223/mina/actions/runs/40436974665); machine-readable first-party summary: \`results/JNCC_PREDATOR_REPORTED_NICHE_V34_SOURCE_RESULT.json\`.

## 3. The *pre-outcome* JNCC × predator island join

Question: can one compare two or more verified physical landmasses bearing JNCC sub-sites *within the same original species × Country × Master site × unit network*? The V30 baseline 1,483 structurally eligible JNCC networks and 9,821 child site records were selected without opening census magnitude cells. Site coordinates may be original reference points, not verified nest polygons. A candidate landmass must contain **exactly one** original RSPB island \`lowid\` point; all component JNCC points must be strictly interior, without coast snapping; large continental/major landmasses cannot borrow offshore source predator labels.

| Frozen comparison | Coarse Natural Earth 10m (V35) | Primary pinned GSHHG **full L1** (V36) |
|---|---:|---:|
| Source landmass polygons in UK/Ireland ROI | 98 | 3,206 |
| Unique-small-island physical polygons each carrying exactly one interior RSPB \`lowid\` | 20 | 700 |
| JNCC original child points strictly linked to one such island | 302 | 834 |
| Entirely source-mapped JNCC parent networks | 27 | 37 |
| Entirely mapped **mixed-physical-island** parent networks | **0** | **3** |
| Taxa among mixed parent networks | 0 | Common Tern; European Shag; Herring Gull |
| Mixed-parent networks with both mink confirmed/probable and other status | 0 | **0** |
| Mixed-parent networks with both brown rat confirmed/probable and other status | 0 | **1** |

For the full-resolution primary, the 3 complete geographically mixed parents cover **8 distinct original island IDs** and 3 species. Source QA: 4,587 original RSPB point interiors, 2,286 source coast-snapped, 690 unresolved, 2,125 ambiguous multiple polygons; 234 small mapped land polygons contain multiple original RSPB point IDs and are held, not arbitrarily assigned. Accordingly this is a **precision-limited strict lower bound on analyzable geographic units**, not a statement that only 3 actual inter-island movements exist.

A priori signed H2 within-parent refuga gate: >=20 fully mapped mixed-landmass parent panels, >=5 independent physical landmasses, >=5 taxa. **V36 fails on parent and taxon numbers: 3/20 and 3/5** (despite 8 distinct islands). The one brown-rat category contrast also lacks verified surveyed absence and period alignment. Thus **H2 mammalian-predator refuge redistribution is NOT IDENTIFIED, not refuted**. No correlation or causal beta is fitted against seabird E/shares to obtain a post hoc “positive” result.

Source original GSHHG archive v2.3.7 f L1 SHA256 \`8dbbe7e071e77e9e75f2d639239099ebca8d5c16d6a07df8169729d49f15cf41\`; do not substitute the coarser 8,264-unit >=5 km² island repository analysis-universe for UK rocks. First-party workflow [V35](https://github.com/zuizui0223/mina/actions/runs/40437554346), [V36](https://github.com/zuizui0223/mina/actions/runs/40438230884); source summaries \`results/JNCC_PREDATOR_NATURAL_EARTH_SOURCE_GEO_SUPPORT_V35.json\`, \`results/JNCC_PREDATOR_GSHHG_F_L1_ORIGINAL_GEO_SUPPORT_V36.json\`.

## 4. Ecological consequences and stop/continuation decision

**Established now:** a large, genuinely primary-sourced joined UK island-predator record dataset (9,688 ID matches), independent first-pass reported-label models with poor geographic transfer, a recovered 506-island source denominator, and a rigorous geographic impossibility of identifying H2 *under the frozen strict comparison criteria*, even at GSHHG full resolution. This is an inspectable geographic/measurement constraint, not a novel demonstration that predators control seabird concentration.

**Not supported:** transferring the V30 62.25% excess concentration to predation; identifying island escape from two censuses; treating 0 as verified predator absence; using species nesting form alone as predator mortality evidence; using an Antarctic penguin system as a causal mammalian predator-free control. Antarctica still has skuas and other nonmammalian predation; its observation processes and count-error null differ from the idealized multinomial JNCC source.

**Next viable ecological work:** The immediate predator H2 component needs independent original colony/nest footprint, local mammal accessibility (burrow/ground vs truly inaccessible cliff and nest-site surveyed absence), verified period-specific predator status or eradication chronology and within-network contrasts on the **same observation programme**. Until available, freeze H2 as NOT_IDENTIFIED. Other predefined V32 tests (H1 baseline size/social retention and H3 independent habitat quality) are conceptually separate, may proceed only after their own no-outcome-leakage source and statistical gates. Do **not** loosen mixed-island eligibility retrospectively, snap coast coordinates or use “island vs mainland” as if it directly measured mammal predation.

**PR and paper separation:** [PR #201 draft](https://github.com/zuizui0223/mina/pull/201) preserves JNCC V30 original descriptive result in PR #198 and frozen Penguin Ecology PR #189. This V33–V36 paper lane is exploratory source-first measurement work and cannot be presented as an independent prospective confirmation of V30.
