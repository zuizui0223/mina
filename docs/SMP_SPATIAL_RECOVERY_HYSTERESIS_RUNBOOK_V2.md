# SMP spatial-recovery hysteresis execution runbook v2

**Date:** 2026-10-05  
**Branch:** \`research/smp-spatial-recovery-hysteresis-v2\`  
**Status:** canonical V2 execution runbook before any SMP hysteresis support/effect outcome.

## Goal

Execute one prospective test:

> **Does later recolonization of the same breeding SiteID occur at a higher surrounding population state than its earlier abandonment, beyond non-circular temporal placement on the observed local abundance trajectory?**

No later stage is authorized if an earlier stage fails.

## Step 0 — raw data custody

On receipt of the SMP bulk extract:

1. record filename, size and SHA-256;
2. preserve an untouched read-only copy;
3. do not manually browse count magnitudes;
4. do not inspect species abundance rankings or vacancy frequency interactively.

## Step 1 — count-blind candidate structure

Run:

\`\`\`bash
python scripts/gate_smp_spatial_recovery_hysteresis_structure_v1.py \
  --input <SMP_RAW_EXTRACT> \
  --out build/SMP_SPATIAL_RECOVERY_CANDIDATE_STRUCTURE_V1.json
\`\`\`

Count is dropped before panel selection.

If the structural minimum fails: **STOP**.

## Step 2 — provider physical-identity resolution

Use the frozen identity-resolution template and provider/site-history metadata.

Run:

\`\`\`bash
python scripts/finalize_smp_spatial_recovery_structure_v1.py \
  --support-json build/SMP_SPATIAL_RECOVERY_CANDIDATE_STRUCTURE_V1.json \
  --identity-resolution-csv <FILLED_IDENTITY_CSV> \
  --out build/SMP_SPATIAL_RECOVERY_STRUCTURE_V1.json
\`\`\`

Every retained SiteID must have stable physical identity and mutual exclusivity. Every retained panel must have one provider-resolved \`master_site_key\`.

If unresolved: **STOP**.

## Step 3 — provider zero semantics

Freeze the provider-confirmed zero-semantics JSON.

Required:

- direct Count=0 is surveyed nil;
- absent row is not zero;
- estimated/imputed zeros are excluded;
- compatible record era/year range is documented.

If unresolved: **STOP**.

## Step 4 — V1 state-only spell extraction

Use the frozen provider-confirmed state scanner only to identify completed spells and consecutive phase blocks:

\`\`\`bash
python scripts/gate_smp_spatial_recovery_hysteresis_support_v1.py \
  --input <SMP_RAW_EXTRACT> \
  --support-json build/SMP_SPATIAL_RECOVERY_STRUCTURE_V1.json \
  --zero-semantics-json <FILLED_ZERO_SEMANTICS_JSON> \
  --out build/SMP_SPATIAL_RECOVERY_HYSTERESIS_SUPPORT_V1.json
\`\`\`

At this stage Count is reduced only to positive / explicit zero / unusable.

No magnitude is retained.

## Step 5 — V2 non-circular shift support

Run:

\`\`\`bash
python scripts/finalize_smp_spatial_recovery_hysteresis_support_v2.py \
  --v1-support-json build/SMP_SPATIAL_RECOVERY_HYSTERESIS_SUPPORT_V1.json \
  --out build/SMP_SPATIAL_RECOVERY_HYSTERESIS_SUPPORT_V2.json
\`\`\`

For every physical MasterSite phase block, V2 freezes all common integer shifts that keep **every event year of every spell** inside the same observed consecutive block.

No circular wrap.

One common shift will later be shared across all spells in that block.

Each shift group requires at least 3 common shifts.

After that restriction, support must still include at least:

- 30 spells;
- 20 SiteIDs;
- 10 physical MasterSites;
- 5 species;
- 4 species with >=3 spells;
- 3 species spanning >=2 MasterSites.

If fail: **STOP BEFORE MAGNITUDE OPENING**.

## Step 6 — immutable pre-magnitude receipt

Before Stage C:

- commit/hash the identity-resolved structure;
- commit/hash zero-semantics confirmation;
- commit/hash V1 state-only spell output;
- commit/hash V2 shift-support output;
- record exact code SHA.

After this point the spell roster and V2 common shifts are immutable.

## Step 7 — one V2 magnitude-opening execution

Run exactly once:

\`\`\`bash
python scripts/run_smp_spatial_recovery_hysteresis_v2.py \
  --input <SMP_RAW_EXTRACT> \
  --structural-json build/SMP_SPATIAL_RECOVERY_STRUCTURE_V1.json \
  --v2-support-json build/SMP_SPATIAL_RECOVERY_HYSTERESIS_SUPPORT_V2.json \
  --out-json build/SMP_SPATIAL_RECOVERY_HYSTERESIS_RESULT_V2.json \
  --out-spells-csv build/SMP_SPATIAL_RECOVERY_HYSTERESIS_SPELLS_V2.csv
\`\`\`

For focal SiteID \(j\),

\[
N_{-j,t}=\sum_{k\ne j}n_{k,t}.
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

Aggregate:

1. repeated spells within species × MasterSite × SiteID;
2. SiteIDs within species × physical MasterSite;
3. physical MasterSites within species;
4. species with equal weight.

## Confirmatory gate 1

Require:

\[
T_{\mathrm{obs}}>0
\]

and one-sided species sign-flip

\[
p_{\mathrm{sign}}\le0.05.
\]

## Confirmatory gate 2 — V2 non-circular common-shift null

Use 20,000 simulations, seed 20261005.

For each physical MasterSite phase block:

- draw one Stage-B-frozen common shift;
- apply it to every spell in the block;
- do not wrap;
- leave observed abundance matrices unchanged;
- recompute the exact same \(H\) and hierarchy.

Require:

\[
\Delta_{\mathrm{shift}}
=
T_{\mathrm{obs}}-\operatorname{median}(T_{\mathrm{null}})>0
\]

and

\[
p_{\mathrm{shift}}\le0.05.
\]

Both gates must pass.

## V2 pre-data calibration boundary

At minimum synthetic replication:

- stationary FPR 3.3%;
- monotonic drift FPR 0%;
- reversible-threshold FPR 0%;
- moderate synthetic hysteresis recovery 0%;
- strong synthetic hysteresis recovery 100%.

Therefore V2 is intentionally conservative.

Do not weaken the test if real effects resemble the unresolved moderate calibration case.

## Final routing

### Both gates pass

Activate the integrated manuscript spine V2.

### Any gate fails

Do not add another null or mechanism analysis.

Keep the Antarctic penguin Ecology manuscript as the standalone paper.

## Immutable after Stage C opens

No changes to:

- physical identity rules;
- zero semantics;
- vacancy-spell definition;
- support thresholds;
- common-shift groups;
- allowed shifts;
- abundance transform;
- transition midpoint;
- leave-one-SiteID-out state;
- hierarchy;
- equal-species weighting;
- sign-flip rule;
- V2 null family;
- 20,000 null simulations;
- taxonomic/site subset.

Any mechanism analysis requires new independent information.
