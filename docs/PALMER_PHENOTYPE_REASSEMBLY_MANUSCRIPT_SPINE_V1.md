# Palmer phenotype reassembly manuscript spine v1

## Working title

**Species sorting creates transient island phenotypes in Palmer penguins**

Alternative:

**Apparent island phenotypes are compositional and temporally reassembled in Palmer penguins**

## One-sentence ecological claim

Functional differentiation among neighboring Palmer breeding sites is generated
mainly by species sorting, while the residual within-Adélie island phenotype is
weak, changes sign among years, and transfers poorly to a different breeding
season.

## Why this is an ecological paper

The question is not whether morphology can classify an island.

The ecological question is **where island-level functional differentiation comes
from**.

An island assemblage can differ functionally because:

1. different species occupy different breeding sites;
2. the same species develops persistent site-specific phenotypes;
3. transient demographic, age, condition or foraging composition produces a
   site signal that is reassembled between years.

The Palmer data distinguish these levels unusually well because the same three
breeding sites contain multiple Pygoscelis species and Adélie penguins are
sampled repeatedly across three breeding seasons.

## Evidence architecture

### Result 1 — the obvious island phenotype is mainly compositional

Across the full Palmer Penguins assemblage, morphology strongly predicts
breeding-site identity relative to a pooled site distribution.

Frozen decomposition:

- morphology versus pooled site marginal: **+0.38946** nats;
- species identity versus pooled site marginal: **+0.53601** nats;
- morphology beyond species identity: **−0.08375** nats.

Ecological interpretation:

> The strongest island-associated phenotype is a community-composition signal:
> different penguin species occupy the breeding sites in different proportions.

This is species sorting / assemblage structure, not evidence that individuals of
the same species form stable island ecotypes.

## Result 2 — fixed within-Adélie island effects are weak

Restricting the analysis to Adélie penguins removes species turnover.

After sex, year, egg date and clutch completion are controlled, fixed island
identity explains only small additional fractions of structural-trait variance:

- bill length partial R² = **0.0166**;
- bill depth partial R² = **0.0154**;
- flipper length partial R² = **0.0479**.

These effect sizes are not zero, but they are small relative to the conspicuous
full-assemblage island signal.

## Result 3 — island contrasts repeatedly change sign through time

Equal-sex island contrasts reverse among the three breeding seasons:

- bill length: **3/3** island pairs reverse;
- bill depth: **3/3**;
- flipper length: **2/3**.

Body mass and isotope traits also show extensive sign reversal but remain
secondary because body mass is condition-sensitive and blood isotopes integrate
pre-breeding foraging.

This is the clearest descriptive signature of temporal reassembly: an island that
is relatively high for a trait in one year is not consistently high in the next.

## Result 4 — within-year morphology exists, but it does not persist

The frozen persistence extension uses exactly the same structural traits and
nearest-centroid classifier for two validation scales.

### Same-year leave-one-individual-out

Mean balanced accuracy:

**0.4482**

Year-specific values:

- PAL0708: **0.5035**;
- PAL0809: **0.3912**;
- PAL0910: **0.4500**.

### Leave-one-year-out transfer

Mean balanced accuracy:

**0.3424**

Year-specific values:

- PAL0708 held out: **0.3257**;
- PAL0809 held out: **0.3681**;
- PAL0910 held out: **0.3333**.

Three-island chance reference:

**0.3333**

Persistence gap:

**0.1059** balanced-accuracy units.

Ecological interpretation:

> Structural morphology carries modest information about breeding-site identity
> within a season, but almost none of that information survives transfer to a
> different year.

The result is therefore not “no island phenotype.” It is **a temporally unstable
island phenotype**.

## Result 5 — isotope signatures do not rescue persistence

The same comparison for δ15N + δ13C gives:

- same-year mean balanced accuracy = **0.3597**;
- cross-year mean balanced accuracy = **0.3403**;
- persistence gap = **0.0194**.

This provides no evidence that pre-breeding isotope space contains a more stable
island signature than structural morphology.

Because blood isotopes integrate pre-breeding foraging, this remains a secondary
sensitivity rather than a local-island trophic mechanism test.

## Central ecological synthesis

The evidence is hierarchical:

