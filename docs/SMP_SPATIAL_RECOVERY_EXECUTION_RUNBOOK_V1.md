# SMP spatial-recovery hysteresis execution runbook v1

**Status:** frozen execution order before receipt/opening of SMP count magnitudes.

## Goal

Execute the abandonment-versus-recolonization threshold test without changing the analysis order after ecological outcomes become visible.

## Required inputs

1. Raw SMP Colony Count / Whole Colony Count extract.
2. Provider/site-history resolution table based on:
   - `submission/SMP_SPATIAL_RECOVERY_IDENTITY_RESOLUTION_TEMPLATE.csv`
3. Provider/official zero-semantics confirmation based on:
   - `submission/SMP_SPATIAL_RECOVERY_ZERO_SEMANTICS_CONFIRMATION_TEMPLATE.json`

No later stage is authorized if an earlier gate fails.

---

## Stage A0 — raw count-blind structure

Run:

```bash
python scripts/gate_smp_spatial_recovery_hysteresis_structure_v1.py \
  --input <SMP_RAW_FILE> \
  --out build/SMP_SPATIAL_RECOVERY_RAW_STRUCTURE_V1.json
```

Use `--assume-whole-colony-extract` only if BTO/SMP explicitly confirms that the export contains Whole Colony / Site-level records only.

Required pass:

- >=10 structurally eligible species × MasterSite panels;
- >=10 distinct MasterSites;
- >=5 species;
- each retained panel has >=3 SiteIDs, >=10 complete years and >=12-year span.

If fail: **STOP**.

Forbidden at this stage:

- count magnitudes;
- zero/positive occupancy histories;
- abundance trends;
- concentration or hysteresis outcomes.

---

## Stage A1 — SiteID identity resolution

Complete the provider/history table before looking at occupancy states.

Every retained SiteID must resolve:

- stable physical identity;
- mutually exclusive child;
- no overlap with parent/sibling;
- no boundary change during panel;
- not retired/replaced.

Run:

```bash
python scripts/finalize_smp_spatial_recovery_structure_v1.py \
  --support-json build/SMP_SPATIAL_RECOVERY_RAW_STRUCTURE_V1.json \
  --identity-resolution-csv <IDENTITY_RESOLUTION_CSV> \
  --out build/SMP_SPATIAL_RECOVERY_STRUCTURE_V1.json
```

Required output identity:

- `analysis_id = mina-smp-spatial-recovery-structure-v1`
- `status = identity_resolved_count_blind_structure`
- `structural_gate_passed = true`

The exact inherited complete-year set is retained after SiteID removal. Do not extend the time window.

If fail: **STOP**.

---

## Stage A2 — zero semantics confirmation

Fill:

`submission/SMP_SPATIAL_RECOVERY_ZERO_SEMANTICS_CONFIRMATION_TEMPLATE.json`

from BTO/SMP official documentation or provider correspondence.

All must be true:

- direct observed Count = 0 is a surveyed nil return;
- absent SiteID × year is not zero;
- estimated/imputed zeroes are excluded.

Also freeze:

- compatible start year;
- compatible end year;
- non-empty record-family/era description.

`confirmation_source` must be non-empty.

If any condition cannot be confirmed: **STOP**.

If semantics apply only to a narrower era, Stage B starts from inherited Stage-A complete years inside that interval. It then keeps only years with usable direct positive/explicit-zero state for every retained SiteID. Missing/unparseable records remove the year and are never zero. Panels falling below 10 state-complete years or a 12-year span are excluded before spell scanning. Do not infer zero semantics from ecological patterns.

---

## Stage B — state-only vacancy spell gate

Only now may count values be reduced to categorical state.

Run:

```bash
python scripts/gate_smp_spatial_recovery_hysteresis_support_v1.py \
  --input <SMP_RAW_FILE> \
  --support-json build/SMP_SPATIAL_RECOVERY_STRUCTURE_V1.json \
  --zero-semantics-json <ZERO_SEMANTICS_CONFIRMATION_JSON> \
  --out build/SMP_SPATIAL_RECOVERY_HYSTERESIS_SUPPORT_V1.json
```

Completed spell:

