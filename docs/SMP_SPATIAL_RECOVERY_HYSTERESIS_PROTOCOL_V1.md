# SMP spatial-recovery hysteresis protocol v1

**Status:** frozen before receipt/opening of the bulk SMP abundance magnitudes.

## Hypothesis

> **Population recovery does not retrace spatial collapse: a breeding site that has been abandoned is recolonized only after the surrounding population has recovered beyond the population state at which that same site was lost.**

For the same SiteID,

\[
H=A_{\mathrm{recolonize}}-A_{\mathrm{abandon}}.
\]

Primary directional prediction:

\[
H>0.
\]

A positive paired difference alone is not sufficient. Confirmation additionally requires that the species-level signal survives a frozen structured phase null that preserves the observed multivariate parent-population trajectories.

## Why this is the island-ecology test

The Antarctic penguin results show two facts:

1. decline can concentrate breeding effort beyond proportional thinning;
2. numerical increase at regional scale does not necessarily restore effective breeding-site number.

Those observations suggest weak spatial reversibility but do not directly compare loss and recovery of the same place.

The SMP test does.

A reversible site-quality/basin view predicts that, for a stable physical SiteID, abandonment and recolonization should occur at approximately the same surrounding population state, apart from stochasticity and sampling.

History-dependent processes can break that symmetry. Once a breeding site is empty, loss of an established aggregation, site fidelity, conspecific information or other biological memory can raise the population state required for recolonization.

The estimand is the **loss–recovery asymmetry itself**, not a particular social mechanism.

## Stage A1 — count-blind structural support

Use the frozen species × MasterSite / SiteID support gate.

No count magnitude may be used to select species, MasterSites, SiteIDs, count units, years or thresholds.

## Stage A2 — physical SiteID identity

Before any positive/zero occupancy history is inspected, resolve SiteID continuity from provider metadata.

A focal SiteID is retained only if all are true over the retained interval:

- stable physical identity;
- mutually exclusive child Site within the MasterSite;
- no overlap with parent or sibling records;
- no boundary change;
- not retired/replaced.

If multiple count Units are structurally eligible for one species × MasterSite, the provider must identify a canonical Unit before occupancy states are opened; otherwise exclude that panel.

If physical identity cannot be resolved, stop this hypothesis.

## Stage A3 — zero semantics

Before scanning vacancy events, freeze provider/documentation confirmation that:

- a direct row with Count = 0 is a surveyed nil return;
- an absent SiteID × year record is not biological zero;
- estimated/imputed zero records are excluded from the primary test.

If these semantics differ by era or record family, restrict the compatible era/family **before** occupancy states are inspected.

## Stage B — occupancy-state cycles only

After A1–A3 pass, convert retained direct counts to:

- occupied: direct observed count \(>0\);
- vacant: provider-confirmed direct observed count \(=0\);
- missing/unusable.

Missing is never zero.

A completed vacancy spell is:

\[
1\rightarrow0\rightarrow\cdots\rightarrow0\rightarrow1
\]

with every year from abandonment through recolonization calendar-consecutive and complete.

First colonization is excluded because it has no prior within-site abandonment threshold.

### Phase-block support

Each completed spell is assigned to the maximal calendar-consecutive complete-year block containing the entire spell.

Only spells in blocks of at least **6 years** can enter Stage C. This gives at least six distinct circular phase alignments under the structured null.

### Program support thresholds

After the phase-block filter, require at least:

- 30 completed spells;
- 20 distinct physical SiteIDs;
- 10 MasterSites;
- 5 species;
- 4 species with at least 3 spells;
- 3 species represented by spells in at least 2 MasterSites.

If any condition fails, stop before abundance magnitudes are opened.

## Stage C — paired threshold estimand

For focal SiteID \(j\), exclude the focal site from the surrounding parent abundance:

\[
N_{-j,t}=\sum_{k\neq j} n_{k,t}.
\]

For abandonment \(t\rightarrow t+1\),

\[
A_e=
\frac{\log(1+N_{-j,t})+\log(1+N_{-j,t+1})}{2}.
\]

For later recolonization \(u\rightarrow u+1\),

\[
A_c=
\frac{\log(1+N_{-j,u})+\log(1+N_{-j,u+1})}{2}.
\]

Then

\[
H=A_c-A_e.
\]

The same SiteID is therefore its own control for fixed place identity and stable site quality.

## Replication hierarchy

Average in this fixed order:

1. repeated completed spells within SiteID;
2. SiteIDs within MasterSite;
3. MasterSites within species;
4. species with equal weight.

The primary observed statistic is

\[
T_{\mathrm{obs}}=
\mathrm{mean}\left(H_{\mathrm{species}}\right).
\]

