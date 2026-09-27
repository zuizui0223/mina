# Manuscript spine — island as a demographic boundary v1

## Working title

**Are islands demographic islands? Hierarchical coherence in Adélie penguin breeding populations**

Alternative:

**Geographic islands structure annual demographic coherence in a colonial marine predator**

## Central question

For a highly mobile marine predator whose breeding sites are divided among nearby islands, does the geographic island label correspond to a real demographic level, or is it merely a convenient census grouping?

The focal test asks whether subcolonies assigned to the same island share annual demographic deviations beyond colony-specific behavior and the common regional year signal, relative to pseudo-island partitions matched for observation history and abundance.

## Main result

The missingness-robust frozen test strongly supports island-level demographic coherence.

Five-island analysis, 1991–2017:

- 56 eligible colony codes;
- same-island mean residual pair-year product = **+0.05618**;
- different-island mean residual pair-year product = **−0.03662**;
- island contrast = **+0.09280**;
- abundance/coverage-stratified pseudo-island permutation: **p = 0.00010**.

The result persists after removing Litchfield Island:

- 47 eligible colony codes;
- contrast = **+0.08571**;
- **p = 0.00100**.

Supported statement:

> After removing colony-specific scale and the regional year component, subcolonies on the same geographic island share annual demographic deviations more strongly than expected under matched pseudo-island assignments.

Do **not** interpret the negative between-island residual product as biological anti-synchrony. Year-centering creates a zero-sum residual constraint. The inferential object is the observed island-versus-pseudo-island contrast.

## What changed from the previous hypothesis

### Rejected: within-island spatial insurance

The original H1 predicted compensatory dynamics among subcolonies, such that within-island synchrony would be unusually low and aggregation would stabilize the island total.

That prediction failed.

In the frozen complete-case exploratory partition:

- observed mean within-island growth synchrony phi = 0.255;
- pseudo-island null mean = 0.195;
- lower-tail p = 0.999;
- observed hierarchy-gap upper-tail p = 0.979.

Thus the data do not support a story in which subcolonies within an island function primarily as compensating insurance units.

### Supported replacement: island-level common deviations

The missingness-robust analysis instead finds that subcolonies on the same island tend to move in the same annual direction after a regional year effect is removed.

The island therefore behaves as a **mesoscale demographic coherence unit**, nested between subcolony and region.

## Ecological interpretation

The result is consistent with island-shared processes acting on breeding subcolonies. Candidate mechanisms include:

- island-scale snow accumulation and melt;
- shared geomorphology and drainage;
- common local access to nearshore foraging habitat;
- island-specific breeding phenology or disturbance;
- spatially structured recruitment or site fidelity.

None is identified by the current covariance test.

## Existing mina results under the new spine

### Background, not novelty

- five-island long-term PC1 = 96.4%;
- annual island-total growth synchrony is moderate;
- year explains 53.5% and island 33.0% of log-abundance variation.

These establish regional forcing plus persistent local structure but do not themselves establish the island boundary.

### Secondary local-state result

Effective colony number remains a conditional association, not a predictive pillar. Its role becomes:

> internal breeder distribution varies with demographic state inside a spatial unit that is independently shown to possess island-level annual coherence.

Do not use N_eff to define the island-boundary result.

### Litchfield

Litchfield remains a useful collapse endpoint, but the island-coherence result does not depend on it. The four-island exclusion test remains significant.

### Torgersen

Torgersen is an important heterogeneity case. Its standalone descriptive within-island residual product is slightly negative, unlike Christine, Cormorant, Humble and Litchfield. Therefore do not claim every island individually exhibits positive subcolony coherence.

This heterogeneity makes the GIS crosswalk particularly valuable: it can test whether Torgersen's mapped habitat structure explains why its internal dynamics differ from the pooled island pattern.

## Figure plan

### Figure 1 — hierarchy and study system

Subcolony → island → Palmer region.

Show the five breeding islands and the conceptual question: which boundary captures shared annual demographic deviations?

### Figure 2 — island versus pseudo-island covariance

Primary figure.

Plot the 20,000 pseudo-island null distribution and the observed covariance contrast (+0.0928).

Inset: five-island and no-Litchfield estimates.

### Figure 3 — residual annual coherence

Heat map or network of pairwise residual covariance among eligible colony codes, grouped by island.

Do not imply geographic-distance effects unless coordinates are added later.

### Figure 4 — temporal persistence

Show descriptive contrasts:

- 1991–2006: +0.0838;
- 2007–2017: +0.1806.

The late record has fewer pair-years because of collapse and identifier discontinuities, so these values are descriptive rather than separate confirmatory tests.

### Figure 5 — local heterogeneity

Per-island descriptive within-pair products, highlighting that Torgersen differs from the other islands.

Connect this to independent mapped Torgersen habitat evidence without claiming colony-code-level spatial validation.

## Next decisive gate

The remaining inferential ambiguity is **island boundary versus geographic proximity**.

Current data establish that the census island label predicts demographic covariance beyond matched pseudo-island grouping. They do not show that crossing water adds information after pairwise geographic distance is controlled.

The next confirmatory model should be frozen before colony coordinates are opened:

```
pairwise residual covariance
    ~ f(distance)
    + same_island
```

with a spatially constrained permutation or pairwise mixed model.

The colony-code ↔ GIS crosswalk is therefore the direct route from:

**island labels are demographic units**

to the stronger claim:

**the geographic island boundary itself is a demographic discontinuity beyond distance**.

## Claim boundary

Supported now:

> Geographic island membership captures a reproducible mesoscale structure in annual Adélie penguin demographic deviations near Palmer Station.

Not yet supported:

> Coastlines causally delimit penguin populations.

> Within-island movement creates the covariance pattern.

> Within-island subcolonies provide compensatory spatial insurance.

> Every Palmer island individually shows the same internal covariance structure.
