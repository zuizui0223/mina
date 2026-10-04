# Manuscript v0.1 — mobile breeding nodes decouple colony identity from site identity in emperor penguins

## Working title

**Mobile breeding nodes decouple colony identity from site identity in emperor penguins**

Alternative:

**Persistence without a fixed place: time-scale-dependent breeding-node identity in emperor penguins**

## Abstract

Ecological monitoring commonly attaches population persistence to fixed geographic sites, even though habitat patches can change through time. Dynamic-landscape and patch-tracking theory already accommodate patch creation and destruction, and occupancy studies recognize that temporary movement outside a sampling unit can generate apparent extinction and colonization. A less explored empirical case occurs when an occupied breeding node itself relocates while the biological aggregation retains a continuous source-provided identity. We used public satellite-derived emperor penguin colony locations to quantify this mismatch directly.

For Astrid, Mertz and SANAE, a long-term remote-sensing series provided one validated annual reference location for each of ten breeding seasons from 2014/15 to 2023/24. We quantified the fraction of 27 consecutive-season transitions that would leave fixed geographic nodes of 0.5, 1, 2, 5 and 10 km radius. We then applied the same frozen radius set to an independent 2024 synthetic-aperture-radar dataset containing 596 huddles from six colonies to evaluate within-season false absence.

Interannual relocation was large relative to ordinary fixed-site definitions. Named colonies moved beyond the previous node in 26/27 transitions at 0.5 km, 24/27 at 1 km, 16/27 at 2 km, 8/27 at 5 km and 4/27 at 10 km. Consecutive-season displacement had a median of 2.30 km and a 95th percentile of 14.52 km. In contrast, within the independent 2024 SAR sample, only 1/48 post-anchor colony-dates fell outside a 0.5 km node and none fell outside a 1–10 km node; the 95th percentile minimum huddle distance from the seasonal anchor was 0.389 km.

Thus geographic site identity was stable at short within-season scales but frequently failed across breeding seasons, even while the source data retained the same named-colony identity. In ephemeral breeding habitat, persistence can therefore occur through relocation of the occupied node rather than persistence at a fixed place. Population identity, geographic node identity and habitat persistence should be treated as distinct spatial properties when interpreting long-term occupancy and turnover.

## Introduction

Patch occupancy is one of the central abstractions of metapopulation and island ecology. A spatial unit is observed as occupied or unoccupied through time, and transitions are interpreted as persistence, local extinction or colonization. This abstraction is powerful precisely because it reduces complex population dynamics to a stable set of geographic nodes.

The assumption that landscapes themselves are static is not required by modern metapopulation theory. Dynamic-landscape models explicitly allow habitat patches to be created, destroyed or altered through time (Keymer et al. 2000, *The American Naturalist*, doi:10.1086/303407). Patch-tracking metapopulation models likewise describe organisms whose persistence depends on tracking newly created habitat patches as old patches disappear (Snäll et al. 2003, *Oikos*, doi:10.1034/j.1600-0706.2003.12551.x). Empirical occupancy work also recognizes that temporary movement outside a sampling unit can be confounded with apparent extinction and colonization (Rota et al. 2009, *Journal of Applied Ecology*, doi:10.1111/j.1365-2664.2009.01734.x).

These frameworks distinguish population dynamics from changing habitat, but a practical ambiguity remains when the **occupied population node itself changes coordinates**. A fixed-site database may record disappearance from one location and appearance at another. If the biological aggregation is independently identified as the same colony, however, the ecological state is not necessarily extinction followed by colonization. It can instead be persistence through relocation.

Emperor penguins provide an unusually direct system for separating these interpretations. Colonies breed on fast ice, ice shelves and other frozen substrates whose geometry changes through time. Recent satellite studies have documented both within-season movement and substantial interannual relocation of named emperor colonies (Macdonald et al. 2026; Fretwell et al. 2026). Those studies establish that colonies move. Our question is different: **how strongly does fixed geographic site identity disagree with source-provided colony identity, and does that disagreement depend on temporal scale?**

We therefore distinguish two state variables:

\[
C_t = \text{source-provided named-colony identity}
\]

and

\[
L_t = \text{geographic location of the occupied breeding node}.
\]

A colony can satisfy

\[
C_{t+1}=C_t
\]

while

\[
L_{t+1}\ne L_t.
\]

We quantified the consequences using a radius-based fixed-node diagnostic frozen before displacement was examined. For three colonies with ten annual observations each, we asked how often consecutive breeding seasons would fall outside fixed nodes of 0.5–10 km. We then used an independent six-colony SAR dataset to ask the same question within one breeding season. This design tests whether node identity is simply unstable at all timescales or whether geographic sites are meaningful short-term units that become unreliable as population identifiers across years.

