# SMP spatial-recovery hysteresis protocol v1

**Status:** frozen before receipt/opening of SMP bulk abundance magnitudes.

## Hypothesis

> **Population recovery does not retrace spatial collapse: after a breeding SiteID is abandoned, recolonization occurs only at a higher surrounding population state than the state at which the same SiteID was lost.**

For the same SiteID,

\[
H=A_{\mathrm{recolonize}}-A_{\mathrm{abandon}}.
\]

The directional prediction is \(H>0\), but positive \(H\) alone is not confirmatory.

## Stage A1 — count-blind candidate structure

Freeze species × MasterSite panels and retained SiteIDs without using Count magnitude.

Minimum panel support:
- >=3 retained SiteIDs;
- >=10 complete years;
- >=12-year calendar span;
- stable method/unit support.

Program minimum before identity resolution:
- >=10 panels;
- >=10 MasterSites;
- >=5 species.

## Stage A2 — physical identity resolution

Before positive/zero state is inspected, provider/site-history metadata must establish:

- one provider-resolved physical `master_site_key`;
- stable SiteID identity through the retained interval;
- mutually exclusive child SiteIDs;
- no overlap with parent/sibling totals;
- no boundary change;
- no retirement/replacement;
- provider-selected canonical Unit if more than one otherwise-valid Unit exists.

Ambiguous panels/SiteIDs are excluded. The inherited Stage-A year set can shrink but can never be extended.

## Provider zero-semantics gate

Stage B is unauthorized until provider/official documentation confirms:

1. a direct Count=0 row is a surveyed nil return;
2. an absent SiteID × year row means missing/not surveyed, not biological zero;
3. estimated or imputed zeroes can be excluded;
4. the compatible years/record family are documented.

Missing is never converted to zero.

## Stage B — occupancy history only

Reduce eligible direct observations to:

- occupied: Count > 0;
- vacant: provider-confirmed direct Count = 0;
- missing/unusable.

A completed vacancy spell is

\[
1\rightarrow0\rightarrow\cdots\rightarrow0\rightarrow1
\]

with all years from abandonment through recolonization calendar-consecutive and state-complete.

First colonization is excluded.

### Non-circular common-offset support

Assign each spell to the maximal calendar-consecutive state-complete block containing it.

For every **provider-resolved physical MasterSite × identical block**, take all spells in that group and freeze the intersection of integer offsets \(q\) for which every event year of every spell remains inside the block after adding \(q\).

Rules:
- no circular wrap;
- offset 0 must be present;
- all species/SiteIDs sharing the same physical MasterSite/block use the same offset in a null draw;
- the group must have >=3 common offsets or none of its spells enters Stage C.

This support is frozen using years and spell timing only, before abundance magnitudes open.

### Stage-B replication gate

After common-offset filtering require at least:
- 30 completed spells;
- 20 SiteIDs;
- 10 physical MasterSites;
- 5 species;
- 4 species with >=3 spells;
- 3 species with spells in >=2 MasterSites.

If any condition fails, stop before magnitude opening.

## Stage C — paired transition-state asymmetry

For focal SiteID \(j\), use leave-one-SiteID-out surrounding abundance:

\[
N_{-j,t}=\sum_{k\ne j}n_{k,t}.
\]

For abandonment \(t\to t+1\),

\[
A_e=
\frac{\log(1+N_{-j,t})+\log(1+N_{-j,t+1})}{2}.
\]

For later recolonization \(u\to u+1\),

\[
A_c=
\frac{\log(1+N_{-j,u})+\log(1+N_{-j,u+1})}{2}.
\]

Then

\[
H=A_c-A_e.
\]

These are annual transition-state proxies, not exact continuous-time thresholds.

## Fixed replication hierarchy

Average in this order:

1. repeated spells within SiteID;
2. SiteIDs within physical MasterSite;
3. physical MasterSites within species;
4. species with equal weight.

The primary observed statistic is the unweighted mean of species means, \(T_{obs}\).

## Confirmatory gate 1 — species sign-flip

Test whether species-level mean \(H\) values are centered above zero.

- exact enumeration for <=20 species;
- otherwise 100,000 sign flips;
- one-sided alpha = 0.05.

Require:
- \(T_{obs}>0\);
- \(p_{sign}\le0.05\).

Five species is the minimum capable of exact one-sided p<=0.05.

## Confirmatory gate 2 — structured non-circular common-offset null

A positive \(H\) can arise merely because recolonization occurs later along a changing parent-population trajectory.

For each of 9,999 null resamples:

1. keep every frozen SiteID, species, MasterSite, spell, event pattern and observed multivariate count trajectory;
2. for each physical MasterSite × block, draw one offset uniformly from its Stage-B-frozen common offset set;
3. apply that same offset to all species/SiteIDs/spells sharing the group;
4. never wrap across a block boundary;
5. recompute the identical hierarchical \(T\).

Report

\[
\Delta_{linear}=T_{obs}-\mathrm{median}(T_{linear,null})
\]

and the plus-one upper-tail probability \(P(T_{linear,null}\ge T_{obs})\).

Require:
- \(\Delta_{linear}>0\);
- \(p_{linear}\le0.05\).

## Why circular shifts are prohibited

A pre-outcome synthetic audit showed that the earlier circular null falsely supported **40/40 monotonic-drift datasets** because the circular seam manufactured extreme negative shifted contrasts.

That failed design is preserved in:
`results/SMP_SPATIAL_RECOVERY_HYSTERESIS_RECOVERY_AUDIT_FAILURE_V1.json`.

No SMP outcome data were involved in this repair.

## Confirmatory rule

Spatial-recovery hysteresis is supported only if **all four** conditions hold:

- \(T_{obs}>0\);
- \(p_{sign}\le0.05\);
- \(\Delta_{linear}>0\);
- \(p_{linear}\le0.05\).

No criterion can rescue failure of another.

## Interpretation

If supported, allowed:

> Spatial recovery occurred at a higher surrounding population state than spatial loss at the same breeding sites, beyond generic temporal alignment with the same local abundance histories.

> Population recovery did not simply retrace the spatial pathway of collapse.

Not allowed:

> Allee effects or conspecific attraction caused the asymmetry.

Same-site pairing controls fixed place identity/quality. The common-offset null controls generic temporal alignment without circular wrap. Neither removes time-varying habitat, predators, disturbance, management, or demographic composition.

## Stop rule

After magnitude opening, do not change:
- zero definition;
- vacancy-spell definition;
- abundance transform;
- transition midpoint;
- leave-one-site-out state;
- block definition;
- common-offset support;
- null family/resamples;
- hierarchy/weighting;
- site/species subset;
- vacancy-duration rule.

Any mechanism test requires independent information.