community level
    strong island functional differentiation
        ↓ mostly species composition

within Adélie
    modest island differentiation within a year
        ↓ repeated sign reversals

across years
    island phenotype ~ non-transferable

The Palmer “island phenotype” is therefore better interpreted as **dynamic
assembly** than as a fixed island ecotype.

Species sorting creates the largest functional contrast among sites, while the
within-species component is reassembled among breeding seasons.

## Island-ecology framing

Pygoscelis penguins are central-place marine foragers breeding on discrete
terrestrial patches. The breeding island can filter which species and which
individuals occupy a site without containing the main trophic resource base.

This makes the system useful for separating:

- **community sorting among islands**;
- **persistent within-species differentiation**;
- **temporally labile within-species composition**.

The present result supports the first and third much more strongly than the
second.

## Discussion structure

### D1. Snapshot functional differentiation can be compositional

A strong island classifier does not imply that the island has produced a local
phenotype. In a multi-species assemblage, species turnover can create large
functional differences among sites.

This is a community-assembly result.

### D2. Within-species spatial differentiation can be real but ephemeral

Same-year structural morphology carries island information above chance, so the
within-Adélie signal is not completely absent.

However, the signal changes among years and fails to transfer temporally.

Candidate biological sources include annual differences in cohort composition,
age structure, body condition, breeder arrival, or nonrandom site use. The
present data do not distinguish these mechanisms.

### D3. Persistent island ecotype is not supported

Three observations converge:

1. fixed island partial R² is small;
2. pairwise trait contrasts reverse signs;
3. cross-year island classification is essentially at chance.

Together these are difficult to reconcile with a stable three-island phenotype
over the sampled period.

Do not convert this into evidence against evolutionary differentiation at other
timescales or locations.

### D4. Species sorting can dominate functional island biogeography

If community-weighted traits are measured at one time point, species replacement
can look like functional adaptation of an island community even when the
within-species component is weak or unstable.

For mobile consumers, island functional differentiation may therefore reflect
**who breeds there** more strongly than persistent phenotypic divergence of the
residents.

### D5. Temporal replication changes the ecological conclusion

A single breeding season would have suggested stronger site differentiation.
Repeated seasons reveal that much of the within-species signal is not persistent.

This is the broader ecological sampling-design lesson, not an ODSP methods claim.

## Figure plan

### Figure 1 — Where the island phenotype comes from

Panel A: Palmer breeding sites and species represented.

Panel B: assemblage-scale decomposition: morphology → pooled; species → pooled;
morphology beyond species.

Panel C: conceptual split between species sorting and within-species phenotype.

### Figure 2 — Island trait contrasts are reassembled among years

For bill length, bill depth and flipper length:

- equal-sex island means by year;
- connect the three island means within each year;
- emphasize pairwise rank reversals rather than p-values.

Body mass and isotopes move to Supplement.

### Figure 3 — Spatial phenotype within a year, temporal failure across years

For structural morphology:

- three same-year LOO balanced accuracies;
- three leave-one-year-out balanced accuracies;
- chance line = 1/3;
- mean within-year 0.448 versus cross-year 0.342.

Secondary inset: isotope 0.360 versus 0.340.

## Table 1 — Hierarchical evidence

Columns:

- ecological level;
- question;
- metric;
- observed result;
- interpretation.

Rows:

1. assemblage / species sorting;
2. fixed within-Adélie island effect;
3. island × year reassembly;
4. same-year spatial discrimination;
5. cross-year temporal persistence.

## What is not part of this paper

- long-term LTER colony-network concentration;
- Paper 2 Antarctic-wide demographic filtering;
- causal snow or geomorphology tests;
- individual repeated-measure plasticity;
- local adaptation genetics;
- ODSP methodological novelty.

Those remain separate mina/ODSP products.

## Submission-scale claim

A defensible abstract conclusion is:

> Functional differences among neighboring Palmer penguin breeding sites are
> dominated by species composition. Within Adélie penguins, structural morphology
> contains modest island information within individual breeding seasons, but
> island contrasts repeatedly reverse and cross-year prediction falls to chance.
> Island functional differentiation in this system is therefore better described
> as species sorting plus temporal reassembly than as a persistent within-species
> island phenotype.
