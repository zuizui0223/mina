# SMP spatial-recovery hysteresis protocol v1

**Status:** frozen before receipt/opening of the bulk SMP abundance magnitudes.

## Hypothesis

> **Population recovery does not retrace spatial collapse: a breeding site that has been abandoned requires a higher surrounding population state to be recolonized than the state at which that same site was lost.**

For the same physical SiteID,

\[
H = A_{\mathrm{recolonize}} - A_{\mathrm{abandon}}.
\]

Primary prediction:

\[
H>0.
\]

## Why this is the discriminating island-ecology test

The Antarctic penguin results show replicated concentration during decline and, at the regional scale, lower effective breeding-site number even in some increasing networks. Those results suggest weak spatial reversibility but do not compare extinction and recolonization thresholds at the same place.

A reversible site-quality/basin model predicts that, after fixed site identity is controlled, abandonment and later recolonization should occur at approximately the same surrounding population state:

\[
H\approx 0.
\]

History-dependent spatial recovery predicts:

\[
H>0.
\]

Positive social feedback, conspecific attraction and site fidelity are possible mechanisms, but the estimand is the asymmetry itself.

## Stage A1 — count-blind structural support

Use identifiers, sampling years, methods, count unit and missingness only.

No count magnitude or zero/positive occupancy history is used to choose panels.

## Stage A2 — physical SiteID identity gate

Before occupancy states are opened, require provider/site-history resolution for every retained SiteID.

A SiteID is eligible only if it is:

- physically stable across the retained interval;
- a mutually exclusive child component;
- not overlapping a parent or sibling component;
- not boundary-changed during the panel;
- not retired/replaced without an outcome-blind physical crosswalk.

If site history is unavailable, the hysteresis route stops. Apparent abandonment created by renaming, merging, splitting or boundary change is unacceptable.

## Stage B — occupancy-state cycles only

Convert every retained direct count to:

- **positive**: observed count \(>0\);
- **vacant**: observed count \(=0\) exactly;
- **missing/unusable**.

A missing row is never zero.

A completed vacancy spell is:

\[
1\rightarrow0\rightarrow\cdots\rightarrow0\rightarrow1
\]

with every year in the spell calendar-consecutive and complete.

The frozen support gate requires:

- at least 30 completed spells;
- at least 20 SiteIDs with completed spells;
- at least 10 MasterSites;
- at least 5 species;
- at least 4 species with at least 3 spells;
- at least 3 species with spells from at least 2 MasterSites.

If this fails, stop before opening abundance magnitudes.

## Stage C — paired abandonment/recolonization threshold

For focal SiteID \(j\), define surrounding population state using the parent total **excluding the focal SiteID**:

\[
N_{-j,t}=\sum_{k\ne j}n_{k,t}.
\]

For abandonment \(t\rightarrow t+1\),

\[
A_e=
\frac{
\log(1+N_{-j,t})+
\log(1+N_{-j,t+1})
}{2}.
\]

For later recolonization \(u\rightarrow u+1\),

\[
A_c=
\frac{
\log(1+N_{-j,u})+
\log(1+N_{-j,u+1})
}{2}.
\]

Then

\[
H=A_c-A_e.
\]

The same SiteID is its own control for fixed place identity and fixed site quality.

## Replication hierarchy

Average in the following order:

1. repeated spells within SiteID;
2. SiteIDs within MasterSite;
3. MasterSites within species;
4. species with equal weight.

The primary statistic \(T\) is the unweighted mean of species means.

## Primary inference 1 — species sign-flip

Under a reversible mapping, species-level mean \(H\) values are centered on zero.

If there are at most 20 represented species, enumerate every sign combination exactly. Otherwise use 100,000 frozen random sign flips.

The directional test is one-sided for \(T>0\).

## Primary inference 2 — trajectory-phase calibration

A positive paired \(H\) could also be exaggerated by annual sampling, secular abundance trajectories or transition overshoot. Therefore a second frozen null is mandatory.

For each species × MasterSite and each **contiguous complete-year block** containing one or more frozen spells:

1. keep the frozen spell identities and transition years fixed;
2. keep the observed multivariate count trajectory fixed;
3. circularly shift the complete annual count matrix by one common random lag for the entire block;
4. use the same lag for all SiteIDs and spells in that block, preserving cross-site covariance;
5. recompute all \(H\) values and the same species-balanced \(T\).

Use 9,999 resamples with seed 20261005.

The plus-one upper-tail probability is

\[
p_{\mathrm{phase}}
=
\frac{
1+\#(T_{\mathrm{null}}\ge T_{\mathrm{obs}})
}{
10000
}.
\]

This is a structured temporal-alignment null, not a mechanistic occupancy model.

## Confirmatory decision

Spatial-recovery hysteresis is supported only if all three conditions hold:

\[
T>0,
\]

\[
p_{\mathrm{sign}}\le0.05,
\]

and

\[
p_{\mathrm{phase}}\le0.05.
\]

## Interpretation

### If supported

Allowed:

> **Spatial recovery requires a higher surrounding population state than spatial loss at the same breeding sites.**

> **Population recovery does not simply retrace the spatial pathway of decline.**

Not allowed without additional evidence:

> conspecific attraction causes the hysteresis;

> an Allee effect has been demonstrated.

### If the sign-flip passes but the trajectory-phase null fails

Interpretation:

> the paired asymmetry is compatible with generic temporal alignment of the observed abundance trajectories and cannot support spatial hysteresis.

### If \(H\) is unresolved or negative

The general spatial-hysteresis hypothesis is not supported. Do not rescue it with alternative thresholds, lags or subsets.

## Relation to existing work

Colonization, recolonization, persistence and extinction are established objects in metapopulation and seabird occupancy research. The intended contribution is narrower: a prospective multi-species, **same-site paired test of abandonment versus recolonization population thresholds**, motivated by an independently discovered spatial-recovery anomaly in Antarctic penguins.

## Mechanism boundary

Same-site pairing removes fixed SiteID quality, and the trajectory-phase null calibrates generic temporal alignment. Neither removes time-varying habitat degradation, predator change, disturbance, management or other unmeasured temporal confounding.

A positive result therefore establishes **history-dependent spatial recovery**, not a unique social mechanism.

## Stop rule

After abundance magnitudes are opened, do not change:

- SiteID identity decisions;
- vacancy-spell definition;
- explicit-zero rule;
- log transform;
- leave-one-site-out parent state;
- transition midpoint;
- hierarchy or weighting;
- support thresholds;
- sign-flip test;
- trajectory-phase null.