[
1 \rightarrow 0 \rightarrow \cdots \rightarrow 0 \rightarrow 1
]

with no missing year between abandonment and recolonization.

Each spell must lie inside a maximal contiguous frozen complete-year block of at least 6 years.

Required support after the phase-block filter:

- >=30 completed spells;
- >=20 distinct SiteIDs;
- >=10 MasterSites;
- >=5 species;
- >=4 species with >=3 spells;
- >=3 species represented by spells in >=2 MasterSites.

If fail: **STOP BEFORE MAGNITUDE OPENING**.

Forbidden Stage-B outputs:

- abandonment abundance;
- recolonization abundance;
- H;
- parent abundance trajectory;
- E / kappa / gamma.

Freeze and hash the exact Stage-B support JSON before proceeding.

---

## Stage C — one magnitude-opening execution

Run once:

```bash
python scripts/run_smp_spatial_recovery_hysteresis_v1.py \
  --input <SMP_RAW_FILE> \
  --structural-json build/SMP_SPATIAL_RECOVERY_STRUCTURE_V1.json \
  --cycle-json build/SMP_SPATIAL_RECOVERY_HYSTERESIS_SUPPORT_V1.json \
  --out-json build/SMP_SPATIAL_RECOVERY_HYSTERESIS_EFFECT_V1.json \
  --out-spells-csv build/SMP_SPATIAL_RECOVERY_HYSTERESIS_SPELLS_V1.csv
```

For focal SiteID j:

[
N_{-j,t}=\sum_{k\ne j} n_{k,t}
]

[
A_e=\frac{\log(1+N_{-j,t})+\log(1+N_{-j,t+1})}{2}
]

[
A_c=\frac{\log(1+N_{-j,u})+\log(1+N_{-j,u+1})}{2}
]

[
H=A_c-A_e.
]

Aggregation:

spell -> SiteID -> MasterSite -> species -> equal-species mean.

Primary observed statistic:

[
T_{obs}=\mathrm{mean}(\text{species mean }H).
]

---

## Primary inference

### Test 1 — species sign flip

- exact enumeration if <=20 species;
- otherwise 100,000 sign flips;
- one-sided positive direction.

### Test 2 — structured common-phase null

Within each species × MasterSite × contiguous phase block:

- circularly shift the entire multivariate SiteID count matrix by one common phase;
- all spells in that block receive the same shift;
- preserve cross-site covariance and block-level temporal structure;
- keep frozen event-year positions fixed.

Use 9,999 resamples, seed 20261005.

Confirmatory support requires all:

1. `T_obs > 0`
2. sign-flip one-sided `p <= 0.05`
3. `Delta_phase = T_obs - median(T_phase_null) > 0`
4. phase-null upper-tail `p <= 0.05`

Failure of any one condition means **no confirmatory hysteresis support**.

---

## Frozen interpretation table

### All four criteria pass

Allowed:

> Spatial recovery occurred at a higher surrounding population state than spatial loss at the same breeding sites, beyond generic temporal alignment with observed MasterSite abundance trajectories.

Allowed:

> Population recovery did not simply retrace spatial collapse.

Not allowed:

> Allee effects caused the result.

> Conspecific attraction caused the result.

### H positive but phase null fails

Conclusion:

> Apparent threshold asymmetry is compatible with temporal alignment on changing population trajectories.

No hysteresis claim.

### Sign-flip fails / H near zero / H negative

Conclusion:

> The independent SMP test does not support a general spatial recovery barrier.

Do not rescue with new thresholds, subsets, transforms or lags.

---

## Immutable after Stage C opens

Do not change:

- SiteID identity rules;
- explicit-zero semantics;
- complete-year set;
- vacancy-spell definition;
- minimum 6-year phase block;
- 30-spell / 20-SiteID / 10-MasterSite / 5-species support thresholds;
- leave-one-SiteID-out parent abundance;
- log1p transform;
- transition midpoint;
- aggregation hierarchy;
- equal-species weighting;
- sign-flip rule;
- circular phase-null family;
- 9,999 phase resamples;
- species/SiteID exclusions;
- vacancy-duration filters.

Any mechanism test requires independent data.
