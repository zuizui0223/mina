# PR189 novelty audit after the recovery result

**Status:** superseded by `PR189_RECOVERY_NOVELTY_AUDIT_V2.md` after independent Heard Island triangulation.

## What is not new

### Breeding capacity can constrain Adélie population growth

Southwell & Emmerson (2020) already showed across East Antarctic Adélie populations that low breeding-habitat availability is associated with reduced population growth, higher occupancy of available habitat, and use of steeper, otherwise less-used terrain.

Therefore PR189 should **not** claim that it newly discovers density dependence, terrestrial breeding limitation, or the importance of breeding capacity.

### Metapopulation recovery can be spatially incomplete

Wilson et al. (2023) developed a spatial recovery framework in which aggregate abundance can recover while some local populations remain collapsed. Their "hidden collapse" regime makes the important conservation point that aggregate recovery can mask local failure.

Therefore PR189 should **not** claim that it is the first study to distinguish aggregate and spatial recovery.

### Diversity/evenness metrics are established

The reciprocal Simpson index is a standard Hill effective-number metric. PR189 uses it as an abundance-weighted measure of spatial redundancy; the metric itself is not novel.

## A 2026 Ross study already explains colony-specific demographic divergence

Dugger et al. (2026) explicitly set out to identify demographic mechanisms behind the divergent Ross Island colony trajectories.

Their 25-year mark-recapture analysis reports:
- the lowest age-related recruitment at Royds;
- recruitment at Crozier almost twice as high, with Bird intermediate;
- breeder movement between colonies below 0.20%;
- the highest breeding propensity at Crozier and lowest at Bird;
- pre-breeder apparent survival highest at Bird, not Crozier.

They also describe Bird and Crozier as having more than doubled over the study period while Royds declined and then slowly recovered/stabilized.

Therefore PR189 should **not** claim:
- first discovery of divergent Ross colony growth;
- first demographic explanation of Crozier versus Royds/Bird trajectories;
- first evidence that recruitment differs among Ross colonies.

The mark-recapture study is instead unusually useful independent support for interpreting the census allocation pattern.

## What PR189 adds

The Ross result is different from a hidden collapse.

During frozen 2001-2012 recovery:

- total abundance increased 3.70-fold;
- all 3/3 biological colonies increased;
- all 6/6 frozen census components increased;
- yet E3 declined 10.7% and E6 declined 14.0%.

There is no collapsed local node to explain the loss of redundancy.

Instead, the system became more concentrated because one already dominant colony increased disproportionately.

This is **differential amplification**.

The decline-side evidence supplies the mirror process: concentration can also arise through **differential attrition**, where local units lose abundance unequally.

The contribution is therefore not the discovery of Ross colony heterogeneity. It is the **cross-phase spatial-state decomposition**: the empirical separation of two opposite demographic routes to the same concentration state, plus the explicit demonstration that strong numerical recovery can lose abundance-weighted spatial redundancy even when every monitored unit grows.

## Exact general statement

For fixed breeding units with local instantaneous growth rates r_i,

    d log(E) / dt = 2 (r_bar - r_D),

where r_bar is abundance-weighted mean growth and r_D is growth weighted by squared abundance shares.

Thus concentration increases whenever already dominant units have higher growth than the metapopulation average.

This can occur under either:

- negative total growth: dominant nodes lose least;
- positive total growth: dominant nodes gain most.

Conversely, recovery becomes spatially spreading when small nodes grow strongly enough that r_D < r_bar.

The mathematics is elementary and not itself presented as a novel theorem. Its value is to identify the ecological estimand that links the cases: **dominance-weighted growth allocation**.

## Why Beaufort matters

Beaufort lies on the opposite side of the same decomposition.

From 2004 to 2010 its new subcolony grew 108%, versus 33.6% in the established main colony, and received about 3.15 times the gain expected from its starting share.

E therefore increased slightly while total abundance increased.

The independent habitat/movement study reports a large release of usable nesting habitat and declining export to Ross Island after habitat became available.

Beaufort is therefore consistent with a capacity-opening route that redirects growth toward a previously tiny/new breeding unit.

It does not prove a universal capacity threshold.

## Mechanistic support on Ross Island

The Ross census amplification rank is:

    Crozier > Bird > Royds.

Independent individual-demography work from the same system reports the same ordering for local recruitment, while adult movement between colonies is very low.

Separate nesting-habitat work reports higher and less variable reproductive success at Crozier than Royds.

These data streams support a quality-weighted amplification interpretation, but they overlap the Ross system and do not constitute an independent system-level replication.

## Important prior that sharpens the mechanism

Southwell & Emmerson (2020) found that breeding habitat availability can impose density-dependent growth limitation and force occupation of poorer terrain.

This means the useful new question is no longer:

> Does capacity matter?

It is:

> **How does heterogeneity in demographic quality and dynamic capacity determine where recovery is allocated across a spatial network?**

That question distinguishes:

- stable spatial quality differences, which can amplify dominant nodes;
- newly released capacity, which can redirect growth toward smaller/new nodes.

## Relation to existing metapopulation recovery theory

Wilson et al. emphasize recovery regimes determined by local productivity, dispersal, network structure, density dependence, and disturbance spatial structure.

PR189 fits naturally inside that broad theory but adds a specific empirical recovery state that is easy to miss if monitoring focuses on occupancy:

> **hidden concentration during recovery** — aggregate abundance rises and every monitored node grows, yet abundance-weighted spatial redundancy falls because growth is disproportionately allocated to dominant nodes.

Use this phrase as a descriptive label, not as a claim that no prior study has ever observed an analogous pattern.

## Conservation implication

Occupancy alone would call Ross recovery spatially intact because all monitored breeding units persisted and grew.

Total abundance would call it a strong recovery.

E shows a third dimension: the recovering population became more dependent on the dominant colony.

Therefore three recovery axes should be kept distinct:

1. total abundance;
2. occupancy/persistence of local nodes;
3. abundance-weighted spatial redundancy.

A system can improve on the first two while deteriorating on the third.

## Current novelty level

The strongest defensible novelty is **conceptual-empirical**, not taxonomic and not mathematical:

> A strong numerical recovery can reduce spatial redundancy through differential amplification even when every monitored breeding unit increases; the same concentration metric can be generated during decline by differential attrition, so spatial concentration does not identify the sign or mechanism of population change.

The broader two-mode quality-versus-capacity mechanism remains a generated hypothesis until tested outside Ross/Beaufort.


## Additional mechanism already anticipated in the literature

Schmidt et al. (2021) found higher and less variable reproductive success at Crozier than Royds and proposed a positive feedback in colonial nesting geometry: as colonies grow, perimeter-to-area ratio can decline, reducing edge exposure and potentially increasing average subcolony quality.

This means a self-reinforcing advantage of large colonies is biologically plausible and partly anticipated. PR189 should not present positive feedback from colony size/geometry as newly discovered.

What remains distinctive is the **state-space consequence** of such local feedback: it can turn aggregate recovery into a loss of spatial redundancy rather than a restoration of it.
