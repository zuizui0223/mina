# SMP spatial-recovery hysteresis execution runbook v1

**Date:** 2026-10-05  
**Branch:** research/smp-spatial-recovery-hysteresis-v1  
**Purpose:** Execute the preregistered spatial-recovery hysteresis test without collapsing blind stages.

## Inputs

### Provider data extract

A raw SMP Colony Count / Whole Colony Count file, ideally covering 1986–2024.

The file must contain the fields required by the frozen structural scripts, including Species, SiteID, Site, MasterSite, Unit, Count, Accuracy, year/date, and the relevant Plot, Method, Estimate and Comments fields where available.

### Provider/site-history resolution

Fill:

submission/SMP_SITE_IDENTITY_RESOLUTION_TEMPLATE.csv

Required columns:

- species
- MasterSite
- SiteID
- master_site_key
- master_site_identity_confirmed
- stable_identity
- mutually_exclusive_child
- overlaps_parent_or_sibling
- boundary_change_during_panel
- retired_or_replaced
- canonical_unit
- notes

Every SiteID in the candidate structural roster must be resolved before Stage B.

### Zero-semantics confirmation

Copy and complete:

submission/SMP_ZERO_SEMANTICS_CONFIRMATION_TEMPLATE.json

Required:

- row_with_direct_count_zero_is_surveyed_nil = true
- absent_site_year_row_is_not_zero = true
- estimated_or_imputed_zero_excluded_from_primary = true
- non-empty confirmation_source
- compatible_start_year
- compatible_end_year
- non-empty compatible_record_family_or_era

Do not infer these values from ecological patterns.

---

# Stage A1 — candidate structure only

Run:

~~~bash
python scripts/gate_smp_spatial_recovery_hysteresis_structure_v1.py \
  --input <SMP_RAW_EXTRACT> \
  --out build/SMP_SPATIAL_RECOVERY_CANDIDATE_STRUCTURE_V1.json
~~~

Add --assume-whole-colony-extract only if the provider explicitly confirms that the supplied file contains only whole-colony/site-level records and no Plot/spatial-level field is present.

## Pass condition

The JSON must contain:

decision.structural_gate_passed = true

Minimum support:

- 10 candidate panels
- 10 distinct MasterSites
- 5 species
- each panel >=3 retained SiteIDs
- >=10 complete years
- >=12-year span

## If failed

Stop.

Do not lower thresholds, open positive/zero states, inspect abundance trends, or choose a different hierarchy after seeing count magnitudes.

---

# Stage A2 — provider identity resolution

Before any occupancy-state scan, fill the provider/site-history CSV using only provider metadata/crosswalk/history.

Run:

~~~bash
python scripts/finalize_smp_spatial_recovery_structure_v1.py \
  --support-json build/SMP_SPATIAL_RECOVERY_CANDIDATE_STRUCTURE_V1.json \
  --identity-resolution-csv <FILLED_IDENTITY_CSV> \
  --out build/SMP_SPATIAL_RECOVERY_STRUCTURE_V1.json
~~~

## Pass condition

decision.structural_gate_passed = true

Every retained panel must first resolve to exactly one provider-confirmed physical master_site_key. Every retained SiteID must then satisfy:

- stable identity
- mutually exclusive child
- no overlap with parent/sibling
- no boundary change during retained panel
- not retired/replaced

If multiple count Units survive for one species × MasterSite, a provider-defined canonical_unit is required before state opening.

## If failed

Stop.

Do not infer physical continuity from count trajectories or occupancy patterns.

---

# Stage A3 — freeze zero semantics

Complete:

submission/SMP_ZERO_SEMANTICS_CONFIRMATION_TEMPLATE.json

Save the provider-confirmed file separately, for example:

private/SMP_ZERO_SEMANTICS_CONFIRMATION.json

Do not replace the repository template with private provider correspondence.

The compatible time range can be narrower than 1986–2024.

If semantics differ among data eras or record families, use only the provider-confirmed compatible scope.

---

# Stage B — occupancy-state support only

Run:

~~~bash
python scripts/gate_smp_spatial_recovery_hysteresis_support_v1.py \
  --input <SMP_RAW_EXTRACT> \
  --support-json build/SMP_SPATIAL_RECOVERY_STRUCTURE_V1.json \
  --zero-semantics-json <FILLED_ZERO_SEMANTICS_JSON> \
  --out build/SMP_SPATIAL_RECOVERY_HYSTERESIS_SUPPORT_V1.json
~~~

This stage may read Count only to classify each usable direct record as positive or explicit zero. It must not retain or output count magnitude.

## Spell definition

A completed spell is:

\[
1\rightarrow0\rightarrow\cdots\rightarrow0\rightarrow1
\]

with no missing calendar year between abandonment and recolonization.

First colonization is excluded.

## Structured-null support

Every spell is assigned to its maximal calendar-consecutive state-complete block.

Only spells in blocks of at least 6 consecutive years enter Stage C.

