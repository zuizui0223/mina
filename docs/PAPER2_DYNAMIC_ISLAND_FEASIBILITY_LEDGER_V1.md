# Paper 2 dynamic-island feasibility ledger v1

**Date:** 2026-10-04  
**Branch:** `research/antarctic-island-ecology-v1`  
**Purpose:** Keep the dynamic Antarctic island-ecology lane on one auditable path without reopening demographic outcomes or the closed Paper 1 endpoints.

## Core biological question

> **Can physical breeding opportunity expand while realized penguin breeding space contracts?**

The program separates three moving quantities:

[
A_{available,t},\qquad A_{occupied,t},\qquad N_t.
]

- (A_{available}): summer-exposed terrestrial breeding opportunity.
- (A_{occupied}): realized active breeding / guano footprint.
- (N): breeding abundance, still locked for the new dynamic analysis.

The high-value island-ecology pattern is:

[
\Delta A_{available}>0
\quad\text{and}\quad
\Delta A_{occupied}<0.
]

This would establish land-space decoupling without requiring abundance to stand in for spatial occupation.

---

## Gate ledger

| Gate | Question | Frozen evidence | State |
|---|---|---|---|
| G0 demographic support | Is there a long-term outcome-blind site roster? | 107 site × species units, 88 physical sites | PASS |
| G1 static spatial support | Are candidate sites independently mapped as ice-free terrestrial nodes? | Existing breeding-options atlas covers the great majority of sites | PASS |
| G2 optical catalog | Do early and late optical records exist? | 106/107 units pass; broad 88-site STAC audit also passes | PASS |
| G3 local pixel support | Are locally usable optical pixels available in both epochs? | 77 physical sites / 94 site × species units; three large regional groups | PASS |
| G4 available-space metric recovery | Does the frozen metric recover a known positive control? | Beaufort positive at both 0.50 and 0.67 persistent-exposure thresholds | PASS |
| G5 full available-space extraction | Is (A_{available}) measurable across the frozen QA roster? | 77/77 measured; 57 positive, 16 negative, 4 zero at primary threshold | **PASS** |
| G6 marine archive support | Is one compact marine-access lane available without outcome fishing? | NSIDC G02135 supports all 107 units; 103/105 required month-files available | PASS |
| G7 occupied-footprint reference overlap | Is there independent guano/colony reference support? | 22/44 long-term Adélie sites overlap published reference colonies within 5 km | PASS for recovery; geographically bounded |
| G8 published classifier specification | Can the historical guano classifier be reconstructed numerically? | ETM+ TOA transition matrix and published decision rule recovered | PASS |
| G8b published source-scene crosswalk | Can published positive pixels be linked to modern C2 L1 source scenes? | 45/47 scenes; 7,847/9,143 positive pixels. Frozen pixel-coverage gate fails | **BOUNDED FAIL / DIAGNOSE 2 SCENES** |
| G9a same-sensor occupied-footprint route | Can ETM+ be used in both early and late epochs? | 44/44 have early ETM+ support; 0/44 have frozen 2016–2021 late ETM+ support | **CLOSED** |
| G9b Antarctic ETM+↔OLI bridge support | Are paired ETM+/OLI acquisitions available for a local spectral bridge? | outcome-blind overlap audit running | ACTIVE |
| G10 occupied-footprint measurement recovery | Does the frozen/bridged classifier recover independent footprint references above frozen error? | not yet tested | LOCKED |
| G11 dynamic spatial ecological test | Does available space track occupied space, or do they decouple? | demographic outcomes still locked | LOCKED |
| G12 abundance/marine interpretation | Do abundance and marine access explain residual spatial change? | new demographic outcomes still locked | LOCKED |

---

## What is established methodologically

### 1. Archive availability is not the bottleneck

The frozen optical-catalog analysis supports 106/107 long-term Pygoscelis site × species units. The dynamic-land question therefore does not collapse into a handful of hand-picked sites.

### 2. Local Antarctic image quality is not a fatal bottleneck

The stricter local-pixel gate passes at:

- **77 physical sites**;
- **94 site × species units**;
- **37 Adélie**;
- **32 chinstrap**;
- **25 gentoo**.

Regional replication remains broad:

- Central-west Antarctic Peninsula: 33 physical sites;
- South Shetland Islands: 16;
- Victoria Land: 24.

Seven physical sites fail and remain excluded without rescue:
BISC, CUVE, HUMB, ORNE, PGEO, ROYD, SHIR.

### 3. (A_{available}) is now a measured multi-site dynamic variable

The full frozen extraction completed without technical errors.

Across 77 sites:

- positive primary change: **57**;
- negative primary change: **16**;
- zero primary change: **4**;
- median (Delta A_{available}=+0.03046);
- interquartile range: 0 to +0.15719.

Regional structure is strong:

- South Shetland Islands: **16/16 positive**, median +0.2750;
- Central-west Antarctic Peninsula: 24 positive / 5 negative / 4 zero, median +0.0302;
- Victoria Land: 13 positive / 11 negative, median +0.00462.

This is useful design variation: the later ecological test is not merely comparing one uniformly expanding Antarctic landscape with one uniformly changing penguin population.

### 4. Adélie-specific (A_{available}) variation is sufficient

Among the 37 Adélie sites passing the pixel gate:

- 25 have positive primary (Delta A_{available});
- 12 have negative primary (Delta A_{available});
- median primary change is approximately +0.0150.

Primary (0.50) and frozen stricter (0.67) exposure thresholds have:

- sign agreement at 28/37 sites;
- correlation (r=0.832).

A conservative descriptive split, used only as measurement context, gives:

