# Hierarchy story from the 66-endpoint ledger v1

**Source of truth:** `contracts/ENDPOINT_EVIDENCE_LEDGER_V1.json`  
**Snapshot:** `main@7764523c5f1e536b86084de8583cdd6262ee8fa7`  
**Scope:** exactly the 66 result files in `main/results/`; later branch-only cross-scale results are not folded back into this snapshot.

## One-sentence story

> **近隣個体群は長期的な減少方向を共有するが、その局所的な空間応答は島ごとに異なる。66 result recordsのうち、事前凍結の独立再現まで残った生態信号は、静的な島形質でも固定表現型でもなく、繁殖個体が少数の構成単位へ比例的間引き以上に集中する変化だけだった。**

This is intentionally weaker than “regional forcing determines direction.” The Palmer data establish a shared long-term direction, but the tested annual and low-frequency environmental formulations do not identify the causal regional driver.

## Why this story is not outcome cherry-picking

The repository contains 66 result files, but they are not 66 independent ecological tests.

- **35** are ecological outcome records (E1–E4).
- **31** are schema, coverage, recoverability, sensitivity, provenance or reproducibility records (A0).
- The **three E1 files all occur at the within-system spatial layer**.
- The three E1 files represent **two independent confirmatory lines**, because the two Signy Adélie results belong to one dataset/claim family.
- Static-place ecological outcomes are **E3 only**: no E1 or E2 positive ecological endpoint survives there.
- Mechanism endpoints split between E2 and E3 and never reach E1.
- The individual-process lane stops at E4 because public mark-resight data do not contain the required breeding-site bridge.

The story therefore follows the evidence matrix rather than selecting favorable endpoints after the fact.

## Evidence ladder

### Layer 1 — Regional direction: shared long-term trajectory, unresolved driver

**Evidence:** E2 = 2, E3 = 3.

The five Palmer Adélie island populations share a dominant multi-decadal decline component, while annual synchrony and local endpoints remain heterogeneous. This supports a regional common-direction context.

What fails are simple mechanistic reductions of that direction:

- preceding-year sea-ice duration;
- 3-, 5- and 7-year smoothed sea-ice duration;
- October snowfall × snow-prone habitat.

The appropriate inference is:

> **The long-term decline is regionally coherent, but it is not explained by the finite set of simple annual or smoothed environmental responses that were prospectively tested.**

Do not write that sea ice or snow is ecologically unimportant.

### Layer 2 — Static place: no transferable Antarctic-wide rule

**Evidence:** E1 = 0, E2 = 0, E3 = 5, A0 = 26.

This is the most asymmetric layer in the ledger. A large amount of work was required to make the static-place question identifiable—atlas construction, geographic support audits, forcing recovery, observation calibration, source sensitivity and predictor identifiability—but once real ecological outcomes were opened, every inferential result limits generality rather than establishing it.

The primary A × H interaction:

- has a negative point estimate in all three species;
- does not reject the frozen cross-species permutation null (p = 0.0947);
- has no Holm-significant species-specific effect;
- changes strongly with spatial radius;
- shows a raw 2 km → 5 km sign switch that is itself null-compatible;
- cannot be interpreted as absent at effect sizes around |0.3|;
- does constrain very large common effects around |0.5| or larger.

The defensible statement is:

> **Static breeding-space amount and habitat-option heterogeneity do not yield a confirmed transferable rule across the analyzed Antarctic Pygoscelis populations; large common effects are constrained, but moderate effects are not excluded.**

### Layer 3 — Species and phenotype: apparent island identity is largely compositional

**Evidence:** E2 = 2.

The original morphology-to-island signal is largely borrowed from species identity. Within Adélie penguins:

- fixed island effects are small;
- pairwise island rankings repeatedly reverse across years;
- cross-year island classification from morphology or isotopes is near chance.

This supports:

> **A single-season island phenotype can look persistent when species composition is mixed, but within-species island differentiation is temporally reassembled rather than stably transferable over the sampled years.**

It does not establish plasticity, local adaptation or a universal island-phenotype law.

### Layer 4 — Within-system breeding configuration: the only confirmatory layer

**Evidence:** E1 = 3 files / 2 independent confirmatory lines; E2 = 6; E3 = 1.

Palmer is the discovery system:

- Cormorant, Humble and Litchfield all lose effective breeding components beyond proportional thinning under the frozen count-error family.

The confirmatory weight comes from Signy:

- prospectively frozen Adélie replication;
- separately frozen chinstrap cross-species replication.

Those replications establish that the population-level concentration endpoint is not a Palmer-only accident.

Post-hoc bounded descriptions then show the boundary of the rule:

- Palmer reaches concentration via dominance turnover;
- Signy reaches it via dominant-core retention;
- all five local trajectories have positive abundance–E elasticity;
- a common descriptive κ is near 0.25;
- no universal quarter-power constant is supported;
- no universal 50/25/10% collapse threshold is supported.

