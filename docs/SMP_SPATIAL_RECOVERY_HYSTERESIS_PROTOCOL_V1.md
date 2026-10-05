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

A positive paired difference alone is not sufficient for confirmation. The species-balanced observed statistic must also exceed a structured common-phase null that preserves each MasterSite block's multivariate abundance trajectory.

## Why this is the discriminating island-ecology test

The Antarctic penguin results show replicated concentration during decline and, at regional scale, lower effective breeding-site number even in increasing networks. Those results suggest weak spatial reversibility but do not directly compare loss and later recovery of the same place.

A simple reversible site-quality or basin picture predicts that, for a stable physical SiteID, abandonment and later recolonization should occur at approximately the same surrounding population state, apart from stochasticity and observation timing.

History-dependent processes can break that symmetry. Once a breeding site is empty, loss of an established aggregation, site fidelity, conspecific information or other biological memory may raise the surrounding population state required for recolonization.

The estimand is the **loss–recovery asymmetry itself**, not any particular social mechanism.

## Stage A — stable physical hierarchy

Begin with the count-blind species × MasterSite / SiteID structural gate.

Before any occupancy state is examined, apply a provider/site-history identity gate. A SiteID enters the hysteresis test only if provider metadata support all of the following over the frozen retained interval:

- stable physical identity;
- mutually exclusive child Site within its MasterSite;
- no overlap with parent or sibling Site records;
- no boundary change;
- not retired or replaced.

After identity-ineligible SiteIDs are removed, retain the **exact Stage-A complete-year set**. Do not extend the time window merely because site removal would make additional years complete.

If multiple structurally eligible count Units remain for one species × MasterSite, the panel is excluded unless the provider identifies a canonical Unit before occupancy states are opened.

## Provider zero-semantics gate

Stage B is unauthorized until BTO/SMP documentation or provider correspondence confirms:

1. a direct observed Count = 0 row is a surveyed nil return;
2. absence of a SiteID × year row is not biological zero;
3. estimated or imputed zeroes can be excluded from the primary analysis.

The confirmation is stored in a frozen JSON with a non-empty source citation/description, a compatible start year, a compatible end year, and a description of the record family/era for which those semantics are valid.

If any of these conditions cannot be confirmed, stop the hysteresis route rather than infer zero semantics from the data. If the confirmed zero semantics cover only part of 1986–2024, Stage B uses only the inherited complete years inside that documented interval. The interval may shorten a panel but can never add years.

## Stage B — occupancy-state cycles only

For the identity-resolved frozen roster, reduce every eligible direct count to:

- **occupied:** count \(>0\);
- **vacant:** provider-confirmed explicit count \(=0\);
- **missing/unusable:** never interpreted as vacancy.

A completed vacancy spell is

\[
1\rightarrow0\rightarrow\cdots\rightarrow0\rightarrow1
\]

with every year from abandonment through recolonization calendar-consecutive and complete.

First colonization is excluded because it has no paired prior abandonment threshold.

### Phase-block support

Each completed spell is assigned to the maximal calendar-consecutive block of frozen complete years containing the entire spell.

Only spells in blocks of at least **6 years** are eligible for Stage C. This threshold is frozen before magnitude opening.

### Program support gate

Within the provider-confirmed interval, begin from inherited Stage-A complete years and retain only years in which every retained SiteID has one usable direct positive/explicit-zero state. Missing/unparseable records remove that year; they are never converted to zero. A panel must still retain at least 10 such state-complete years spanning at least 12 calendar years. After that scope restriction and the phase-block filter, require at least:

- 30 completed spells;
- 20 distinct SiteIDs;
- 10 MasterSites;
- 5 species;
- 4 species with at least 3 spells;
- 3 species with spells in at least 2 MasterSites.

If any condition fails, stop before abundance magnitudes are opened.

## Stage C — paired threshold estimand

For focal SiteID \(j\), define surrounding population state from the same frozen MasterSite while excluding the focal SiteID:

\[
N_{-j,t}=\sum_{k\neq j}n_{k,t}.
\]

Excluding the focal SiteID prevents its own disappearance or return from mechanically generating the predictor.

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

The same SiteID is therefore its own control for fixed site identity and stable site quality. Because SMP is sampled annually, \(A_e\) and \(A_c\) are frozen **transition-state proxies** from the two censuses bracketing each transition, not exact continuous-time demographic thresholds.