- 22 same-direction increases;
- 6 same-direction decreases;
- 9 threshold-sensitive sites.

The main analysis should nevertheless retain continuous primary (Delta A_{available}), with the 0.67 metric as its frozen sensitivity rather than choosing a threshold after ecological outcomes are seen.

### 5. Beaufort validates direction of the available-space metric

At Beaufort Island, without using penguin counts:

- threshold 0.50: 0.0423 → 0.0979, (Delta=+0.0556);
- threshold 0.67: 0.0060 → 0.0387, (Delta=+0.0326).

Thus the frozen Landsat/QA metric recovers the direction of a previously documented terrestrial-opportunity expansion case.

This validates direction, not literal nestable-area magnitude.

### 6. The marine side is technically available

The frozen NSIDC monthly sea-ice archive supports all 107 candidate site × species units.

Two historical month-files are absent:

- December 1987;
- January 1988.

They remain missing and are not imputed.

This authorizes a compact marine-access calculation only after the direct terrestrial spatial test closes. It is not evidence that sea ice explains any penguin response.

---

## Active bottleneck: (A_{occupied})

The new Paper 2 should not substitute abundance for spatial occupation if a direct occupied-footprint measure can be recovered.

### Published reference support

The published Landsat work provides:

- a numeric ETM+ TOA classifier specification;
- 9,143 published positive classified pixels;
- 47 source scenes containing those positive pixels;
- 187 published colony clusters;
- spatial overlap with **22/44** long-term Adélie sites at the frozen 5 km radius.

This is a real external measurement-recovery set.

### Source-scene crosswalk result

Modern Collection-2 Level-1 identities were recovered for:

- **45/47 source scenes (95.7%)**;
- **7,847/9,143 published positive pixels (85.8%)**.

The frozen crosswalk required at least 95% coverage by both scenes and pixels. It therefore **fails overall** because two unmatched scenes contain 1,296 positive pixels.

The two unmatched historical source identifiers are:

- `LE71051062001333EDC00` — 1 published positive pixel;
- `LE71241082001018SGS00` — 1,295 published positive pixels.

Do not lower the 95% pixel threshold. Diagnose these two identities first. The second is particularly important because a same-date adjacent WRS row is recoverable in Collection 2, so an archival identity/geolocation issue must be ruled out before declaring those pixels unavailable.

### Same-sensor ETM+ longitudinal route is closed

The preferred no-bridge route was tested prospectively:

- early SLC-on ETM+ (1999–30 May 2003);
- late SLC-off ETM+ (2016–2021);
- same ETM+ TOA classifier at both epochs.

Result:

- early ETM+ summer imagery exists at all 44 candidate Adélie sites;
- late ETM+ summer imagery under the frozen window exists at **0/44** sites.

Therefore the same-sensor longitudinal route is closed. Its window is not shifted after the result.

### Required fallback: validated ETM+↔OLI bridge

The next route is explicitly measurement-only:

1. identify 2013–2015 Antarctic sites with near-date ETM+ and OLI acquisitions;
2. use those paired scenes to test spectral harmonization on Antarctic surfaces;
3. transform OLI TOA into ETM+-compatible spectral space using one externally specified transformation;
4. compare classifier (d) values / class calls between paired sensors on independently defined pixels;
5. freeze allowable bridge error before longitudinal (A_{occupied}) is estimated.

Published TOA harmonization coefficients may supply the transformation, but the Antarctic pair test determines whether they are adequate for this application.

Do not classify OLI with ETM+ coefficients without this bridge.

---

## Inferential sequence after measurement closes

No population trend or Paper 1 concentration outcome is opened until both spatial measurements are frozen.

### Stage 1 — purely spatial island test

For each eligible Adélie site:

[
Delta A_{available}
\quad\text{and}\quad
Delta A_{occupied}.
]

The primary novelty is not a correlation with abundance. It is the direct relation between **changing opportunity** and **changing realized breeding space**.

The critical Antarctic pattern is:

[
Delta A_{available}>0
\quad\text{while}\quad
Delta A_{occupied}<0.
]

### Stage 2 — abundance validation

Only after Stage 1 closes, rejoin MAPPPD abundance and ask whether (A_{occupied}) change corresponds to independently measured demographic change.

### Stage 3 — land–sea interpretation

Only after Stage 2, add the frozen marine-access metric and ask whether marine change explains sites where terrestrial opportunity and occupied breeding space decouple.

---

## Current go/no-go state

### GO

- dynamic terrestrial opportunity as a measured multi-site Antarctic variable;
- broad longitudinal remote sensing;
- Beaufort positive-control recovery;
- compact marine-support lane;
- independent Adélie guano reference set;
- continuous variation in (A_{available}) within Adélie and within major regions.

### ACTIVE

- diagnostic repair of the two unmatched published ETM+ source scenes;
- Antarctic ETM+↔OLI overlap/support audit.

### CLOSED

- same-sensor ETM+ early-versus-2016–2021 primary occupied-footprint route.

### NO-GO unless separately validated

- direct ETM+ classifier application to OLI;
- replacing occupied footprint with abundance because footprint measurement is hard;
- tuning remote-sensing thresholds using population outcomes;
- reopening static-place predictors from the earlier closed macroecology lane.

## Paper-level interpretation if the direct spatial test succeeds

**Paper 1**

> Declining penguin populations can lose effective breeding space faster than proportional thinning predicts.

**Paper 2**

> The physical breeding landscape and the realized breeding landscape are distinct dynamic state variables; in Antarctica they can move in opposite directions.

Together, the program becomes an island-ecology argument about **how populations lose space when island opportunity itself is moving**, rather than another analysis of penguin abundance.
