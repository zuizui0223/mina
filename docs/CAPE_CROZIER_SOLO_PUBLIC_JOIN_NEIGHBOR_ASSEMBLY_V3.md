# Cape Crozier linked spatial–fitness–resighting data: real join, novelty veto and temporal traps

**2026-10-08, mina PR #193 exploratory expansion.** Original source: [pointblue/solo_nests](https://github.com/pointblue/solo_nests), Cox et al. (2024) *Polar Biology*, DOI 10.1007/s00300-024-03246-9; archived Zenodo 10.5281/zenodo.8284755. Pin the exact public release commit `04517cedac18950408abd4d0b510f4aae3447f05`. All numbers below are source-stage observations; no new empirical causal result is claimed.

## Why the previous source gate needed correction

The earlier V2 inventory suggested no open Antarctic data with individual nest geography and outcome. **This was wrong in the limited sense of nest-grain identity:** Cox and coauthors provide 50 named solitary nests with WGS84 GPS coordinates, 2021 reproductive observations and the following 2022/23 checks sharing the **same nest identity**. They also report early neighbor presence, distance to the nearest existing subcolony, large shelter rocks and local area codes.

The published paper itself has already established:
- 36 active nests among 50 solitary site observations in 2021;
- 11 of the 36 nest sites had chicks directly confirmed in a crèche;
- chick survival or persistence from brood through crèche was much worse for solitary sites than matched/historical subcolonies;
- 20 of 41 reliably relocated historical solitary sites reoccupied in 2022; four local potential new subcolonies appeared near formerly solitary nests.

**None can be claimed as a new finding.** Reoccupancy of a *site* cannot identify return of the same unmarked adult versus recruitment of a new breeder.

## Source-reproduced original data join: CI #37784349818

Using source-vetted original CSVs without opening the 25-MB unrelated individual-resight table:
- **50/50** source `solo_outcomes.csv` nest IDs join exactly to `solonest_initial_locations.csv` GPS nest IDs.
- The author's `solonest_obs_data_entry_2223.csv` has **136** dated/undated repeated rows covering all **50** original nest IDs. It is 136 observation events, **not 136 independent nesting pairs**.
- Chronological audit: **104** follow-up rows within Oct 2022–Mar 2023, **5** with missing/unparseable dates, and **27** rows labelled **December 2023**, which post-date the August 2023 public source release. Their real observation season is therefore **unresolved**—most plausibly some are date-entry errors, but this has NOT been independently confirmed. They must not silently be interpreted as true 2023/24 sampling.
- Under a deliberately conservative raw status screen, classifying all rows yields **19** nest IDs with plausible site occupancy and **15** with directly documented active nesting, versus **18** and **13** respectively when accepting only in-window records. This is **not a reproduction or contradiction** of the authors' published **20/41** reoccupancy result, which excludes ambiguous/missing sites and follows different, prespecified status rules.
- Two of the 50 raw nest IDs (`40` and `47`) gain an **active** signal only from the out-of-season labelled rows. This is a **date-integrity sensitivity**, not inferred demographic recruitment.

## Potential new question — exploratory and weak

A limited within-source post-outcome screen asks whether **near neighbors first appearing before late-December hatching** correlate with confirmed crèche attendance. The question is not whether solitary nesting and success differ (already published) nor whether some solitary nests are followed by new subcolonies (already published); it asks whether *within-season social assembly* might alter the post-brood bottleneck, distinct from fixed nesting habitat.

A raw-source exploratory read using a fixed **December 1, 2021** cutoff yields:
- `n_neighbors > 0` in at least one observation by Dec 1 at **9 of 36** eligible initially solitary breeder sites;
- **5/9** among those sites versus **6/27** without recorded early neighbors had **directly confirmed** crèche observations;
- among nests with evidence of incubation/egg present by that date, **5/8** versus **6/26**;
- the two original groups have roughly comparable mean recorded distance to an existing subcolony (about 6.1 versus 6.2 m), though confounding by nest age, geography, rock shelter, colony microstructure, parental quality and surveillance remains uncontrolled.
- Direction also appears on Nov 24 and Dec 22 cutoff sensitivity, but group sizes vary substantially; there is NO confirmatory p-value or causal effect estimate.

**The temporal logic is limited.** Neighbor presence by December 1 is before the published median hatch date (Dec 23), **not necessarily before egg laying or prospecting**. Good sites or more persistent occupied territories can attract neighbors. Sites that fail early have less opportunity for neighbors to accumulate (*immortal-time/selection confounding*). `cr_confirm=0` is an absence of *direct confirmation*, **not** a guaranteed dead chick. This association cannot establish social rescue.

Dedicated source-pinned tests, receipt and CI:
- `contracts/CAPE_CROZIER_SOLO_NEST_SPATIAL_FITNESS_PUBLIC_JOIN_V1.json`
- `scripts/audit_cape_crozier_solo_nest_spatial_outcome_join_v1.py`
- `contracts/CAPE_CROZIER_EARLY_NEIGHBOR_CRECHE_EXPLORATORY_V1.json`
- `scripts/screen_crozier_early_neighbor_creche_v1.py`
- `.github/workflows/crozier-early-neighbor-creche-v1.yml`

The new neighbor screen is **separate from the source join's already-passed CI**; source raw values were previously inspected and it remains *exploratory*, regardless of subsequent workflow success.

## Scientific direction after this audit

There *is* an exact nest-level dataset. But the main colony-formation and fitness patterns have already been published, and it supplies neither independent predator counts, an externally dated breeding-habitat perturbation, nor marked breeder identities. The strongest as-yet unproven hypothesis is **whether early social assembly directly improves an isolated chick's survival across the brood-to-crèche transition, instead of being a consequence of favorable territories or early breeder success**.

A convincing next study needs independent replicated colonies with time-stamped initial nesting locations, neighbors forming **before** focal chicks leave nests, direct predator/fate observations, effort-corrected detection, and preferably marked adult origins. Otherwise this is a small, post-hoc, single-site candidate mechanism and not a new Antarctic island biogeography law.

Keep PR #189 frozen and PR #195 as a georeference/detection source audit, without claiming global causal generality from this single colony.
