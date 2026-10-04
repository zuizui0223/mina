# Paper 2 dynamic-island feasibility ledger v1

**Date:** 2026-10-04  
**Branch:** `research/antarctic-island-ecology-v1`  
**Purpose:** Keep the dynamic Antarctic island-ecology lane on one auditable path without reopening demographic outcomes or the closed Paper 1 endpoints.

## Core biological question

> **Can physical breeding opportunity expand while realized penguin breeding space contracts?**

The program separates three moving quantities:

[
A_{available,t},qquad A_{occupied,t},qquad N_t.
]

- (A_{available}): summer-exposed terrestrial breeding opportunity.
- (A_{occupied}): realized active breeding / guano footprint.
- (N): breeding abundance, still locked for the new dynamic analysis.

The high-value island-ecology pattern is:

[
Delta A_{available}>0
quad	ext{and}quad
Delta A_{occupied}<0.
]

This would establish land-space decoupling without requiring abundance to stand in for spatial occupation.

---

## Gate ledger

| Gate | Question | Frozen evidence | State |
|---|---|---|---|
| G0 demographic support | Is there a long-term outcome-blind site roster? | 107 site × species units, 88 physical sites | PASS |
| G1 static spatial support | Are candidate sites independently mapped as ice-free terrestrial nodes? | Existing breeding-options atlas covers the great majority of sites | PASS |
| G2 optical catalog | Do early and late optical records exist? | 106/107 units pass; 88-site broad STAC audit also passes | PASS |
| G3 local pixel support | Are locally usable optical pixels available in both epochs? | 77 physical sites / 94 site × species units pass; 3 large regional groups | PASS |
| G4 available-space metric recovery | Does the frozen metric recover a known positive control? | Beaufort: positive persistent-summer-exposure change at both 0.50 and 0.67 thresholds | PASS |
| G5 full available-space extraction | Can the same metric be measured across the frozen QA roster? | full 77-site extraction running | ACTIVE |
| G6 marine archive support | Is one compact marine-access lane available without outcome fishing? | NSIDC G02135 supports all 107 units; 103/105 required month-files present | PASS |
| G7 occupied-footprint reference overlap | Is there independent guano/colony reference support? | 22/44 long-term Adélie sites within 5 km of published reference colonies, concentrated in Victoria Land/Adélie Land | PASS for recovery, geographically bounded |
| G8 published classifier specification | Can the published guano classifier be reconstructed numerically? | Lynch & Schwaller ETM+ TOA transition matrix and rule recovered | PASS |
| G9 occupied-footprint sensor alignment | Can the classifier be applied longitudinally without unvalidated sensor transfer? | ETM+→OLI primary route not yet authorized; same-sensor ETM+ audit active | ACTIVE |
| G10 occupied-footprint measurement recovery | Does the frozen classifier recover independent footprint references above a frozen error threshold? | not yet tested | LOCKED |
| G11 dynamic spatial ecological test | Does available space track occupied space, or do they decouple? | no outcomes opened | LOCKED |
| G12 abundance/marine interpretation | Do abundance and marine access explain residual spatial change? | no new demographic outcome opened | LOCKED |

---

## What is already established methodologically

### 1. Archive availability is not the bottleneck

The frozen optical-catalog analysis supports 106/107 long-term Pygoscelis site × species units. This is already sufficient to reject the concern that the dynamic-land question collapses into a few hand-picked sites.

### 2. Local Antarctic image quality is not a fatal bottleneck

The stricter local-pixel gate passes at:

- **77 physical sites**;
- **94 site × species units**;
- **37 Adélie**;
- **32 chinstrap**;
- **25 gentoo**.

Regional replication remains broad enough for later analysis:

- Central-west Antarctic Peninsula: 33 physical sites;
- South Shetland Islands: 16;
- Victoria Land: 24.

Seven physical sites fail and remain excluded without rescue:
BISC, CUVE, HUMB, ORNE, PGEO, ROYD, SHIR.

### 3. The available-space metric has an external directional control

At Beaufort Island, the frozen persistent-summer-exposure metric recovers positive terrestrial change without using penguin counts:

- threshold 0.50: 0.0423 → 0.0979, delta = +0.0556;
- threshold 0.67: 0.0060 → 0.0387, delta = +0.0326.

