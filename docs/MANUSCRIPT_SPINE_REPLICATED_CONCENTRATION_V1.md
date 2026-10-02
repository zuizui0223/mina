# Manuscript spine v1 — replicated breeding-space concentration

## Working title

**Population decline repeatedly concentrates breeding effort within Adélie penguin colonies**

Alternative, more spatial:
**Adélie penguin decline is accompanied by replicated contraction of breeding-space organization**

## One-sentence claim

Long-term Adélie penguin population decline is not well described as proportional thinning across established breeding components: in three Palmer islands and an independently tested Signy Island series, breeders become disproportionately concentrated into a smaller effective set of colony units.

## Biological question

When a colonial breeder declines, does the breeding distribution simply become thinner while retaining its relative spatial composition, or does the population reorganize so that reproduction becomes concentrated among fewer established breeding components?

This is a population-ecology question about the spatial form of decline, not a prediction-method question and not an attempt to identify a single climate driver.

## Why this is not the existing fragmentation story

Existing Adélie work shows that declining abundance can generate fine-scale fragmentation of nest aggregations and higher edge exposure, and that snow/terrain can structure persistence of individual subcolonies. The present paper asks a different hierarchical question: whether breeding effort across established colony/subcolony units remains proportionally distributed as total abundance falls.

The two processes can coexist. A shrinking population may lose whole historical breeding components at a coarse scale while the nests remaining inside occupied components fragment at a finer scale. Torgersen provides direct spatial evidence for this hierarchy: many historical subcolony footprints have disappeared, while some retained footprints contain smaller fragments.

## Study architecture

### Discovery system — Palmer Station, West Antarctic Peninsula

Use the complete 1991–2017 Palmer LTER Adélie census.

Primary concentration inference is restricted to the three islands with unchanged colony-code rosters:

- Cormorant
- Humble
- Litchfield

For each island-year, define effective colony number

N_eff = 1 / sum(p_j^2),

where p_j is the share of breeding pairs in colony-code component j.

Observed changes:

- Cormorant: 3.54 -> 2.86 (-19.1%), slope -0.0310 yr^-1
- Humble: 4.62 -> 2.28 (-50.6%), slope -0.0855 yr^-1
- Litchfield: 5.78 -> 1.00 by the final positive census (-82.7%), slope -0.3681 yr^-1

The frozen null holds the observed island-total trajectory exactly in expectation while imposing a time-invariant cumulative colony composition. Poisson, Gamma-Poisson CV10%, and Gamma-Poisson CV20% count-error families test whether falling total abundance plus independent counting noise is sufficient to reproduce the concentration slope.

All three islands remain more negative than expected under the full frozen error family; the three-island joint probability is approximately 1e-5.

### Independent replication — Signy Island, South Orkney Islands

The independent endpoint was frozen before any Signy N_eff series or slope was computed.

A first execution stopped before endpoint calculation because the official source has no 2010 breeding-pair season. The availability repair changed only the end year from 2010 to 2009, before any N_eff value, slope, or null distribution had been seen.

Primary fixed-roster epoch: 1998–2009, 12 seasons, eight literal published colony units.

Observed:

- total breeding pairs: 2688 -> 901
- N_eff: 3.610 -> 2.539
- fractional N_eff change: -29.7%
- N_eff slope: -0.11148 yr^-1

Frozen fixed-composition null:

- Poisson: p = 0.000010
- Gamma-Poisson CV10%: p = 0.000010
- Gamma-Poisson CV20%: p = 0.000130

The Palmer phenomenon therefore replicates in an independent monitoring system under the same ecological statistic and null logic.

### Physical spatial triangulation — Torgersen Island

Independent map/drone/GIS reconstruction documents contraction from 23 historical active subcolony footprints to five active footprints by 2022 and non-random persistence with respect to long-term snow/terrain conditions.

This evidence is used at phenomenon level only. Census colony codes are not claimed to map one-to-one to GIS polygons.

## Central inference

The replicated result rejects a simple ecological picture in which population decline acts only by proportionally removing breeders from an otherwise fixed breeding distribution.

Instead, decline has a reproducible internal spatial-demographic form: relative breeding effort becomes increasingly concentrated among a smaller effective set of established breeding components.

This is termed **breeding-space concentration** or **coarse-scale breeding-space contraction**.

## What the paper does NOT claim

