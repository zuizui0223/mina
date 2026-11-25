# V14 — An independently published Ross Sea 2026 census shows regional growth alongside Royds under-recovery

**2026-10-10; independent source audit and post-outcome descriptive reanalysis, NOT a new biological effect.** Maintains ecological submission PR189 frozen. This document supplements V12 theoretical reproductive-history aliasing with **actual independent archive source counts**; **not necessarily independent survey observations**, because the new regional data can reuse counts underlying previous Ross studies.

Original author dataset [Anderson et al. (2026), Adélie penguin census data, DOI 10.7931/kf06-x745](https://doi.org/10.7931/kf06-x745), Landcare NZ DataStore, CC-BY-NC 4.0, official XLSX resource `5fd490e5-92c4-4f2c-a82e-c66db2320eb1`, verified original MD5 **195a9027a0d18012812b09fb345ac60e**.

## Source quality and actual time coverage

The [source-validated sampling audit #38014975839](https://github.com/zuizui0223/mina/actions/runs/38014975839) successfully retrieved the **actual original 2026 XLSX**, with **39 named census site units** and year columns 1981–2024 (**44 years**). Among 39×44=1,716 unit-years, original records have **522 positive numeric pair counts**, **two explicit source zeros**, **1,192 unrecorded cells**. An explicit zero is not silently exchanged with a source blank or a biologically well-surveyed true empty site. The workbook has **305 consecutive within-site pairs of recorded years**; many site-years have missing information. The published 2020 column has no numeric observations in the focal 2020 time slice (check completeness before any COVID interpretation).

**Cape Barne is absent from the source's 39-name roster; do NOT infer any Cape Barne zero, continued abandonment, or colonization from this data source.** Geographic site names also differ in survey subdivisions (Cape Crozier West/East, Cape Bird North/Middle/South). These are **six site units on Ross Island, not six independent Antarctic islands**.

A local code path verifies the CKAN official metadata first, then verifies the original XLSX MD5, parses original native source year/colony cells and distinguishes missing, explicit zero, reported number and source text; no remote XLSX is committed or redistributed.

## A fixed six-site exact paired survey contrast

Within the six named Ross Island site units listed below, all three selected years **1999, 2001 and 2024** have actual nonmissing source breeding-pair counts.

| Ross Island census site | 1999 reported pairs | 2001 | 2024 | 2024 vs 1999 |
|---|---:|---:|---:|---:|
| Cape Bird Middle | 3,333 | 1,834 | 3,937 | **+18.1%** |
| Cape Bird North | 32,353 | 17,334 | 44,118 | **+36.4%** |
| Cape Bird South | 11,664 | 7,149 | 16,629 | **+42.6%** |
| Cape Crozier East | 17,055 | 7,944 | 20,494 | **+20.2%** |
| Cape Crozier West | 139,386 | 59,170 | 222,187 | **+59.4%** |
| **Cape Royds** | **3,620** | **1,367** | **3,058** | **−15.5%** |
| **Six source sites, same denominator in each year** | **207,411** | **94,798** | **310,423** | **+49.7%** |

These are independently archived *breeding-pair counts*, not marked bird survival or successful chicks. The six-unit total fell **54.3%** between 1999 and 2001, and 2024 was **49.7% above** 1999. Site recovery was unequal: Royds remained smaller than its 1999 count, whereas the other five Ross Island components were larger.

Under a purely descriptive **constant-1999-proportions counterfactual** (multiply every named 1999 count by `310423/207411 = 1.49666`), Royds would have **5,418** 2024 breeding pairs, vs **3,058 observed** — a descriptive deficit of **2,360** pairs relative to proportional growth, **NOT** an estimate of deaths, migrants or missing nesting opportunities. Royds' share of these six counted sites shrank from **1.745%** to **0.985%** (about **56.4%** of its earlier relative representation).

**Cape Crozier West accounts for 80.4% of the six-site *net gain* between 1999 and 2024** (82,801 of 103,012 pairs), although strong spatial growth heterogeneity is already related to the PR189 research result and Ross Sea population literature. Do not treat the concentration of net change as a novel ecology law.

## A useful size-related falsification, still not causality

The **1999 baseline sizes** of Royds (3,620 pairs) and Bird Middle (3,333 pairs) are remarkably close, yet their 2024 ratios diverge (**0.845 vs 1.181**). Starting census size **alone** cannot explain this particular two-site difference. However **2001 shock magnitude differs**: Royds fell 62.2% between 1999–2001 while Bird Middle fell 45.0%; sites also differ in sea access, microhabitat, predator geography, count methods, exchange of visitors and demographic history. This is NOT a matched causal design, nor does it separate colonist supply from functional accessibility or inherited territory/physical memory.

The six site-year trajectories are legitimate independent **archive provenance** and better constraints on past-site recovery than model-generated annual zeros or fixed coordinates. But the original count data may overlap existing Ross-based manuscripts; verification of independent survey teams, sites and protocols remains outstanding. Restrict the claim to **descriptive source-verified site heterogeneity**.

## Scientific bottleneck / future falsification

The 2026 39-unit source **cannot** itself identify why one subsite lagged amid adjacent growth. Competing explanations include: lower effective arrival of prospective breeders, stage-dependent access to nearby waters, different site substrate/snow or nearby skua predation, and a state-dependent decision not to attempt breeding. These explanations must be distinguished using externally recorded arrival/first-egg/chick outcomes and marked adult origins; a two-column ratio or regression of neighboring pair counts does not identify a cause.

Even if Royds reoccupied old nesting patches, the source has **no nest-patch GPS**, no individual resights and no data from Cape Barne. No new island-colonization or social-memory mechanism established.

**Data source/licence:** Anderson et al 2026 DOI 10.7931/kf06-x745, CC-BY-NC 4.0. Derived noncommercial citation-ready summaries only, no original XLSX copied into the git repository.

**Reproducibility:**
- `contracts/ROSS_NZ_2026_39_COLONY_SOURCE_GATE_V13.json` (frozen before 2024 count exposure)
- `scripts/audit_nz_2026_ross_39_colony_census_source_v13.py` (official MD5/39×44 source classification, sampling support)
- `contracts/ROSS_2026_AERIAL_SIX_SITE_PROPORTIONAL_RECOVERY_V14.json` (clearly *post-exposure* site contrast)
- `scripts/audit_ross_2026_six_site_recovery_benchmark_v14.py` and its tests/workflow
- [Six site counts reproducibility Action #38015174826](https://github.com/zuizui0223/mina/actions/runs/38015174826) **success**

**Current verdict:** Spatially nonuniform recovery reverified on a newly identified full census source. Not new causal evidence; keep PR193 exploratory, Ecology PR189 scientifically frozen and marked-data PR142 blocked pending official author source.