## Methods

### Conceptual estimand

We define **fixed-node false turnover** as disagreement between source-provided named-colony identity and a fixed geographic node definition.

For a named colony with annual location \(L_t\), a fixed node of radius \(r\) preserves site identity between consecutive seasons when:

\[
d(L_t,L_{t+1}) \le r.
\]

If:

\[
d(L_t,L_{t+1}) > r,
\]

a fixed-site representation would classify the colony as absent from the previous node even though the source retains the same named-colony identity.

This is an observational classification diagnostic. It does not imply demographic closure, identical individual membership or true colonization/extinction.

### Interannual dataset

The primary long-term analysis used public data associated with Macdonald et al. (2026, *Antarctic Science*; Zenodo doi:10.5281/zenodo.17380979) for Astrid, Mertz and SANAE.

The route files contain a source-supplied seasonal reference coordinate used in the published distance-to-fast-ice-edge measurements. A semantic audit was conducted before any interannual displacement was calculated. The audit required the source reference coordinate to be finite, date information to be parseable and the coordinate to be invariant within each colony-season.

The audit yielded 71 route features across 30 colony-seasons, with ten seasons per colony. Dates were parseable for all features, and each of the 30 colony-seasons had one invariant source reference coordinate; maximum within-season variation in the reference coordinate was 0 m. We therefore used that source-provided coordinate as the annual breeding-node anchor.

A previous semantic hypothesis that the coordinate should coincide with a route endpoint failed and remains in the audit trail. It was superseded only after the publication's method definition and within-season coordinate invariance were used to define the corrected semantic test, before interannual displacement was opened.

### Fixed-node radii

The radius set was frozen before displacement outcomes were inspected:

- 0.5 km;
- 1 km;
- 2 km;
- 5 km;
- 10 km.

No radius is interpreted as the biologically correct colony boundary. The complete aliasing curve is the primary result.

For each named colony we calculated displacement between consecutive annual anchors. Only transitions between adjacent breeding seasons entered the primary denominator.

### Identity-preserving displacement distribution

We report empirical q50, q90 and q95 of consecutive-season anchor displacement. These are descriptive summaries rather than recommended monitoring radii.

### Independent within-season dataset

To separate routine within-season movement from interannual node relocation, we used an independent 2024 SAR huddle dataset from six colonies: Atka Bay, Coulman Island, Cape Roget, Cape Washington, Franklin Island and Cape Crozier.

The dataset contained 596 mapped huddles across 54 colony-dates. For each colony, the earliest detected date defined the seasonal anchor. On each later date, the fixed node was considered occupied if at least one mapped huddle centroid fell within radius \(r\) of the anchor. This minimum-group rule prevents a colony split from being classified as absent when one group remains within the original node.

The same pre-frozen 0.5, 1, 2, 5 and 10 km radii were used. Forty-eight post-anchor colony-dates entered the within-season denominator.

### Inference

The long-term dataset contains only three independent named colonies, so all analyses are descriptive. No p-values, pooled frequency-law claims or continent-wide turnover estimates are reported.

## Results

### Interannual node relocation

Across the three named colonies there were 27 consecutive-season transitions.

The fixed-node aliasing curve was:

| Radius | Transitions outside previous node | Fraction |
|---|---:|---:|
| 0.5 km | 26/27 | 0.963 |
| 1 km | 24/27 | 0.889 |
| 2 km | 16/27 | 0.593 |
| 5 km | 8/27 | 0.296 |
| 10 km | 4/27 | 0.148 |

Consecutive-season displacement had:

- median = 2.30 km;
- q90 = 11.32 km;
- q95 = 14.52 km.

The largest transition was 63.21 km at Mertz between 2022/23 and 2023/24.

### Colony-specific patterns

Astrid was comparatively stable, with median displacement 1.76 km, q95 2.27 km and maximum 2.41 km. Seven of nine transitions exceeded 1 km, but none exceeded 5 km.

Mertz was highly heterogeneous, with median 3.91 km, q95 42.61 km and maximum 63.21 km. Three of nine transitions exceeded 10 km.

SANAE showed recurrent multi-kilometre relocation: median 5.15 km, q95 12.80 km and maximum 15.72 km. All nine transitions exceeded 1 km and five exceeded 5 km.

These differences are descriptive and do not define general colony types.

### Within-season validation

The independent 2024 SAR dataset contained 48 post-anchor colony-dates.

False absence was:

| Radius | Post-anchor dates outside node | Fraction |
|---|---:|---:|
| 0.5 km | 1/48 | 0.021 |
| 1 km | 0/48 | 0 |
| 2 km | 0/48 | 0 |
| 5 km | 0/48 | 0 |
| 10 km | 0/48 | 0 |

