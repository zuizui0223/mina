# Paper 2 result spine v1 — dynamic terrestrial opportunity does not generally redirect Antarctic Pygoscelis breeding use

**Date:** 2026-10-04  
**Status:** first real dynamic outcome closed; predeclared marine modifier stopped at measurement support.  
**Paper 1 remains unchanged.**

## Central question

> **When Antarctic breeding land becomes more available, do penguins shift breeding use toward those sites?**

The paper treats terrestrial breeding opportunity as a dynamic state rather than a static island attribute.

For each frozen physical breeding site, the Landsat pipeline measures:

[
Delta A_{available}
]

as change in the persistent summer-exposed fraction of an independently mapped ice-free support.

The demographic response is not raw abundance. It is the change in a site's breeding use **relative to contemporaneous conspecific sites in the same regional monitoring context**.

## Why this question matters

Local and palaeoecological studies show that deglaciation can release terrestrial breeding-space limitation.

- Beaufort Island: retreating ice increased nesting habitat, colony abundance increased, and emigration changed (LaRue et al. 2013).
- East Antarctic / Holocene evidence: penguin expansion has repeatedly followed deglaciation and emergence of ice-free ground.

Those results establish that terrestrial capacity can matter.

They do not establish that contemporary breeding redistribution across Antarctica generally tracks decadal change in terrestrial opportunity.

Paper 2 is the broad change-to-change test of that generalization.

---

# Measurement result: the breeding landscape is physically moving

The frozen summer-exposure metric passed its external Beaufort positive-direction control and then ran across the full frozen local-pixel roster.

## Full terrestrial measurement

- 77 physical sites.
- 57 positive changes.
- 16 negative changes.
- 4 zero changes.
- Median (Delta A_{available}=+0.03046).

Regional pattern:

- Central-west Antarctic Peninsula: 24 positive, 5 negative, 4 zero; median +0.0302.
- South Shetland Islands: **16/16 positive**; median +0.2750.
- Victoria Land: 13 positive, 11 negative; median +0.00462.
- Southwest Antarctic Peninsula: 2/2 positive.
- Elephant Island: 1/1 positive.
- Northeast Antarctic Peninsula: 1/1 positive.

For the outcome-blind Adélie subset:

- 37 sites;
- 25 positive, 12 negative under p50;
- 28/37 p50–p67 sign agreement;
- p50–p67 correlation (r=0.832);
- robust same-direction classification: 22 increase, 6 decrease, 9 threshold-sensitive.

Therefore there is ample spatial and regional variation in changing terrestrial opportunity. The ecological test is not defeated by a nearly constant predictor.

Boundary: this metric is **persistent summer exposure within fixed current AEI support**, not literal newly deglaciated nestable rock.

---

# H1: terrestrial opportunity tracking

## Frozen model

85 site × species units in six supported species × regional networks:

- Adélie: 30 units;
- chinstrap: 31;
- gentoo: 24.

The model removes:

- site fixed effects;
- species-specific region × season states.

The focal coefficient asks whether a +1 SD difference in terrestrial-opportunity change rate produces a different relative breeding-use trajectory per decade.

Inference used 9,999 within-species × region exposure permutations and Holm correction across the three species.

## Result

### Adélie

[
eta_A=+0.0713
]

- one-sided permutation p = 0.0624;
- Holm p = 0.1872;
- precision-weighted beta = +0.0776.

The direction is compatible with opportunity tracking, but it is not confirmatory.

The frozen p67 measurement sensitivity weakens the result:

- beta = +0.0350;
- p = 0.1683;
- Holm p = 0.5049.

### Chinstrap

[
eta_A=-0.0258
]

- p = 0.5627;
- Holm p = 0.869.

### Gentoo

[
eta_A=+0.00853
]

- p = 0.4345;
- Holm p = 0.869.

Across species:

- 2/3 coefficients positive;
- median beta = +0.00853;
- no species passes the frozen multiplicity criterion.

## H1 conclusion

> **Changing terrestrial opportunity is not sufficient to explain contemporary relative redistribution of breeding use across Antarctic Pygoscelis at the tested spatial and temporal scale.**

Do not write:

- “deglaciation has no effect on penguins”;
- “land does not matter”;
- “Adélie tracks habitat” based on p = 0.0624.