- N_eff decline causes population decline.
- The pattern is an early-warning indicator.
- Individual penguins move from failing to successful subcolonies.
- Public information, prospecting, win-stay/lose-switch, or breeding dispersal has been demonstrated.
- Small colonies disappear earlier because of an Allee effect; the frozen Palmer zero-boundary audit shows that small-first zero hitting is mechanically expected under proportional thinning.
- One habitat mechanism explains both Palmer and Signy.
- Coarse-scale concentration rules out fine-scale fragmentation. They are different spatial levels.

## Relation to existing Adélie spatial theory

McDowall & Lynch (2019) predicts that declining abundance can fragment nest aggregations even in homogeneous habitat, potentially generating edge-related positive feedbacks. Schmidt et al. (2021) shows that emergent subcolony geometry and local habitat can structure reproductive success. Cimino et al. (2025) documents selective loss of historical Torgersen subcolonies under long-term snow and terrain differences.

The gap filled here is longitudinal and distributional: whether decline across established breeding components is proportional, or instead produces a systematic redistribution/concentration of breeding effort, and whether that phenomenon transfers to a second long-term Adélie system.

## Results order

### R1. Palmer decline has a non-proportional internal spatial form
Show annual abundance and N_eff for COR, HUM, LIT. Report fixed-composition error-null inference.

### R2. The same concentration independently appears at Signy
Show 1998–2009 Signy total abundance and N_eff. Report the three frozen null probabilities.

### R3. The replicated census signal corresponds to real breeding-space loss at Torgersen
Summarize historical-footprint loss and habitat-structured persistence without attempting a colony-code crosswalk.

### R4. Scale resolves an apparent conflict with fragmentation theory
Use published evidence, not a new response search: whole historical breeding components disappear at coarse scale even though retained components may fragment internally at finer scale.

## Figure plan

### Figure 1 — Two-system study design
Map Palmer and Signy, with nested schematic: island/site -> established breeding components -> nests.

### Figure 2 — Palmer discovery
For COR, HUM, LIT: total breeding pairs and annual N_eff through time, plus observed N_eff slopes against frozen null distributions.

### Figure 3 — Signy replication
Top: total breeding pairs and N_eff, 1998–2009.
Bottom: observed N_eff slope against Poisson, CV10%, CV20% null distributions.

### Figure 4 — Cross-system synthesis
Effect summary for four independent population units (COR, HUM, LIT, Signy): start-to-end fractional N_eff change, with Torgersen mapped-footprint attrition as independent physical triangulation.

No Paper 2 A x H panel, phenotype panel, or lag-2 performance panel belongs in the main paper.

## Discussion spine

1. **Decline has geometry.** Counting fewer animals is not equivalent to knowing how breeding space is lost.
2. **The geometry replicates.** Signy makes concentration a two-system ecological result rather than a Palmer-specific curiosity.
3. **Scale matters.** Coarse-scale loss of breeding components can coexist with fine-scale fragmentation inside retained components.
4. **Mechanisms remain plural.** Snow/terrain, nest-site fidelity, density dependence, predation geometry, breeding participation and movement can all contribute; the present data identify the demographic spatial outcome, not a unique cause.
5. **Why it matters.** A colony with the same total number of breeders can occupy breeding space very differently. Monitoring only total abundance can therefore miss a second dimension of population contraction: loss of the effective number of breeding components.

## Material to remove from the main manuscript

Move out of this paper's main narrative:

- Antarctic-wide static area x habitat-complex analysis
- radius sign-switch diagnostics
- Palmer phenotype reassembly
- performance-memory and lag-2 redistribution
- win-stay/lose-switch tests
- N_eff next-year-growth prediction
- beta hierarchy as a headline result

They remain provenance or future/separate-paper material. Bringing them into this manuscript would recreate the branching-exploration problem that the independent Signy concentration replication now solves.

## Inferential status

Palmer concentration was developed during exploration but has a stringent frozen count-error null family and three-island replication. Signy concentration is a separately frozen endpoint in an external dataset; its availability-only window repair occurred before any Signy N_eff outcome was computed.

The manuscript should describe this as **discovery followed by prospective external endpoint replication**, not as a fully preregistered study from inception.

## Stop rule

Do not search additional concentration metrics, thresholds, windows, lags, or mechanisms for this manuscript.

The only remaining analyses allowed for the main paper are:
1. figure/data packaging of already frozen Palmer and Signy results;
2. descriptive harmonization needed to put the four population units on the same plotted scale;
3. literature positioning and manuscript writing;
4. reproducibility/audit checks that do not create a new ecological endpoint.