The minimum distance from the seasonal anchor to any mapped huddle on later dates had:

- median = 0.143 km;
- q90 = 0.350 km;
- q95 = 0.389 km.

Thus a 1 km fixed node retained the source-named colony on every post-anchor date in this independent one-season sample.

## Discussion

### Persistence can occur through relocation

The principal result is a separation between colony identity and geographic node identity.

Within a breeding season, fixed geographic nodes were remarkably stable at kilometre scales. Across breeding seasons, however, the same named colonies frequently re-established beyond those node boundaries.

At a 1 km radius, none of 48 independent within-season post-anchor observations appeared absent, whereas 24 of 27 interannual transitions left the previous node.

The two datasets contain different colonies and should not be used to estimate a formal within-versus-between ratio. Their contrast nevertheless establishes an important qualitative pattern: geographic site identity can be a valid short-term sampling unit yet a poor long-term population-identity unit.

### Dynamic patches versus mobile occupied nodes

Dynamic-landscape theory already allows habitat patches to appear and disappear. Patch-tracking metapopulations already describe organisms that colonize newly created patches. The present result adds a narrower empirical distinction.

In the source data, biological colony identity is retained while the occupied breeding-node coordinate changes. A fixed-site interpretation can therefore decompose a continuing named colony into apparent extinction at \(L_t\) and colonization at \(L_{t+1}\).

The alternative state is:

\[
\text{colony identity persists}
+
\text{breeding node relocates}.
\]

We term this **relocation-based spatial persistence**.

### Why this is not simply temporary emigration

Occupancy theory has long recognized temporary emigration as a source of apparent occupancy change. The emperor case differs in scale and object.

The population-level aggregation itself is re-established at a new breeding coordinate between years, and the source explicitly retains the named colony identity. We can therefore quantify disagreement between site identity and colony identity directly rather than infer movement indirectly from detection/non-detection patterns.

### Consequences for island and metapopulation ecology

Island and patch ecology often treats patch identity as a stable spatial reference. The emperor system shows that at least three kinds of persistence should be distinguished:

1. **habitat persistence** — whether the physical breeding opportunity exists;
2. **site persistence** — whether the same geographic node remains occupied;
3. **population identity persistence** — whether the biological aggregation remains continuously identified.

These properties can diverge.

A geographic node can disappear as a population site even when the population-level colony identity continues elsewhere.

### Relation to the broader Antarctic program

Paper 1 showed that breeding use can contract within persistent spatial systems beyond proportional thinning.

Paper 2 showed that changing terrestrial opportunity does not generally predict where Pygoscelis breeding use increases.

Paper 3 shows that, in an ephemeral breeding system, the geographic node itself can change while colony identity persists.

Together, the program distinguishes:

\[
\text{allocation within place}
\rightarrow
\text{capacity of place}
\rightarrow
\text{identity of place}.
\]

This provides a more explicit state-space view of island population dynamics than a single site-occupancy variable.

### Limitations

The long-term result is based on three named colonies and should not be generalized into a continent-wide probability of relocation.

Named-colony identity is source-provided. It does not establish demographic closure, continued membership of the same individual birds or absence of immigration/emigration.

The 14.52 km q95 is an empirical summary, not a universal correct colony radius.

The 63 km Mertz transition is an observed extreme, not evidence for typical annual movement.

No environmental mechanism is tested. In particular, we do not attribute the movement curve causally to fast-ice change, ice-shelf calving or prey conditions.

### Conclusion

> **In emperor penguins, modest geographic nodes retain colony identity within a breeding season, but the same named colonies frequently re-establish beyond those nodes between years. Persistence in an ephemeral breeding landscape can therefore occur through relocation rather than persistence at a fixed place.**

## References cited in positioning

- Keymer JE, Marquet PA, Velasco-Hernández JX, Levin SA. 2000. Extinction thresholds and metapopulation persistence in dynamic landscapes. *The American Naturalist* 156:478–494. doi:10.1086/303407.
- Snäll T, Ribeiro PJ Jr, Rydin H. 2003. Spatial occurrence and colonisations in patch-tracking metapopulations: local conditions versus dispersal. *Oikos* 103:566–578. doi:10.1034/j.1600-0706.2003.12551.x.
- Rota CT et al. 2009. Occupancy estimation and the closure assumption. *Journal of Applied Ecology* 46:1173–1181. doi:10.1111/j.1365-2664.2009.01734.x.
- Macdonald GJ et al. 2026. Year-round movement of emperor penguin colonies observed from space. *Communications Earth & Environment* 7:703.
- Fretwell PT et al. 2026. Dynamic emperor penguin colonies. *Communications Biology*.