The correct contrast with prior work is scale and generality:

> **Release of terrestrial breeding-space limitation is real in particular systems and over long postglacial histories, but it does not emerge as a transferable rule for decadal redistribution across the present multi-site comparison.**

---

# H2: land–sea coupling

A single marine modifier was frozen before H1 outcome:

- November–January;
- NOAA/NSIDC Sea Ice Index v4;
- 25 km grid;
- distance to nearest grid-cell center with sea-ice concentration <15%;
- early–late median distance change;
- positive favorable change = open water becomes closer.

## Measurement support result

The public archive itself was broadly available, but the **actual distance metric** failed the frozen continuation gate.

Across the 77 terrestrial sites:

- 58 pass both epoch measurement requirements;
- passing fraction = 75.3%;
- frozen requirement = 80%.

Regional passing counts:

- Central-west Antarctic Peninsula: 33;
- South Shetland Islands: 16;
- Victoria Land: only 5;
- other regions: 4 combined.

Median favorable marine change among passing sites = 0 km.

Therefore:

> **H2 is closed without an ecological interaction test.**

This is a support failure, not evidence against marine control.

No threshold, month set, search radius or alternative ocean covariate is opened as a rescue.

---

# Direct occupied-footprint route

The preferred strongest spatial formulation would compare:

[
Delta A_{available}
quad 	ext{with} quad
Delta A_{occupied}.
]

That route remains methodologically unresolved.

What succeeded:

- independent published Adélie guano reference overlaps 22/44 long-term sites at 5 km;
- published Landsat-7 ETM+ classifier transition matrix and rule were recovered;
- 45/47 published source scenes were directly crosswalked to Collection-2;
- diagnostic evidence identifies one major unmatched scene as a crosswalk implementation issue rather than a missing historical scene.

What failed/closed:

- same-sensor ETM+ longitudinal route: 0/44 sites have the frozen 2016–2021 late ETM+ support because post-2013 Antarctic Landsat-7 acquisition is not systematic;
- direct ETM+ classifier application to OLI is not authorized without a validated spectral bridge.

Thus the current paper must call the response **relative breeding use**, not occupied breeding footprint.

---

# Ecological contribution

The result changes the interpretation of Antarctic “island area.”

A static island formulation assumes:

[
P=f(A,I).
]

Paper 2 shows that even when the terrestrial opportunity term itself changes through time,

[
Delta A_{available}
]

does not by itself determine which breeding nodes gain relative use.

The important distinction is therefore:

1. **physical opportunity** — land becomes exposed/available;
2. **realized breeding use** — penguins redistribute among sites;
3. **population abundance** — total breeders change.

These state variables need not move together.

This is particularly useful in Antarctica because land availability is changing rapidly and independently from the marine matrix that sustains central-place foragers.

## One-sentence conclusion

> **Across a multi-site Antarctic Pygoscelis comparison, terrestrial breeding opportunity changed substantially but did not provide a confirmed general rule for where breeding use increased, showing that dynamic physical island capacity and biological redistribution are separable processes.**

## Stronger but still defensible alternative

> **Deglaciation can release local nesting constraints, but expanding breeding opportunity is not sufficient to organize contemporary penguin redistribution across Antarctic breeding-site networks.**

---

# Relationship to Paper 1

Paper 1:

> Declining populations repeatedly concentrate breeding into fewer effective components beyond proportional thinning.

Paper 2:

> Changing terrestrial capacity does not generally tell us which breeding sites will gain or lose relative use.

Together:

> **The spatial form of decline is more reproducible than a simple terrestrial explanation for where that spatial change occurs.**

This is the bridge from penguin breeding ecology to island ecology.

---

# What remains unresolved

- individual dispersal and recruitment;
- direct occupied-footprint change;
- marine resource/access mechanisms;
- social/site-fidelity effects;
- whether mobile breeding substrates produce a different spatial response mode.

The last item is the natural transition to Paper 3.

## Stop rule

No same-data rescue via:

- alternate land thresholds;
- alternate regional grouping;
- raw abundance substitution;
- broad marine covariate screening;
- post-hoc species pooling.

Further mechanism requires independent measurements or a new system.
