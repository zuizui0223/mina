# SMP spatial-recovery hysteresis literature position v2

**Date:** 2026-10-05  
**Status:** positioning-only update after V2 pre-data recovery audit; no inferential rule is changed.

## Already established

### Recolonization is distinct from first colonization

Bled, Royle & Cam (2011, *Ecology*, doi:10.1890/10-0392.1) explicitly separated persistence, first colonization and recolonization in Black-legged Kittiwake nest-site dynamics and related them to density and reproductive information.

### Buffer effects across increase, decline and recovery are established

Bennett et al. (2022, *Journal of Animal Ecology*, doi:10.1111/1365-2656.13674) tested site-dependent regulation in common guillemots across population increase, decline and recovery.

### Allee effects can delay seabird recolonization in theory

Schippers et al. (2011, *Ecological Modelling*, doi:10.1016/j.ecolmodel.2011.05.022) showed that Allee-type colonial dynamics can prolong recolonization of empty breeding patches and slow metapopulation recovery.

### Historical hysteresis is already part of island theory

Dynamic island-biogeography and positive-feedback theory already permit colonization and extinction to follow different constraints.

Therefore none of the following is novel by itself:

- recolonization as a distinct process;
- site-dependent occupancy;
- social information;
- Allee effects;
- recolonization barriers;
- the concept of hysteresis.

## Candidate empirical contribution

The candidate contribution is deliberately narrow:

> **A prospective multi-species same-place test of whether the surrounding population state associated with later recolonization is systematically higher than the state associated with earlier abandonment, using the same physical breeding SiteIDs as their own controls.**

The primary annual-census proxy is

\[
H=A_{\mathrm{recolonize}}-A_{\mathrm{abandon}}.
\]

This is stronger than a cross-site occupancy comparison because stable place identity is paired out.

## Why V2 is needed

The original V1 circular phase null failed a pre-data synthetic calibration: it classified 40/40 monotonic-drift datasets as confirmatory.

V2 replaces circular wrap with a **non-circular common-shift null**.

Within each physical MasterSite consecutive block:

- all SiteID/species event geometries are retained;
- one integer-year shift is shared by every spell;
- shifted events must remain inside the observed block;
- no end-to-start wrapping is allowed;
- observed abundance trajectories remain unchanged.

At minimum synthetic replication V2 produced:

- stationary false-positive rate 3.3%;
- monotonic-drift false-positive rate 0%;
- reversible-threshold false-positive rate 0%;
- strong-hysteresis recovery 100%.

The moderate synthetic calibration was unresolved. This conservatism is part of the frozen design.

## Strongest allowed novelty statement if supported

> **We prospectively tested across multiple seabird species whether spatial loss and later recovery of the same breeding places occur at different surrounding population states.**

Strongest biological interpretation:

> **Population recovery did not simply retrace spatial collapse.**

## Still prohibited after support

Do not claim:

- discovery of ecological hysteresis as a concept;
- first evidence that recolonization differs from colonization;
- proof of an Allee mechanism;
- proof of conspecific attraction;
- elimination of all habitat-quality explanations;
- universality across island taxa.

## Measurement boundary

\(A_e\) and \(A_c\) are averages of annual censuses bracketing observed transitions.

They are transition-state proxies, not exact continuous-time thresholds.

Preferred wording:

- loss–recovery state asymmetry;
- surrounding population state at observed abandonment/recolonization;
- spatial recovery hysteresis, with the annual-census qualification stated explicitly.
