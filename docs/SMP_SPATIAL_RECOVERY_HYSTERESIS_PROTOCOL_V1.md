# SMP spatial-recovery hysteresis protocol v1

**Status:** frozen before receipt/opening of the bulk SMP abundance magnitudes.

## Hypothesis

> **Spatial recovery is hysteretic in colonial breeders: a breeding site that has been abandoned is recolonized only after the surrounding population has recovered beyond the population state at which that same site was lost.**

For the same SiteID:

[
H = A_{recolonize} - A_{abandon}.
]

Primary prediction:

[
H>0.
]

## Why this is the discriminating island-ecology test

The penguin results show replicated concentration during decline and, at the regional scale, lower effective breeding-site number even in increasing networks. Those results suggest but do not test weak spatial reversibility.

A static reversible basin model maps population size and stable site quality onto occupancy. For the same physical SiteID, abandonment and recolonization should therefore occur at approximately the same surrounding population state, apart from stochastic noise.

Positive feedback, conspecific attraction, site fidelity or other history-dependent processes can break that symmetry. Once a site is empty, the absence of an established breeding aggregation can raise the population state required for recolonization.

The present test deliberately targets **the asymmetry itself**, not a specific social mechanism.

## Stage A — stable hierarchy

Reuse the stricter frozen species × MasterSite / SiteID support gate.

No count magnitude is used to select panels.

## Stage B — occupancy-state cycles only

Convert each retained direct count to one of three states:

- positive;
- explicit zero;
- missing/unusable.

Missing is never zero.

A completed vacancy spell is:

[
1 ightarrow 0 ightarrow cdots ightarrow 0 ightarrow 1
]

with every intervening calendar year complete and consecutive.

The support gate is frozen at:

- >=30 completed spells;
- >=20 SiteIDs with completed spells;
- >=10 MasterSites;
- >=5 species;
- >=4 species with >=3 spells;
- >=3 species with spells from >=2 MasterSites.

If this fails, stop before opening abundance magnitudes.

## Stage C — paired threshold test

For focal SiteID (j), remove that site's count from the parent total:

[
N_{-j,t}=sum_{k
e j} n_{k,t}.
]

For an abandonment transition (t	o t+1):

[
A_e = rac{log(1+N_{-j,t})+log(1+N_{-j,t+1})}{2}.
]

For the later recolonization transition (u	o u+1):

[
A_c = rac{log(1+N_{-j,u})+log(1+N_{-j,u+1})}{2}.
]

Then:

[
H=A_c-A_e.
]

The same SiteID is its own control for stable place quality.

## Replication hierarchy

Average in this order:

1. repeated spells within SiteID;
2. SiteIDs within MasterSite;
3. MasterSites within species;
4. species with equal weight.

The primary statistic is the unweighted mean of species means.

Inference is a one-sided sign-flip test on species means. If there are <=20 species, enumerate all sign combinations; otherwise use 100,000 frozen random sign flips.

## Interpretation

### Supported H > 0

Allowed:

> spatial recovery requires a higher surrounding population state than spatial loss at the same breeding sites.

> population recovery does not simply retrace the spatial pathway of decline.

Not yet allowed:

> conspecific attraction causes hysteresis.

### H around zero

Supports a broadly reversible occupancy response at the measured SiteID scale; the MAPPPD increasing-network observation would not generalize into an occupancy-hysteresis rule.

### H < 0

Opposite to the social-recolonization-barrier prediction; recolonization occurs at lower surrounding abundance than abandonment.

## Relation to island biogeography

This reframes colonization and extinction as potentially history-dependent transitions of the same breeding islands. The island object is not only whether a patch is suitable, but whether it is already socially occupied.

The hypothesis is therefore about the symmetry of **extinction and recolonization thresholds**, not merely abundance–occupancy correlation.

## Mechanism boundary

A positive result can be produced by social feedback, site fidelity or persistent biological memory, but also by time-varying environmental deterioration. Stable SiteID pairing removes fixed site quality, not all temporal confounding.

The current paper should therefore make social Allee/conspecific attraction a mechanistic interpretation, not the estimand itself.

## Stop rule

After abundance magnitudes are opened, do not change the vacancy-spell definition, log transform, leave-one-site-out parent state, transition midpoint, hierarchy, weighting, or support thresholds.
