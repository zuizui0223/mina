# V17 — Only two geographically matched off–Ross sites have 2001 and 2005 censuses

**2026-10-10, mina PR193**. Original NZ 2026 Adélie penguin counts (doi:10.7931/kf06-x745; CC-BY-NC 4.0), official census MD5 `195a9027a0d18012812b09fb345ac60e` and official location supplement without publisher MD5. Both source files re-fetched and paired by **literal** original census site identity, not fuzzy names or proximity. Technical reproduction: [GitHub Action #38038070701](https://github.com/zuizui0223/mina/actions/runs/38038070701) SUCCESS.

## Actual matched-source evidence

| Source geography | Number of source site rows observed in BOTH years | 2001 counted breeding pairs | 2005 | Raw ratio 2005/2001 |
|---|---:|---:|---:|---:|
| Ross Island (Bird N/M/S, Crozier E/W, Royds) | **6** | **94,798** | **254,617** | **2.686** |
| Off Ross Island with an exact literal location source identity (Franklin East, Inexpressible) | **2** | **28,947** | **35,912** | **1.241** |
| No literal match to publisher geographic location workbook (Terra Nova Bay) | **1** | **9,478** | **15,693** | **1.656** |

The **9** distinct paired 2001/2005 source site rows are not nine *independent islands*, and six of them are on a single Ross Island. Exact site evidence:

- Bird Middle **1,834→3,965**, Bird North **17,334→39,979**, Bird South **7,149→13,765**;
- Crozier East **7,944→24,203**, Crozier West **59,170→170,246**, Royds **1,367→2,459**;
- Franklin Island East **980→1,944**, Inexpressible Island **27,967→33,968**;
- Terra Nova Bay **9,478→15,693** but provider's site-location source lacks a literal matched location key.

The first *two* off-Ross records are geographical context, **not** a credible difference-in-differences control. Off-Ross 1999 original counts are absent, and 2024 has numerical counts only from six Ross Island source rows. The 2001 counts were already during the B-15/C-16 iceberg perturbation, not a common standardized pre-exposure time. Regional sites have different predation, sea ice, snow, biological species/demographics, count visibility and survey effort. The ratio-of-sums is *not* the average site-specific biological per-capita growth rate.

## Main ecological reason to stop an easy paper

The published prior literature already provides the specific cause relevant to this period:

- Dugger et al. (2010; [PNAS, DOI 10.1073/pnas.1000623107](https://doi.org/10.1073/pnas.1000623107)): iceberg-era environmental instability produced adult breeder dispersal **up to ~3.5%**, compared with ordinary annual breeding movements **under 1%**, with more movement away from the small Royds colony.
- LaRue et al. (2013; [PLOS ONE, DOI 10.1371/journal.pone.0060548](https://doi.org/10.1371/journal.pone.0060548)): Beaufort's glacier-retreat-mediated nesting area increase coincided with reduced post-2005 visitation/emigration to Ross Island, based on individual band observations. The effect of growing source habitat on emigrant retention is prior art.
- Lyver et al. (2014; [PLOS ONE, DOI 10.1371/journal.pone.0091188](https://doi.org/10.1371/journal.pone.0091188)): the full original 1981–2012 Ross Sea census trajectories and broad regional synchrony, density dependence and icebergs are prior art. Reanalysis of the **same 2001→2005 source years in a 2026 updated archive is not a new independent natural experiment**.

**Decision:** The new 2026 dataset adds well-verified source coverage through 2024 for Ross Island, but the 2001–2005 matched off-island *causal* contrast is structurally blocked by at most 2 geolocatable off-Ross sites, absence of off-Ross predisturbance values, nonmatched count protocol risks, and already-published marked penguin movement rates. No claim that a change in pairs is observed dispersal, true natal recruitment, or causal ice-access resistance.

The actual remaining high-information observation would be **arrival-stage** and **post-arrival decision-stage** data at marked birds and independent physical access sites, not additional paired pair-count regressions. Ecology PR189 frozen, USAP source PR142 and emperor/source PR195 untouched.

Contracts: `contracts/ROSS_2001_2005_MATCHED_OFFISLAND_SOURCE_SUPPORT_V17.json`. Script: `scripts/audit_ross_2001_2005_matched_offisland_source_v17.py`. Tests/workflow: `tests/test_ross_2001_2005_matched_offisland_source_v17.py`, `.github/workflows/ross-2001-2005-matched-offisland-v17.yml`.
