# SMP spatial-recovery execution manifest v1

**Status:** frozen before receipt/opening of the requested SMP bulk extract.

## Goal

Execute one prospective test only:

> **Does recolonization of the same breeding SiteID occur at a higher surrounding population state than abandonment, beyond structured temporal alignment?**

## Hard execution order

### Step 0 — raw file custody

On receipt:

- record filename, byte size and SHA-256;
- make an untouched read-only copy;
- do not browse count values manually;
- do not sort species by abundance;
- do not inspect zero frequencies interactively.

### Step 1 — Stage A1 count-blind structure

Run only:

- schema check;
- direct/whole-colony record filtering;
- candidate species × MasterSite / SiteID support;
- missingness/year support;
- count Unit/method stability.

The Count column is dropped before panel selection.

Output:
- candidate frozen support JSON only.

### Step 2 — Stage A2 physical identity resolution

Obtain/freeze provider crosswalk before positive/zero states are opened.

Resolve:

- stable physical MasterSite key;
- SiteID continuity;
- merge/split/rename/boundary history;
- mutually exclusive child status;
- parent/aggregate overlap;
- canonical Unit if needed.

If provider identity metadata are inadequate, stop.

### Step 3 — zero-semantics confirmation

Freeze written provider/official confirmation that:

1. direct Count=0 is a surveyed nil;
2. absent SiteID × year is missing/not surveyed, not zero;
3. estimated/imputed zeroes can be excluded;
4. applicable years/record family are documented.

If not confirmed, stop.

### Step 4 — Stage B state-only scan

Only now convert Count to:

- positive;
- explicit zero;
- missing/unusable.

Do not retain magnitudes in output.

Freeze:

- state-complete years;
- completed 1→0→…→0→1 spells;
- contiguous state-complete blocks;
- one non-circular common-offset set per physical MasterSite × block;
- exact Stage-C-eligible spell roster.

Run replication gate.

If it fails, stop permanently. Do not lower thresholds.

### Step 5 — archival freeze before magnitude opening

Commit and hash:

- raw structural receipt;
- identity-resolved roster;
- provider zero-semantics confirmation;
- completed-spell roster;
- support-gate result;
- code commit used.

No Stage C until all are immutable in repository history.

### Step 6 — single magnitude opening

Run Stage C exactly once.

Calculate:

- leave-one-SiteID-out surrounding abundance;
- A_e;
- A_c;
- H = A_c - A_e;
- fixed hierarchical aggregation;
- species sign-flip;
- physical-MasterSite sign-flip;
- structured non-circular common-offset null.

### Step 7 — decision

Confirmatory support requires all:

- T_obs > 0;
- species sign-flip one-sided p <= 0.05;
- physical-MasterSite sign-flip one-sided p <= 0.05;
- Delta_linear > 0;
- linear-shift-null upper-tail p <= 0.05.

If any fail:

- no alternate threshold;
- no trait split;
- no region split;
- no alternative zero definition;
- no first-colonization rescue;
- no alternative common-offset/null model;
- no mechanism screen.

### Step 8 — manuscript routing

If both gates pass:
- activate `docs/REGISTERED_INTEGRATED_MANUSCRIPT_SPINE_HYSTERESIS_V1.md`.

Otherwise:
- retain current penguin Ecology manuscript as standalone;
- SMP becomes an independent null/falsification result.

## Forbidden before Stage C

Do not inspect:

- annual MasterSite totals;
- abundance trends;
- species-level abundance trajectories;
- SiteID counts beyond positive/zero state;
- E;
- kappa;
- gamma;
- H;
- environmental moderators;
- traits.

## Forbidden after Stage C

No new endpoint or rescue analysis on the same SMP extract.

Mechanism requires a separate new contract and independent information.
