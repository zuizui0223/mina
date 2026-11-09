# Ross Sea Adélie band/resight — observed transitions (research lane)

**Current as of 2026-11-09:** Original USAP-DC CSVs `601443` and `601444` were obtained from the user and matched their publisher MD5s. This branch is **Draft PR #212** (target: climate working branch PR #206, not main). It contains **aggregate evidence and source-reproduction code only**, not original band IDs or raw ZIP data. This is NOT a 2026-first discovery of breeding dispersal: Dugger et al. 2010 and 2026 already studied this Ross metapopulation by mark–recapture.

## Most useful present result

- Of **7,132** age≥2 chick-band individuals seen in the source, **506** were detected in another colony, and **64** had stricter egg/chick-bearing nesting observations outside their natal colony. **3** individuals were observed nesting in two different colonies in distinct breeding seasons. These are **observations, not movement/recruitment/settlement probabilities**.
- In the 64 birds with an observed foreign-colony nest, **23** had a prior-year resight at the *same future foreign nesting colony*; **41** were first detected there during a season when a strict nest was already recorded. Recorded lead gaps span **1–5 years** and first strict foreign nest median banding age is **6 years**.
- **All 23 prior-year foreign-colony resights were at Cape Crozier**, which dominates the observations. **14/23** also had earlier ambiguous possible-nesting status events, so the strict stage history **does not identify true first prospecting or first nesting**. Independent raw-source Pandas grouping reproduced the age, lead-year and stage counts; original raw files remain local.
- Accepted source resight events by colony: Crozier **80,437**, Royds **8,545**, Bird **5,693**, Beaufort **3** (36 colony-year cells in total). These are **record counts, not standardized search effort**. Consequently route-specific colonization rates, origin/destination preference and climate-resistance effects are **not identified**.

## Canonical readouts and implementation

- [Most recent observed-stage chronology](OBSERVED_STAGE_CHRONOLOGY_JA_20261109.md) — new 23 / 41 split, first-documented event timing, status ambiguity and source QA.
- [Prior 506 vs 64 observation and censoring audit](OBSERVABILITY_AND_STAGE_GATE_JA_20261108.md).
- [Original 64 nesting and 3 two-colony cases](VERIFIED_OBSERVED_NEST_MOVEMENT_JA_20261108.md).
- [Frozen post-result stage audit specification](FROZEN_OBSERVED_STAGE_SEQUENCES_20261109.md).
- [Rerunnable source reconstruction script](reconstruct_observed_nesting_movements.py) — accepts both original USAP-DC ZIPs at runtime, checks original published hashes, and exports aggregate-only CSV/JSON.
- [Safe aggregate source results](outputs/observed_stage_chronology_no_individual_ids.json) and [year-gap histogram](outputs/observed_foreign_visit_to_nest_gap_histogram.csv).
- [Aggregate CI success #42555275473](https://github.com/zuizui0223/mina/actions/runs/42555275473); this checks Python syntax, public aggregate reconciliation and conservative status parser without accessing private user-provided original ZIPs.

## Scope and next evidence gate

The biological question worth advancing is **when an observed foreign-colony visitor later nests there**, beyond what prior multistate capture–recapture models already explained. However **individual-specific observation histories, colony-year survey effort and detection probability** must first be handled jointly before any transition probability or causal climate linkage. Published prior art: [Dugger et al. 2026](https://doi.org/10.3389/fevo.2026.1868960), [Dugger et al. 2010](https://doi.org/10.1073/pnas.1000623107).

The already completed WAP Chinstrap Circuitscape source dates, ocean geography and species are different from these Ross Adélie observations. **Do not regress them together**, overclaim new dispersal biology, or generate future penguin nest counts from this audit. Warming manuscript v0.6, main and frozen Paper1/Paper2 unchanged.
