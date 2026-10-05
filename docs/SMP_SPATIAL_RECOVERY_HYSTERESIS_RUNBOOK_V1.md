# SMP spatial-recovery hysteresis execution runbook v1

**Date:** 2026-10-05  
**Branch:** \`research/smp-spatial-recovery-hysteresis-v1\`  
**Status:** canonical execution runbook before SMP effect magnitudes are opened.

## Goal

Execute one prospective test:

> **Does later recolonization of the same breeding SiteID occur at a higher surrounding population state than its earlier loss, beyond generic temporal alignment on the same observed local abundance histories?**

The measured quantities are annual **transition-state proxies**, not exact continuous-time demographic thresholds.

No later stage is authorized if an earlier stage fails.

---

# Required provider inputs

## 1. Raw SMP extract

A Colony Count / Whole Colony Count extract within the provider-confirmed compatible period.

Required fields:

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

Before positive/zero states are opened, resolve:

- provider-confirmed physical \`master_site_key\`;
- stable SiteID identity;
- mutually exclusive child status;
- overlap with parent/sibling totals;
- boundary change;
- retirement/replacement;
- canonical Unit if multiple otherwise-valid Units remain.

Do not infer these from occupancy or abundance trajectories.

## 3. Zero-semantics confirmation

Freeze official/provider confirmation that:

- a direct observed Count = 0 is a surveyed nil return;
- absent SiteID × year is missing/not surveyed, not biological zero;
- estimated/imputed zeroes can be excluded;
- the compatible year interval and record family/era are documented.

If this cannot be established prospectively, **STOP**.

---

# Stage A0 — count-blind candidate structure

Run:

~~~bash
python scripts/gate_smp_spatial_recovery_hysteresis_structure_v1.py \
  --input <SMP_RAW_EXTRACT> \
  --out build/SMP_SPATIAL_RECOVERY_CANDIDATE_STRUCTURE_V1.json
~~~

Use \`--assume-whole-colony-extract\` only with explicit provider confirmation.

Required:

- >=10 candidate species × MasterSite panels;
- >=10 distinct MasterSites;
- >=5 species;
- each panel >=3 retained SiteIDs;
- >=10 complete years;
- >=12-year span.

The Count column is dropped before panel selection.

If fail: **STOP**.

---

# Stage A1 — provider physical-identity resolution

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
- one physical \`master_site_key\` per retained panel;
- every retained SiteID passes the frozen identity/mutual-exclusivity rules.

The inherited Stage-A year set may shrink but may never be extended after SiteID removal.

If fail: **STOP**.

---

# Stage A2 — freeze zero semantics

Create the provider-confirmed JSON matching:

\`contracts/SMP_SPATIAL_RECOVERY_ZERO_SEMANTICS_V1.json\`.

All three semantic booleans must be true and the applicable start/end years plus record-family description must be frozen.

If confirmation applies only to a narrower era, all later stages are restricted to inherited complete years inside that era.

If fail: **STOP**.

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

Counts are reduced only to:

- occupied = direct observed count \(>0\);
- vacant = provider-confirmed direct count \(=0\);
- missing/unusable.

Missing is never zero.

A completed spell is:

\[
1\rightarrow0\rightarrow\cdots\rightarrow0\rightarrow1
\]

with every year from loss through recovery calendar-consecutive and state-complete.

First colonization is excluded.

## Freeze the structured non-circular common-offset support

For every completed spell:

1. assign it to its maximal calendar-consecutive state-complete block;
2. group spells by **provider-resolved physical MasterSite × identical block**;
3. for every group, calculate the intersection of integer offsets that keep **all four event years of every group spell inside the same block**;
4. require observed offset 0;
5. prohibit circular wrapping;
6. retain the group only if it has >=3 common offsets.

All species/SiteIDs sharing one physical MasterSite/block use the same drawn offset in each Stage-C null replicate.

This support is frozen from identities and years only. No abundance magnitude is used.

## Required Stage-B replication support

After common-offset filtering require:

- >=30 eligible completed spells;
- >=20 distinct SiteIDs;
- >=10 physical MasterSites;
- >=5 species;
- >=4 species with >=3 spells;
- >=3 species with spells in >=2 physical MasterSites.

If fail: **STOP BEFORE MAGNITUDE OPENING**.

## Freeze receipt before Stage C

Before proceeding:

1. commit the exact identity-resolved structure JSON;
2. commit/hash the provider zero-semantics confirmation;
3. commit the Stage-B JSON and its exact spell roster;
4. verify all Stage-C spells have >=3 frozen common offsets including 0;
5. verify no count magnitude, \(A_e\), \(A_c\), \(H\), or null effect appears in Stage-B output;
6. record the code commit.

No Stage C until these are immutable in repository history.

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
N_{-j,t}=\sum_{k\neq j} n_{k,t}.
\]

For abandonment \(t\to t+1\),

\[
A_e=
\frac{\log(1+N_{-j,t})+\log(1+N_{-j,t+1})}{2}.
\]

For later recolonization \(u\to u+1\),

\[
A_c=
\frac{\log(1+N_{-j,u})+\log(1+N_{-j,u+1})}{2}.
\]

Then

\[
H=A_c-A_e.
\]

\(A_e\) and \(A_c\) are annual transition-state proxies.

Aggregate in the frozen order:

1. repeated spells within SiteID;
2. SiteIDs within physical MasterSite;
3. physical MasterSites within species;
4. species with equal weight.

Primary statistic:

\[
T_{\mathrm{obs}}=\mathrm{mean}(\text{species mean }H).
\]

---

# Confirmatory gate 1 — species sign-flip

Require:

\[
T_{\mathrm{obs}}>0
\]

and

\[
p_{\mathrm{sign}}\le0.05.
\]

For <=20 species enumerate every sign configuration exactly; otherwise use 100,000 frozen sign flips with seed 20261005.

This gate alone is insufficient.

---

# Confirmatory gate 2 — structured non-circular common-offset null

Purpose: test whether positive \(H\) is explained only by the frozen event dates occupying particular locations on trending/autocorrelated local abundance trajectories.

For each of 9,999 null resamples:

1. retain the complete frozen spell roster;
2. retain every observed multivariate count trajectory within each species × MasterSite;
3. for each **physical MasterSite × identical state-complete block**, draw one offset uniformly from its Stage-B-frozen common-offset set;
4. apply that same offset to all species, SiteIDs and spells sharing the group;
5. do not wrap across block boundaries;
6. recompute \(H\) from the shifted event dates;
7. aggregate through the identical spell → SiteID → physical MasterSite → species hierarchy.

Report:

\[
\Delta_{\mathrm{linear}}
=
T_{\mathrm{obs}}-
\mathrm{median}(T_{\mathrm{linear,null}})
\]

and the plus-one upper-tail probability

\[
p_{\mathrm{linear}}
=
P(T_{\mathrm{linear,null}}\ge T_{\mathrm{obs}}).
\]

Require:

\[
\Delta_{\mathrm{linear}}>0
\]

and

\[
p_{\mathrm{linear}}\le0.05.
\]

## Why circular shifts are prohibited

Before any SMP effect outcome was opened, the synthetic recovery audit showed that the earlier circular null falsely supported **40/40 monotonic-drift datasets** because the wrap seam manufactured extreme contrasts.

That failed design is preserved as provenance. It must not be reinstated after outcomes are known.

---

# Final decision

Spatial-recovery asymmetry is supported only if **all four** conditions hold:

1. \(T_{\mathrm{obs}}>0\);
2. \(p_{\mathrm{sign}}\le0.05\);
3. \(\Delta_{\mathrm{linear}}>0\);
4. \(p_{\mathrm{linear}}\le0.05\).

Allowed precise conclusion:

> **Later recovery of the same breeding sites was associated with higher surrounding population states than their earlier loss, beyond structured temporal alignment with the observed local abundance trajectories.**

Allowed program-level interpretation:

> **Population recovery did not simply retrace spatial collapse.**

Do not call \(A_e\) and \(A_c\) exact continuous-time thresholds.

## If sign-flip passes but common-offset null fails

Conclusion:

> the raw same-site asymmetry is compatible with temporal alignment on the observed abundance trajectories.

No hysteresis claim and no replacement null.

## If any support/effect gate fails

The independent generalization is not supported.

The Antarctic penguin manuscript remains the bounded standalone paper.

No rescue analysis.

---

# Mechanism boundary

Even with full support, do not claim that:

- Allee effects caused the pattern;
- conspecific attraction caused the pattern;
- public information was demonstrated;
- habitat quality is irrelevant.

Same-site pairing controls fixed place identity.

The structured non-circular common-offset null controls generic local temporal alignment while preserving shared local temporal covariance.

Neither removes time-varying habitat deterioration, predators, disturbance, management, or demographic composition.

Preferred terms:

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
- physical MasterSite/block grouping;
- minimum 3 common offsets;
- 30-spell / 20-SiteID / 10-MasterSite / 5-species support thresholds;
- leave-one-SiteID-out parent abundance;
- \(\log(1+N)\);
- annual transition midpoint;
- aggregation hierarchy;
- equal-species weighting;
- sign-flip rule;
- structured non-circular common-offset null;
- 9,999 null resamples;
- species/SiteID exclusions;
- vacancy-duration rules.

Any mechanism/moderator test requires independent data.
