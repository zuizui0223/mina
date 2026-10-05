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

A positive paired difference alone is not sufficient for confirmation. The observed species-balanced \(H\) must also exceed a frozen elapsed-time-matched trajectory-drift null.

## Why this is the discriminating island-ecology test

The penguin results show replicated concentration during decline and, at the regional scale, lower effective breeding-site number even in increasing networks. Those results suggest weak spatial reversibility but do not directly compare loss and recovery of the same place.

A simple reversible site-quality/basin picture predicts that, for a stable SiteID, abandonment and later recolonization should occur at approximately the same surrounding population state, apart from observation noise and annual sampling.

History-dependent processes can break that symmetry. Once a breeding site is empty, the loss of an established aggregation, site fidelity, conspecific information, or other biological memory may raise the population state required for recolonization.

The estimand is the **loss–recovery asymmetry itself**, not any single social mechanism.

## Stage A — stable hierarchy

Reuse the frozen species × MasterSite / SiteID structural gate.

No count magnitude is used to select panels.

## Stage B — occupancy-state cycles only

Convert each retained direct count to:

- occupied: direct observed count \(>0\);
- vacant: direct observed count \(=0\) exactly;
- missing/unusable.

Missing is never zero.

A completed vacancy spell is:

\[
1\rightarrow0\rightarrow\cdots\rightarrow0\rightarrow1
\]

with every year from abandonment through recolonization calendar-consecutive and complete.

First colonization is excluded because it has no prior within-site abandonment threshold.

### Support thresholds

Before any abundance magnitude is opened, require at least:

- 30 null-eligible completed spells;
- 20 SiteIDs;
- 10 MasterSites;
- 5 species;
- 4 species with at least 3 spells;
- 3 species with spells in at least 2 MasterSites.

### Frozen support for the trajectory-drift null

For each observed spell define

\[
d=u-t,
\]

where \(t\to t+1\) is abandonment and \(u\to u+1\) is recolonization.

Using only the frozen complete-year identities, enumerate every pseudo start year \(s\) for which

\[
s,\ s+1,\ s+d,\ s+d+1
\]

are all complete years in the same panel.

A spell must have at least **3** such pseudo placements to enter Stage C.

This filter uses only year identities and vacancy duration, never count magnitude.

If the support gate fails, stop before opening abundance magnitudes.

## Stage C — paired threshold estimand

For focal SiteID \(j\), exclude the focal site from the surrounding parent abundance:

\[
N_{-j,t}=\sum_{k\ne j}n_{k,t}.
\]

For abandonment \(t\to t+1\),

\[
A_e=
\frac{
\log(1+N_{-j,t})+\log(1+N_{-j,t+1})
}{2}.
\]

For later recolonization \(u\to u+1\),

\[
A_c=
\frac{
\log(1+N_{-j,u})+\log(1+N_{-j,u+1})
}{2}.
\]

Then

\[
H=A_c-A_e.
\]

The same SiteID is its own control for fixed place identity and stable site quality.

## Replication hierarchy

Average in this fixed order:

1. repeated spells within SiteID;
2. SiteIDs within MasterSite;
3. MasterSites within species;
4. species with equal weight.

The observed primary statistic is the unweighted mean of species means:

\[
T_{\mathrm{obs}}.
\]

## Primary inference 1 — species sign-flip

Test whether species-level mean \(H\) values are centered above zero.

If there are at most 20 species, enumerate every sign assignment exactly. Otherwise use 100,000 sign flips with seed 20261005.

This test alone is not sufficient for confirmation.

## Primary inference 2 — elapsed-time-matched trajectory-drift null

A positive \(H\) could arise simply because recolonization occurs later while the parent population is changing.

For each spell and each of 20,000 simulations:

1. retain its SiteID, MasterSite, species and observed transition-gap \(d\);
2. uniformly draw one of its Stage-B-frozen pseudo start years;
3. use the **observed leave-one-SiteID-out parent abundance trajectory**;
4. calculate the same pseudo-\(H\) from transition midpoints;
5. aggregate pseudo-\(H\) through the identical SiteID → MasterSite → species hierarchy.

This generates \(T_{\mathrm{null}}\) expected from the same elapsed times on the same observed parent trajectories without privileging the observed vacancy timing.

Report

\[
\Delta T
=
T_{\mathrm{obs}}-\mathrm{median}(T_{\mathrm{null}})
\]

and the plus-one upper-tail probability

\[
P(T_{\mathrm{null}}\ge T_{\mathrm{obs}}).
\]

## Confirmatory rule

Spatial-recovery hysteresis is supported only if all four conditions hold:

\[
T_{\mathrm{obs}}>0,
\]

\[
p_{\mathrm{signflip}}\le0.05,
\]

\[
\Delta T>0,
\]

and

\[
p_{\mathrm{drift}}\le0.05.
\]

No single criterion can rescue failure of another.

## Interpretation

### Confirmatory support

Allowed:

> **Spatial recovery occurred at a higher surrounding population state than spatial loss at the same breeding sites, beyond generic abundance drift over the same elapsed times.**

> **Population recovery did not simply retrace the spatial pathway of decline.**

Not allowed:

> conspecific attraction caused the hysteresis.

### Positive \(H\), drift null not rejected

Interpretation:

> apparent threshold asymmetry is compatible with generic temporal change in surrounding abundance.

Do not claim spatial hysteresis.

### \(H\) unresolved or negative

The independent test does not support the predicted recovery barrier.

Do not rescue by changing vacancy thresholds, abundance transforms, or spell definitions.

## Relation to island biogeography

The hypothesis concerns the symmetry of extinction and recolonization thresholds of the **same breeding islands**.

A reversible mapping treats occupancy as a function of current place and regional population state. A hysteretic mapping additionally depends on history:

\[
P(O_{t+1}=1\mid N,\mathrm{site},O_t)
\neq
P(O_{t+1}=1\mid N,\mathrm{site})
\]

in a way that makes recovery harder after vacancy.

This makes occupancy history a state variable of the island.

## Mechanism boundary

A supported result can be consistent with social feedback, site fidelity, conspecific attraction, public information, or other biological memory. It can also be produced by time-varying habitat deterioration, predator change, disturbance, or management.

SiteID pairing removes fixed site quality. The trajectory-drift null removes generic temporal drift over the same elapsed time. Neither identifies a unique mechanism.

## Stop rule

After magnitude opening, do not change:

- vacancy-spell definition;
- explicit-zero rule;
- transition midpoint;
- \(\log(1+N)\) transform;
- leave-one-SiteID-out parent state;
- minimum pseudo-placement support;
- pseudo-placement rule;
- null simulation family;
- hierarchy or weighting;
- species/site subset;
- vacancy-duration threshold.

Any mechanism test requires new independent information.