## Replication hierarchy

Average in this fixed order:

1. repeated spells within SiteID;
2. SiteIDs within MasterSite;
3. MasterSites within species;
4. species with equal weight.

The primary observed statistic is

\[
T_{\mathrm{obs}}
=
\mathrm{mean}(\text{species mean }H).
\]

This prevents species with many monitored sites from dominating macroecological inference.

## Primary inference 1 — species sign-flip

Test whether species-level mean \(H\) values are centered above zero.

If there are at most 20 species, enumerate every sign assignment exactly. Otherwise use 100,000 frozen random sign flips with seed 20261005.

This test alone is insufficient for confirmation.

## Primary inference 2 — structured common-phase null

A positive \(H\) could arise because abandonment dates happen to occur earlier than recolonization dates on a trending or autocorrelated MasterSite abundance trajectory.

The structured null preserves that temporal structure.

For each species × MasterSite × frozen contiguous phase block:

1. retain the complete multivariate SiteID count matrix;
2. retain every frozen vacancy spell and its observed event-year positions;
3. draw one circular year shift for the entire block;
4. apply the **same shift to all SiteIDs and all spells in that block**;
5. compute \(H\) at the shifted abundance phases while keeping the event-year pattern fixed;
6. aggregate through the identical spell → SiteID → MasterSite → species hierarchy.

Use 9,999 resamples with seed 20261005.

Because the whole physical MasterSite/block is shifted together, the null preserves each site's marginal abundance series, within-species cross-site covariance, dependence among multiple spells, and—when frozen blocks align—cross-species temporal covariance generated by shared local conditions.

The circular seam is accepted as part of the frozen null and is not tuned after outcomes.

Report

\[
\Delta_{\mathrm{phase}}
=
T_{\mathrm{obs}}-
\mathrm{median}(T_{\mathrm{phase,null}})
\]

and the plus-one upper-tail probability

\[
P(T_{\mathrm{phase,null}}\ge T_{\mathrm{obs}}).
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
\Delta_{\mathrm{phase}}>0,
\]

and

\[
p_{\mathrm{phase}}\le0.05.
\]

No criterion can rescue failure of another.

## Interpretation

### Confirmatory support

Allowed:

> **Spatial recovery occurred at a higher surrounding population state than spatial loss at the same breeding sites, beyond generic temporal alignment with the observed MasterSite abundance trajectories.**

> **Population recovery did not simply retrace the spatial pathway of collapse.**

Not allowed:

> conspecific attraction caused the hysteresis.

### Positive H, phase null not rejected

Interpretation:

> the apparent abandonment–recolonization asymmetry is compatible with temporal alignment on the observed abundance trajectories.

Do not claim spatial hysteresis.

### H unresolved or negative

The independent test does not support the predicted recovery barrier.

Do not rescue the hypothesis by redefining vacancy, excluding species, changing abundance transforms, or altering the null.

## Relation to island biogeography

The hypothesis concerns the symmetry of extinction and recolonization thresholds at the **same breeding islands**.

A reversible mapping treats occupancy as a function of current place and current surrounding population state. A history-dependent mapping additionally depends on whether the site is already occupied:

\[
P(O_{t+1}=1\mid N,\mathrm{site},O_t)
\neq
P(O_{t+1}=1\mid N,\mathrm{site}).
\]

A supported positive H would therefore show that the same physical breeding site has different demographic thresholds for spatial loss and spatial recovery.

## Mechanism boundary

A supported result can be consistent with social positive feedback, conspecific attraction, site fidelity, public information, or other biological memory.

It can also arise from time-varying habitat deterioration, predation, disturbance or management.

Same-Site pairing removes fixed site quality. The structured phase null removes generic temporal alignment with the observed surrounding abundance trajectory. Neither identifies a unique causal mechanism.

## Stop rule

After magnitude opening, do not change:

- vacancy-spell definition;
- explicit-zero rule;
- identity-resolution rule;
- frozen complete-year set;
- minimum 6-year phase block;
- transition midpoint;
- \(\log(1+N)\) transform;
- leave-one-SiteID-out parent state;
- circular-shift scheme;
- number of phase resamples;
- hierarchy or weighting;
- species/SiteID subset;
- vacancy-duration threshold.

Any mechanism test requires new independent information.
