# SMP spatial-recovery operational guard supplement v1

**Date:** 2026-10-05  
**Status:** operational supplement added after the V3 scientific freeze.  
**Scientific design unchanged:** yes.

## Purpose

The V3 preregistration defines the scientific design. This supplement prevents
accidental execution out of order or with files that changed after Stage B.

It does not modify any ecological definition, threshold, weighting rule, null,
replication unit, or inferential condition.

## Required operational sequence

### 0. Record raw-file custody without parsing contents

Immediately on receipt, before opening the CSV/Excel file in a spreadsheet or notebook:

```bash
python scripts/record_smp_raw_custody_v1.py \
  --raw <SMP_RAW_EXTRACT> \
  --received-at <ISO8601_TIMESTAMP_WITH_OFFSET> \
  --provider-filename <ORIGINAL_PROVIDER_FILENAME> \
  --source-channel <TRANSFER_CHANNEL> \
  --out build/SMP_RAW_CUSTODY_V1.json
```

This utility reads bytes only to calculate SHA-256. It does not parse rows, columns, species, counts or zero frequencies.

Preserve the provider-delivered file unchanged after this receipt is created.

### 1. Run A0, A1, A2 and Stage B exactly as specified in the canonical runbook

Canonical scientific runbook:

`docs/SMP_SPATIAL_RECOVERY_HYSTERESIS_RUNBOOK_V1.md`

Do not open Stage C yet.

### 2. Create the immutable Stage-B freeze receipt

Run:

```bash
python scripts/freeze_smp_spatial_recovery_stageb_v1.py \
  --raw <SMP_RAW_EXTRACT> \
  --custody-json build/SMP_RAW_CUSTODY_V1.json \
  --candidate-json <A0_CANDIDATE_STRUCTURE_JSON> \
  --identity-csv <PROVIDER_IDENTITY_RESOLUTION_CSV> \
  --resolved-json <A1_RESOLVED_STRUCTURE_JSON> \
  --zero-json <A2_PROVIDER_ZERO_SEMANTICS_JSON> \
  --stageb-json <STAGE_B_SUPPORT_JSON> \
  --prereg-json results/SMP_SPATIAL_RECOVERY_HYSTERESIS_PREREGISTRATION_RECEIPT_V3.json \
  --repo-root . \
  --out build/SMP_SPATIAL_RECOVERY_STAGEB_FREEZE_V1.json
```

This step verifies:

- the raw extract SHA-256, byte size and local filename match the content-blind custody receipt;
- the custody receipt explicitly records that contents were not parsed or inspected;
- the raw extract SHA-256 matches the A0 receipt;
- A0 passed;
- A1 physical-identity resolution passed;
- A2 zero semantics passed;
- the exact A2 semantics embedded in Stage B match the provider-confirmed file;
- Stage B passed and authorized magnitude opening;
- every retained Stage-B spell has the required frozen common offsets;
- no H / abandonment-state / recolonization-state magnitude appears in Stage B;
- every V3 canonical scientific file still has the Git blob SHA pinned in the V3 preregistration receipt.

If any check fails, **STOP**.

## 3. Commit/archive the freeze receipt before Stage C

The freeze receipt hashes:

- raw extract;
- raw-custody receipt;
- A0 candidate structure;
- provider identity-resolution table;
- A1 resolved structure;
- A2 zero-semantics file;
- Stage-B support file;
- V3 preregistration receipt.

Do not edit any of these files after the freeze receipt is created.

## 4. Run Stage C only through the guarded launcher

Run:

```bash
python scripts/guarded_run_smp_spatial_recovery_stagec_v1.py \
  --raw <SMP_RAW_EXTRACT> \
  --resolved-json <A1_RESOLVED_STRUCTURE_JSON> \
  --stageb-json <STAGE_B_SUPPORT_JSON> \
  --freeze-receipt build/SMP_SPATIAL_RECOVERY_STAGEB_FREEZE_V1.json \
  --out-json build/SMP_SPATIAL_RECOVERY_HYSTERESIS_RESULT_V1.json \
  --out-spells-csv build/SMP_SPATIAL_RECOVERY_HYSTERESIS_SPELLS_V1.csv
```

The wrapper rechecks SHA-256 of the exact raw, resolved-structure and Stage-B files
before calling the frozen scientific Stage-C implementation.

If any file changed after Stage-B freeze, Stage C refuses to run.

## Direct invocation rule

For real SMP data, do **not** directly invoke:

`scripts/run_smp_spatial_recovery_hysteresis_v1.py`

Use it only through:

`scripts/guarded_run_smp_spatial_recovery_stagec_v1.py`

The direct script remains the frozen scientific implementation and is retained
for reproducibility and synthetic recovery audits.

## Why this supplement is not a scientific amendment

The V3 frozen design already requires archival freeze before magnitude opening.

This supplement merely makes that requirement machine-enforced by hashing and
input validation.

No biological outcome was opened before this supplement was added.