The high-sensitivity any-exposed diagnostic is also positive.

This does **not** show that the metric measures literal nesting area. It shows that the fixed outcome-blind pipeline is capable of recovering the direction of a previously documented habitat-expansion case.

### 4. The marine side is technically available

The frozen NSIDC monthly sea-ice archive supports all 107 candidate site × species units. Two required historical month-files are missing and remain missing rather than being imputed.

This only authorizes a compact marine-access calculation after the terrestrial spatial measurement closes. It is not evidence that sea ice explains the demographic pattern.

---

## Active bottleneck: realized occupied breeding footprint

The new Paper 2 should not substitute abundance for spatial occupation if a direct occupied-footprint measure can be recovered.

### Why the published guano route is attractive

Published Landsat work supplies:

- a numeric ETM+ TOA classifier specification;
- an independent colony/reference set;
- overlap with **22/44** long-term Adélie sites at the frozen 5 km matching radius.

This gives a real measurement-recovery set rather than a classifier trained against the same demographic series used later for inference.

### Why the direct ETM+→OLI route is not yet acceptable

The recovered classifier was defined for Landsat-7 ETM+ top-of-atmosphere reflectance. OLI/OLI-2 have different spectral response functions.

Therefore:

> **Do not classify OLI pixels with the ETM+ coefficients merely because the output looks plausible.**

A cross-sensor route requires a separately validated spectral bridge.

### Preferred route now under audit: ETM+ only

To remove sensor transfer from the primary occupied-footprint analysis, the preferred sequence is:

1. early ETM+ SLC-on epoch: 1999-01-01 to 2003-05-30;
2. late ETM+ SLC-off epoch: 2016-01-01 to 2021-12-31;
3. identical published ETM+ TOA classifier in both epochs;
4. SLC-off gaps treated as missing pixels;
5. multiple late scenes used to form paired observable support;
6. no gap filling with OLI or demographic-informed scene choice.

The late epoch stops before Landsat 7 left the nominal WRS-2 orbit in April 2022.

If this same-sensor route has enough geographic support, it becomes primary. OLI becomes validation/future extension.

If it fails, the next route is a separately validated ETM+↔OLI bridge. It is not selected after seeing the penguin outcomes.

---

## Inferential sequence after measurement closes

No population trend or Paper 1 concentration outcome should be opened until both spatial measurements are frozen.

### Stage 1 — purely spatial test

For each eligible Adélie site:

[
Delta A_{available}
quad	ext{and}quad
Delta A_{occupied}.
]

Classify only with a predeclared uncertainty rule:

- opportunity tracking;
- land-space decoupling;
- joint contraction;
- unresolved because change does not exceed measurement uncertainty.

The primary novelty test is whether positive (Delta A_{available}) can coexist repeatedly with negative (Delta A_{occupied}).

### Stage 2 — abundance validation

Only after Stage 1 closes, rejoin MAPPPD abundance to ask whether:

[
Delta A_{occupied}
]

tracks independent demographic change.

This is validation/interpretation, not a replacement for the spatial endpoint.

### Stage 3 — land–sea interpretation

Only after Stage 2, add the one frozen marine-access metric and ask whether marine change explains sites where available terrestrial opportunity and occupied space decouple.

---

## Current go/no-go state

### GO
- dynamic terrestrial opportunity as a measurable multi-site Antarctic variable;
- broad longitudinal remote sensing;
- Beaufort-positive-control recovery;
- compact marine-support lane;
- independent Adélie guano reference recovery set.

### ACTIVE
- full 77-site summer-exposure extraction;
- same-sensor ETM+ longitudinal support.

### NO-GO unless separately validated
- direct ETM+ classifier application to OLI;
- replacing occupied footprint with abundance because footprint measurement is hard;
- threshold tuning from population outcomes;
- treating static area effects from the closed earlier Paper 2 lane as evidence for the dynamic hypothesis.

## Paper-level interpretation if the direct spatial test works

Paper 1:
> Declining penguin populations can lose effective breeding space faster than proportional thinning predicts.

Paper 2:
> The physical breeding landscape and the realized breeding landscape are distinct dynamic state variables; in Antarctica they can potentially move in opposite directions.

Together, the program becomes an island-ecology argument about **how populations lose space**, not merely an analysis of penguin abundance.
