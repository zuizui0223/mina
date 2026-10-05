# SMP spatial-recovery hysteresis protocol v2

**Date:** 2026-10-05  
**Status:** candidate final protocol after V1 pre-data failure and V2 synthetic recovery success. No SMP hysteresis support/effect outcome has been opened.

## V1 closure

The original circular phase-null design is closed.

Its frozen pre-data recovery audit produced:

- stationary false positive: 0/40;
- monotonic-drift false positive: **40/40**;
- strong-signal recovery: 40/40.

The monotonic-drift failure is fatal. V1 must never be executed on SMP abundance magnitudes.

## Hypothesis

> **Population recovery does not retrace spatial collapse: later recolonization of the same breeding places requires a higher surrounding population state than their earlier abandonment.**

For the same SiteID,

\[
H=A_{\mathrm{recolonize}}-A_{\mathrm{abandon}}.
\]

The focal SiteID is excluded from the surrounding population state.

## Existing structural and semantic gates

V2 inherits the already outcome-blind requirements that:

1. SiteID identity and MasterSite identity are provider-resolved;
2. retained SiteIDs are stable, mutually exclusive child sites;
3. explicit direct Count = 0 is provider-confirmed as a surveyed nil return;
4. absent rows are not interpreted as zeros;
5. estimated/imputed zeros are excluded;
6. every vacancy spell is calendar-consecutive and state-complete.

No abundance magnitude is opened before these gates and the completed-spell support gate pass.

## V2 null support

The V1 circular phase shift failed because wrapping the end of a monotonic trajectory to its beginning created an artificial null distribution centered below the observed later-minus-earlier contrast.

V2 removes circular wrapping.

### Shift group

All spells that share:

- the same physical \`master_site_key\`;
- the same frozen consecutive phase block

form one shift group.

### Common non-circular shift

For a shift group, freeze every integer \(k\) such that **all four event years of every spell** remain inside the same observed phase block after adding \(k\).

One common \(k\) is applied to every SiteID/species spell in that physical MasterSite block.

Thus V2 preserves:

- physical MasterSite;
- SiteID;
- species;
- each spell's abandonment–recolonization interval;
- relative event geometry among spells;
- cross-site and cross-species local timing;
- the observed multivariate abundance trajectories.

It does **not** wrap the last year onto the first year.

Each shift group must have at least 3 common shifts. Groups below that threshold are removed before abundance magnitude is opened.

After that restriction, the Stage-B support gate still requires at least:

- 30 completed spells;
- 20 SiteIDs;
- 10 physical MasterSites;
- 5 species;
- 4 species with at least 3 spells;
- 3 species represented across at least 2 MasterSites.

## Stage C estimand

For focal SiteID \(j\),

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

## Replication hierarchy

Average in this fixed order:

1. repeated spells within species × physical MasterSite × SiteID;
2. SiteIDs within species × physical MasterSite;
3. physical MasterSites within species;
4. species with equal weight.

The primary observed statistic is \(T_{\mathrm{obs}}\), the unweighted mean of species means.

## Confirmatory gate 1 — replicated positive direction

Species-level mean \(H\) values are tested by a one-sided sign-flip test.

- exact enumeration if species ≤20;
- otherwise 100,000 sign flips;
- seed 20261005.

Required:

\[
T_{\mathrm{obs}}>0
\]

and

\[
p_{\mathrm{sign}}\le0.05.
\]

## Confirmatory gate 2 — non-circular common-shift null

For each of 20,000 simulations:

1. draw one frozen common shift for each physical MasterSite phase block;
2. apply that same shift to every spell in the block;
3. leave the abundance matrices unchanged;
4. compute pseudo-\(H\);
5. aggregate through the identical hierarchy.

Report:

\[
\Delta_{\mathrm{shift}}
=
T_{\mathrm{obs}}-\mathrm{median}(T_{\mathrm{null}})
\]

and the plus-one upper-tail probability.

Required:

\[
\Delta_{\mathrm{shift}}>0
\]

and

\[
p_{\mathrm{shift}}\le0.05.
\]

Both gates must pass.

## Pre-data recovery audit

V2 was tested at the minimum synthetic replication scale: 5 species, 10 physical MasterSites and 30 spells.

False-positive rates:

- stationary exogenous events: **3.3%**;
- monotonic-drift exogenous events: **0%**;
- genuinely reversible decline–recovery threshold cycle: **0%**.

Recovery:

- moderate synthetic hysteresis: **0%**;
- strong synthetic hysteresis: **100%**.

Thus V2 controls the prespecified failure modes but is conservative at minimum replication.

The moderate synthetic effect is **not** used to weaken the test. If the real SMP effect is of that magnitude and is unresolved, it remains unresolved.

## Allowed conclusion if both gates pass

> **Later recovery of the same breeding sites occurred at higher surrounding population states than their earlier loss, beyond the temporal structure of the observed local abundance trajectories. Population recovery therefore did not simply retrace spatial collapse.**

## Mechanism boundary

A supported result does not uniquely identify:

- Allee effects;
- conspecific attraction;
- public information;
- site fidelity;
- social facilitation.

Same-site pairing controls fixed place identity. The V2 null controls generic temporal placement on the observed abundance trajectory without circular wrap.

Time-varying habitat, predators, disturbance, management and demographic composition remain possible explanations.

## Failure route

If:

- structural/identity/zero semantics fail;
- V2 common-shift support fails;
- \(p_{\mathrm{sign}}>0.05\);
- \(\Delta_{\mathrm{shift}}\le0\); or
- \(p_{\mathrm{shift}}>0.05\),

the integrated hysteresis manuscript is not activated.

No third null, alternate vacancy threshold, lag, abundance transform, species subset, trait screen or environmental rescue is permitted.

The existing Antarctic penguin manuscript remains the standalone paper.