The strongest statement in the 66-endpoint snapshot is therefore:

> **Declining Antarctic Pygoscelis populations can concentrate reproduction into fewer effective monitored breeding components more strongly than expected from proportional thinning alone, and this endpoint replicates across geography and species even though its magnitude and component-level route are not universal.**

## Layer 5 — Mechanism traces: informative, but none confirm

**Evidence:** E2 = 7, E3 = 5.

Several traces point toward spatial organization as a biologically meaningful state:

- N_eff retains a positive conditional association with next-year growth under circular-shift, count-error/mechanical-coupling and demographic-momentum diagnostics;
- past reproductive performance contains short-lag information about later redistribution in Palmer;
- short-term performance memory is detectable.

But each is bounded by a nearby negative result:

- the N_eff held-out predictive increment is null-compatible under year-block permutation (p = 0.262);
- the externally fixed >50-pair threshold has the wrong directional coefficient;
- a general reproductive/Allee-like mechanism is not supported;
- the specific win-stay/lose-switch asymmetry is not supported;
- Palmer lag-2 performance-linked redistribution does not independently replicate at Signy.

Thus:

> **The confirmed phenomenon is spatial reorganization; the individual or demographic mechanism producing it remains unresolved.**

## Layer 6 — Individual process: the data stop

**Evidence:** E4 = 1.

The public Palmer records located in the mark-resight audit contain band-source information and evidence that standardized resighting exists, but no reproducible public bridge from band ID to later breeding-site observations.

Therefore current data cannot distinguish:

- adult site retention;
- breeding dispersal;
- prospecting;
- immigration/emigration;
- temporary nonbreeding.

This is not a null ecological result. It is a data-structure boundary.

## The manuscript spine implied by the ledger

### Result 1 — Shared regional direction, divergent local endpoints
Use the five-island long-term decline and heterogeneous local fate as context, not as the novelty claim.

### Result 2 — Two attractive higher-level explanations fail to transfer
Put static island architecture and fixed island phenotype together as failed information carriers:

- static site traits do not produce a confirmed Antarctic-wide rule;
- phenotype-to-island information collapses after conditioning on species and year.

### Result 3 — Breeding configuration is the surviving replicated state variable
Make Palmer explicitly discovery and Signy explicitly confirmation.

### Result 4 — The same endpoint does not imply one local mechanism
Use Palmer turnover versus Signy core retention and the closed scaling exploration to show what is and is not general.

### Result 5 — Mechanistic probes narrow the space but do not identify movement
Pair every positive exploratory mechanism trace with its limiting E3 result.

### Discussion — Where is the information?
The answer is hierarchical:

1. **regional level:** information about long-term direction;
2. **static site level:** little confirmed transferable information;
3. **species level:** much apparent phenotype information;
4. **within-population spatial level:** the replicated information about decline shape;
5. **individual level:** currently unobserved.

## What should be in the main paper

### Main text
Only the evidence families needed for the hierarchy:

- Palmer five-island regional context;
- finite environmental falsifications;
- static-place macro null/bounds;
- phenotype decomposition;
- Palmer discovery concentration;
- Signy Adélie and chinstrap confirmation;
- one compact mechanism paragraph with the strongest E2/E3 pairings.

### Main evidence table
Use the six-layer evidence matrix from `docs/ENDPOINT_EVIDENCE_LEDGER_V1.md`, not all 66 rows.

### Supporting Information
Place the full 66-row ledger and non-independent evidence-family map there.

## Claim discipline

- **Do not say:** “66 endpoints independently support the story.”
- **Say:** “A frozen audit of 66 result records contains 35 ecological outcomes and 31 support/audit records; confirmatory evidence occurs only at the within-system spatial layer.”
- **Do not say:** “Regional forcing determines decline.”
- **Say:** “Neighboring populations share a long-term decline direction, while the tested simple annual and smoothed environmental formulations fail.”
- **Do not say:** “Static island traits have no effect.”
- **Say:** “No confirmed transferable static-place rule was detected; very large common effects are constrained, moderate effects are not excluded.”
- **Do not say:** “N_eff predicts decline.”
- **Say:** “N_eff retains a robust conditional association, but its held-out predictive gain is not stronger than the frozen year-block permutation null.”
- **Do not say:** “Performance causes dispersal.”
- **Say:** “Performance-linked redistribution is locally compatible with short-lived reallocation, but the primary independent Signy replication fails and individual movement is not observed.”

## Relationship to the later cross-scale branch

This document deliberately stops at the frozen 66-file main snapshot. The later MAPPPD regional concentration extension on `analysis/mapppd-regional-concentration-v1` is a separate bounded scale-transfer test and should be added only as a prospective update to this hierarchy, not retroactively counted among the original 66.
