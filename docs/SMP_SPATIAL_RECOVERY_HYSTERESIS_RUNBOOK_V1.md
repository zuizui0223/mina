# SMP spatial-recovery hysteresis execution runbook v1

**Date:** 2026-10-05  
**Branch:** \`research/smp-spatial-recovery-hysteresis-v1\`  
**Status:** canonical execution runbook before SMP effect magnitudes are opened.

## Goal

Execute one prospective test of whether the same breeding sites show asymmetric population states at spatial loss and later recovery.

The primary measured quantities are annual **transition-state proxies**, not exact continuous-time thresholds.

No later stage is authorized if an earlier stage fails.

---

# Required provider inputs

## 1. Raw SMP extract

A Colony Count / Whole Colony Count extract for the provider-confirmed compatible period, ideally within 1986–2024.

Required fields include:

- Species;
- SiteID;
- Site;
- MasterSite;
- Unit;
- Count;
- Accuracy;
- year/date;
- Plot/spatial-level indicator where available;
- Method;
- Estimate;
- Comments.

## 2. Site-history / physical-identity resolution

Fill the provider/site-history table used by:

\`scripts/finalize_smp_spatial_recovery_structure_v1.py\`.

For every candidate SiteID resolve:

- provider-confirmed \`master_site_key\`;
- MasterSite physical identity;
- stable SiteID identity;
- mutually exclusive child status;
- overlap with parent/sibling;
- boundary change;
- retirement/replacement;
- canonical Unit if multiple Units remain.

Do not infer any of these from occupancy or abundance trajectories.

## 3. Zero-semantics confirmation

Complete a private copy of the frozen zero-semantics template using official SMP documentation or provider correspondence.

All must be confirmed:

- direct observed Count = 0 is a surveyed nil return;
- absent SiteID × year is not biological zero;
- estimated/imputed zeroes can be excluded;
- compatible start/end years;
- compatible record family/era.

If this cannot be established prospectively, stop.

---

# Stage A0 — count-blind candidate structure

Run:

~~~bash
python scripts/gate_smp_spatial_recovery_hysteresis_structure_v1.py \
  --input <SMP_RAW_EXTRACT> \
  --out build/SMP_SPATIAL_RECOVERY_CANDIDATE_STRUCTURE_V1.json
~~~

Use \`--assume-whole-colony-extract\` only with explicit provider confirmation.

## Required support

- >=10 candidate species × MasterSite panels;
- >=10 distinct MasterSites;
- >=5 species;
- each retained panel >=3 SiteIDs;
- >=10 complete years;
- >=12-year span.

No occupancy state or abundance magnitude may be exposed.

If fail: **STOP**.

---

# Stage A1 — provider identity resolution

Run:

~~~bash
python scripts/finalize_smp_spatial_recovery_structure_v1.py \
  --support-json build/SMP_SPATIAL_RECOVERY_CANDIDATE_STRUCTURE_V1.json \
  --identity-resolution-csv <FILLED_IDENTITY_CSV> \
  --out build/SMP_SPATIAL_RECOVERY_STRUCTURE_V1.json
~~~

Required:

- \`analysis_id = mina-smp-spatial-recovery-structure-v1\`;
- \`decision.structural_gate_passed = true\`;
- one provider-resolved physical \`master_site_key\` per retained panel;
- every retained SiteID passes all identity/mutual-exclusivity rules.

The inherited complete-year set may shrink but cannot be extended because of SiteID removal.

If fail: **STOP**.

---

# Stage A2 — freeze zero semantics

Freeze the provider-confirmed zero-semantics JSON.

If zero semantics are valid only for a narrower time interval, subsequent stages are restricted to inherited Stage-A complete years inside that interval.

The interval can shorten but never extend the candidate observation window.

If confirmation fails: **STOP**.

---

# Stage B — state-only loss/recovery histories

Run:

~~~bash
python scripts/gate_smp_spatial_recovery_hysteresis_support_v1.py \
  --input <SMP_RAW_EXTRACT> \
  --support-json build/SMP_SPATIAL_RECOVERY_STRUCTURE_V1.json \
  --zero-semantics-json <FILLED_ZERO_SEMANTICS_JSON> \
  --out build/SMP_SPATIAL_RECOVERY_HYSTERESIS_SUPPORT_V1.json
~~~

At this stage Count is reduced only to:

- occupied = direct observed count \(>0\);
- vacant = provider-confirmed direct count \(=0\);
- missing/unusable.

Missing is never zero.

## Completed spell

A completed spell is:

\[
1\rightarrow0\rightarrow\cdots\rightarrow0\rightarrow1
\]

with every year from loss through recovery calendar-consecutive and state-complete.

First colonization is excluded.

## Structured-null support

Each spell is assigned to the maximal calendar-consecutive state-complete block containing it.

Only spells in blocks of at least 6 years enter Stage C.

## Required Stage-B support

After all identity, zero-semantics, state-completeness and phase-block filters:

- >=30 completed spells;
- >=20 distinct SiteIDs;
- >=10 distinct provider-resolved physical MasterSites;
- >=5 species;
- >=4 species with >=3 spells;
- >=3 species with spells in >=2 physical MasterSites.

If fail: **STOP BEFORE MAGNITUDE OPENING**.

## Freeze receipt before Stage C

Before proceeding:

1. archive the exact Stage-B JSON;
2. calculate SHA256;
3. verify no count magnitudes or \(H\) values appear;
4. preserve provider zero-semantics provenance;
5. never change the frozen spell roster afterward.

---

# Stage C — one magnitude-opening execution

Run exactly once:

~~~bash
python scripts/run_smp_spatial_recovery_hysteresis_v1.py \
  --input <SMP_RAW_EXTRACT> \
  --structural-json build/SMP_SPATIAL_RECOVERY_STRUCTURE_V1.json \
  --cycle-json build/SMP_SPATIAL_RECOVERY_HYSTERESIS_SUPPORT_V1.json \
  --out-json build/SMP_SPATIAL_RECOVERY_HYSTERESIS_RESULT_V1.json \
  --out-spells-csv build/SMP_SPATIAL_RECOVERY_HYSTERESIS_SPELLS_V1.csv
~~~

For focal SiteID \(j\),

\[
N_{-j,t}=\sum_{k\neq j}n_{k,t}.
\]

For the two annual censuses bracketing spatial loss,

\[
A_e=
\frac{
\log(1+N_{-j,t})+
\log(1+N_{-j,t+1})
}{2}.
\]

For the two annual censuses bracketing later recovery,

\[
A_c=
\frac{
\log(1+N_{-j,u})+
\log(1+N_{-j,u+1})
}{2}.
\]

Then

\[
H=A_c-A_e.
\]

\(A_e\) and \(A_c\) are annual transition-state proxies. They are **not** direct observations of the within-year demographic threshold.

Aggregate in this frozen order:

1. repeated spells within SiteID;
2. SiteIDs within provider-resolved physical MasterSite;
3. physical MasterSites within species;
4. species with equal weight.

Primary observed statistic:

\[
T_{\mathrm{obs}}
=
\mathrm{mean}(\text{species mean }H).
\]

---

# Confirmatory gate 1 — species sign flip

Required:

\[
T_{\mathrm{obs}}>0
\]

and one-sided species sign-flip

\[
p_{\mathrm{sign}}\le0.05.
\]

If <=20 species, enumerate all sign configurations exactly. Otherwise use 100,000 frozen sign flips.

This gate alone cannot establish spatial-recovery asymmetry.

---

# Confirmatory gate 2 — structured common-phase null

Purpose: test whether positive \(H\) is explained by fixed loss/recovery dates aligning with a trending or autocorrelated surrounding-population trajectory.

For each provider-resolved physical MasterSite × identical contiguous state-complete block:

1. retain the full multivariate SiteID count trajectory;
2. retain all frozen spell event-year positions;
3. draw one common circular shift for the whole physical MasterSite/block;
4. apply that same phase to all eligible species, SiteIDs and spells sharing the block;
5. recompute \(H\);
6. aggregate through the same spell → SiteID → MasterSite → species hierarchy.

Use:

- 9,999 resamples;
- seed 20261005.

This preserves within-block marginal time series and cross-site covariance, and where blocks align it preserves shared cross-species local temporal structure.

The circular seam is accepted prospectively and is not tuned after results.

Required:

\[
\Delta_{\mathrm{phase}}
=
T_{\mathrm{obs}}
-
\mathrm{median}(T_{\mathrm{phase,null}})
>0
\]

and

\[
p_{\mathrm{phase}}\le0.05.
\]

---

# Final decision

## All four criteria pass

Required simultaneously:

1. \(T_{\mathrm{obs}}>0\);
2. \(p_{\mathrm{sign}}\le0.05\);
3. \(\Delta_{\mathrm{phase}}>0\);
4. \(p_{\mathrm{phase}}\le0.05\).

Allowed precise conclusion:

> **Later recovery of the same breeding sites was associated with higher surrounding population states than their earlier loss, beyond structured temporal alignment with the observed MasterSite abundance trajectories.**

Allowed program-level interpretation:

> **Population recovery did not simply retrace spatial collapse.**

Do not report exact continuous-time recolonization/extinction thresholds.

## Sign-flip passes, phase null fails

Conclusion:

> the apparent loss–recovery state asymmetry is compatible with temporal alignment on the observed population trajectories.

No hysteresis claim.

## Sign-flip fails / effect unresolved / support gate fails

The independent generalization is not supported.

The Antarctic penguin paper remains a bounded standalone result.

No rescue analysis.

---

# Mechanism boundary

Even with full support, do not claim that:

- Allee effects caused the pattern;
- conspecific attraction caused the pattern;
- public information was demonstrated;
- all habitat confounding was removed.

Same-site pairing removes fixed place identity.

The common-phase null controls structured temporal alignment with the observed abundance trajectories.

Neither removes time-varying habitat deterioration, predators, disturbance, management or demographic composition.

Preferred wording:

- spatial-recovery asymmetry;
- loss–recovery transition-state asymmetry;
- history-dependent spatial recovery;
- empirical loss–recovery state proxy.

---

# Immutable after Stage C opens

Do not change:

- SiteID identity rules;
- zero semantics;
- inherited complete-year rule;
- state-complete-year rule;
- vacancy-spell definition;
- minimum 6-year phase block;
- 30-spell / 20-SiteID / 10-MasterSite / 5-species support thresholds;
- leave-one-SiteID-out parent abundance;
- \(\log(1+N)\);
- annual transition midpoint;
- aggregation hierarchy;
- equal-species weighting;
- sign-flip rule;
- common circular phase-null family;
- 9,999 phase resamples;
- species/SiteID exclusions;
- vacancy-duration filters.

Any mechanism or moderator test requires independent data.