## Pass condition

decision.hysteresis_magnitude_execution_authorized = true

Minimum Stage-B support:

- 30 phase-eligible completed spells
- 20 distinct SiteIDs
- 10 MasterSites
- 5 species
- 4 species with >=3 spells
- 3 species represented by spells in >=2 MasterSites

## Audit before Stage C

Before proceeding:

1. archive this exact Stage-B JSON;
2. compute and record its SHA256;
3. verify that completed_spells contains no count magnitudes;
4. verify provider-zero semantics provenance is copied into the receipt;
5. do not change the spell roster after this point.

## If failed

Stop.

Do not treat missing as zero, use a low-count vacancy threshold, bridge missing years, include first colonization, or lower support thresholds.

---

# Stage C — one magnitude-opening execution

Only after Stage B passes and its artifact is frozen:

~~~bash
python scripts/run_smp_spatial_recovery_hysteresis_v1.py \
  --input <SMP_RAW_EXTRACT> \
  --structural-json build/SMP_SPATIAL_RECOVERY_STRUCTURE_V1.json \
  --cycle-json build/SMP_SPATIAL_RECOVERY_HYSTERESIS_SUPPORT_V1.json \
  --out-json build/SMP_SPATIAL_RECOVERY_HYSTERESIS_RESULT_V1.json \
  --out-spells-csv build/SMP_SPATIAL_RECOVERY_HYSTERESIS_SPELLS_V1.csv
~~~

This is the first stage authorized to use count magnitudes for the ecological endpoint.

## Observed estimand

For focal SiteID \(j\),

\[
N_{-j,t}=\sum_{k\ne j}n_{k,t}.
\]

At abandonment:

\[
A_e=
\frac{\log(1+N_{-j,t})+\log(1+N_{-j,t+1})}{2}.
\]

At recolonization:

\[
A_c=
\frac{\log(1+N_{-j,u})+\log(1+N_{-j,u+1})}{2}.
\]

Then:

\[
H=A_c-A_e.
\]

Average:

1. spells within SiteID;
2. SiteIDs within MasterSite;
3. MasterSites within species;
4. species equally.

Primary observed statistic:

\[
T_{\mathrm{obs}}.
\]

---

# Confirmatory gate 1 — species sign flip

Required:

\[
T_{\mathrm{obs}}>0
\]

and one-sided species sign-flip

\[
p\le0.05.
\]

If <=20 species, enumerate all sign configurations exactly.

---

# Confirmatory gate 2 — structured temporal phase null

For each provider-resolved physical MasterSite × identical contiguous complete-year block:

- retain the full multivariate count trajectories;
- retain all frozen event-year positions;
- circularly shift the whole MasterSite/block by one common phase;
- apply the same shift across all eligible species, SiteIDs and spells sharing that block;
- preserve within-species cross-site covariance, spell dependence, and aligned cross-species temporal covariance.

Use 9,999 frozen resamples with seed 20261005.

Required:

\[
\Delta_{\mathrm{phase}}
=
T_{\mathrm{obs}}-\mathrm{median}(T_{\mathrm{phase}})>0
\]

and

\[
p_{\mathrm{phase}}\le0.05.
\]

---

# Final decision

## Supported only if both gates pass

Allowed conclusion:

> **Spatial recovery occurred at a higher surrounding population state than spatial loss at the same breeding sites, beyond generic temporal alignment with the observed population trajectories.**

Program-level interpretation:

> **Population recovery did not simply retrace the spatial pathway of collapse.**

## Sign-flip passes, phase null fails

Conclusion:

> apparent asymmetry is compatible with temporal alignment/drift.

No hysteresis claim.

## Support gate fails or Stage C is unresolved

The independent generalization fails or remains unavailable.

Submit/retain the Antarctic penguin result as a bounded standalone finding.

---

# Claims that remain prohibited even after a positive result

Do not claim:

- Allee effects were uniquely identified;
- conspecific attraction caused the pattern;
- public information was demonstrated;
- all habitat confounding was removed;
- first colonization equals recolonization;
- a universal threshold across species.

Preferred wording:

- spatial-recovery asymmetry
- transition-state asymmetry
- empirical loss–recovery threshold proxy
- history-dependent spatial recovery

---

# Frozen literature boundary

Already established before this test:

- Bled et al. 2011: persistence, first colonization and recolonization can differ in kittiwakes.
- Schippers et al. 2011: Allee effects can slow seabird recolonization in metapopulation models.
- Bennett et al. 2022: buffer effects can structure colonial seabird occupancy across growth, decline and recovery.
- Burger et al. 2019: dynamic island-biogeography theory can generate hysteresis.

Candidate novelty is therefore not the existence of these concepts.

It is the prospective multi-species **same-site paired measurement of abandonment versus later recolonization population states**, with a structured temporal-alignment null, linked to an independently discovered Antarctic penguin spatial-recovery anomaly.