## Primary inference 1 — species sign-flip

Species are the macroecological replication units.

Test whether species-level mean \(H\) values are centered above zero.

- if species \(\leq20\): enumerate all sign assignments exactly;
- otherwise: 100,000 sign flips;
- seed: 20261005.

A positive sign-flip result alone is not sufficient.

## Primary inference 2 — structured common-phase null

Positive \(H\) could appear merely because abandonment occurs earlier and recolonization later on a trending or autocorrelated parent-population trajectory.

The structured null preserves the observed population histories.

For each of 9,999 resamples:

1. retain the exact frozen vacancy-spell roster and event-year positions;
2. retain the exact multivariate count trajectory within every species × MasterSite;
3. retain the maximal contiguous complete-year block assigned at Stage B;
4. draw **one common circular year shift** for each species × MasterSite × block;
5. apply that same shift to the entire block-level count matrix, preserving cross-SiteID covariance and the dependence among multiple spells in that block;
6. calculate leave-one-SiteID-out \(H\) at the frozen event positions;
7. aggregate through the identical spell → SiteID → MasterSite → species hierarchy.

Report:

\[
\Delta_{\mathrm{phase}}
=
T_{\mathrm{obs}}-\mathrm{median}(T_{\mathrm{phase}})
\]

and the plus-one upper-tail probability

\[
P(T_{\mathrm{phase}}\geq T_{\mathrm{obs}}).
\]

This is a structured **temporal-alignment null**. It is not a mechanistic reversible-occupancy model.

## Confirmatory rule

Spatial-recovery hysteresis is supported only if all four conditions hold:

\[
T_{\mathrm{obs}}>0,
\]

\[
p_{\mathrm{signflip}}\leq0.05,
\]

\[
\Delta_{\mathrm{phase}}>0,
\]

and

\[
p_{\mathrm{phase}}\leq0.05.
\]

No single criterion can rescue failure of another.

## Interpretation

### All criteria pass

Allowed:

> **Spatial recovery occurred at a higher surrounding population state than spatial loss at the same breeding sites, beyond generic temporal alignment with the observed parent-population trajectories.**

> **Population recovery did not simply retrace the spatial pathway of decline.**

Not allowed:

> conspecific attraction caused the hysteresis.

### \(H>0\), but phase null not rejected

Interpretation:

> the apparent loss–recovery difference is compatible with generic temporal structure in surrounding abundance.

Do not claim hysteresis.

### \(H\leq0\) or species sign-flip unsupported

The independent test does not support the predicted recovery barrier.

Do not rescue the hypothesis by changing vacancy thresholds, transforms, spells, species or time windows.

## Relation to island biogeography

The hypothesis concerns the symmetry of extinction and recolonization thresholds of the **same breeding islands**.

A reversible mapping treats occupancy mainly as a function of current place and current regional population state.

A hysteretic mapping additionally depends on history:

\[
P(O_{t+1}=1\mid N,\mathrm{site},O_t)
\neq
P(O_{t+1}=1\mid N,\mathrm{site}).
\]

In this formulation, occupancy history becomes a state variable of the island.

## Novelty boundary

The manuscript must not claim novelty for:

- Allee effects;
- conspecific attraction;
- first colonization versus recolonization;
- history dependence in dynamic island theory;
- seabird site fidelity.

Those are established.

The candidate new contribution is narrower:

> **a prospectively frozen, multi-species, same-site empirical test of whether abandonment and later recolonization occur at different surrounding-population thresholds, motivated by an independently discovered spatial-recovery anomaly in Antarctic penguins.**

Black-legged kittiwake work has already separated persistence, first colonization and recolonization and related them to local density and breeding success. Dynamic island-biogeography theory has also explicitly predicted history dependence and hysteresis. The present test therefore targets the paired threshold asymmetry itself.

## Mechanism boundary

A supported result can be consistent with social feedback, site fidelity, conspecific attraction, public information or other biological memory.

It can also arise from time-varying habitat deterioration, predator change, disturbance or management.

SiteID pairing removes fixed site quality. The structured phase null controls generic alignment with the observed temporal population trajectory. Neither identifies a unique mechanism.

## Stop rule

After abundance magnitudes are opened, do not change:

- physical SiteID eligibility;
- zero semantics;
- vacancy-spell definition;
- six-year phase-block minimum;
- transition midpoint;
- \(\log(1+N)\) transform;
- leave-one-SiteID-out parent state;
- circular-shift scheme;
- null family or resample count;
- hierarchy or weighting;
- species/SiteID subset;
- vacancy-duration rule.

Any mechanism test requires new independent information.
