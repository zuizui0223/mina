# Frozen physical Circuitscape run: original penguin breeding-site marine nodes

Date: 2026-11-08 JST. **New numeric resistance results have not been inspected at freeze.**

This is a **descriptive physical opportunity exercise**, after the earlier binary connectivity gate and already-known six-site penguin census results. It is **not independently preregistered** and does not infer penguin migration, foraging choices, climate causality, reproduction, or future abundance.

## Data and domain fixed before results

- **OSI SAF OSI-450-a1 v3.1**, monthly September **1993 and 2018**, publisher original native EASE2 raster 432×432, each file checked by expected SHA256 from gate: 1993/09 `944be76f732c07e550703e20cb1c7c561270153e60a64d0e9399cedb812c39f8` and 2018/09 `620d242d86b0db26fe81a2b7c41f136d91ec0a357be32fa2d89b9ccf666e7eeb`. These are two snapshots **not a 25-year climatic trend**. August–November monthly means are not substituted after viewing results.
- Original site codes from pinned coordinates (`5a211a0eaa63b6a5d3516353dd9431428618dbd3`): ARDL, BISC, LION, LLAN, PCHA, PETE.
- Fixed unique nearest valid marine ocean-cell source nodes from prior independent gate: ARDL 65774, BISC 71828, LION 64911, LLAN 65343, PCHA 72260, PETE 72693, 0-based flattened 432×432 native array. All are source-valid in both original months and within 60 km of source site. Revalidate, do not jitter.
- Crop original 432×432 native map to **rows 120:201, columns 75:156 (81×81)** (0-based half-open). Common ocean mask is **intersection of the two valid source-ocean masks**. Physical boundary choice is an admitted model assumption; do not represent crop as complete Antarctic ocean.
- Preserve EASE2 native x/y grid spacing and orientation in Arc/Info ASCII grid. No apparent 1 km interpolation.
- Require all six nodes in the *same connected 8-neighbor common valid-ocean component*, else no pairwise 8-neighbor result. Four-neighbor run only if the same check passes; never replace a disconnected case with zero resistance.

## Models (fixed, no optimization)

- **β=0 constant**: resistance per common marine pixel R=1, all included marine pixels equal. The ocean geometry null.
- **β=+2 sea-ice penalty**: R=exp(+2 × SIC/100).
- **β=−2 sea-ice preference**: R=exp(−2 × SIC/100).

All finite SIC input pixels 0–100%. Sea-ice-to-movement resistance coefficients are **hypothetical**, not estimated biologically. Species/season can reverse the sign and shape of ice associations. Land or invalid ocean pixels are `NODATA_value=-9999` (not zero-SIC ocean). Each year uses same mask and node positions.

Default Circuitscape connection: average **cell conductances**; diagonal connections weighted 1/sqrt(2). Focal nodes distinct positive integers 1–6. Primary 8-neighbor model all β values × both years = 6 solves. Sensitivity 4-neighbor model β=0 and β=+2 × both years = 4 solves, if every site remains connected. Output is per-pair **electrical effective resistance in arbitrary model units**, not kilometers, animal survival, or migration probability. Optionally cumulative current maps are written for 8-neighbor β=0 and β=+2 for both months; they are not GPS routes.

## Fixed comparisons and validation

- For the same pair/year/neighbor rule, compute R_eff(β±2)/R_eff(β0). If there is no connected path, mark NA rather than replace by 0.
- The β0 baseline must agree across 1993/2018 (same mask, exact same nodes), within solver tolerance; if not, fail.
- Cross-year ΔR for β=±2 reflects **different September sea-ice snapshots** and must not be called a statistically validated warming effect.
- Validate full 15-pair matrix as symmetric with diagonal zero, 15 finite positive pairwise resistances for connected pairs.
- Independent SciPy Laplacian effective-resistance calculation on the exact cropped mask uses source-cell average conductance and sqrt(2) diagonal distance to cross-check the Circuitscape 8-neighbor β=0 matrix for all 15 focal pairs (relative tolerance ≤0.5%). If this fails, mark COMPUTATION_HOLD rather than interpret results.

## Ecological interpretation limits

Past 45-day GPS binary graph test found 0 disconnected *low-ice* source-grid components, not absence of environmental movement costs. A physics-only resistor network cannot establish whether the observed Adélie decline / gentoo increase reflects natal philopatry, mortality, immigration, competition or habitat loss. No direct public multi-year ID×next-year breeding-site resight table was found. Do not fit β to those same nesting trajectories or claim SSP future breeding numbers.

## Software

Use **actual Julia Circuitscape.jl** `Circuitscape.compute` with raster pairwise config and CHOLMOD direct solver on the cropped landscape. Save Julia version, package environment, generated INIs, original input SHA, source pixel IDs, resistances, validation metrics and cumulative currents as CI artifact. Documentation: https://docs.circuitscape.org/Circuitscape.jl/latest/options/

Working branch is `codex/penguin-circuitscape-feasibility-20261108`, PR #211; the published warming manuscript v0.6/main/frozen Paper1/2 are not changed by this pilot.
