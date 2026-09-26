# Long-term island reassembly — frozen analysis rules

## Primary question

Does long-term functional change on Palmer Archipelago breeding islands occur
mainly through **species replacement and abundance turnover**?

For island (i), year (t), and species (s):

[
p_{sit}=N_{sit}/\sum_s N_{sit}
]

and for a fixed species trait centroid (ar z_s):

[
CWM_{it}=\sum_s p_{sit}\bar z_s.
]

The first long-term analysis deliberately holds species trait centroids fixed.
It asks how much the **community phenotype** changes through who is present and
abundant. It does not reconstruct unobserved historical within-species
morphology.

## Source and count harmonization

Use APBP/MAPPPD observations for Adélie, chinstrap and gentoo penguins at sites
whose names contain Biscoe, Dream or Torgersen.

Primary rules are coded in `mina.longterm`:

1. nests / breeding-pair observations only;
2. numeric repeated counts at one site/species/year -> median;
3. positive presence-only records remain missing;
4. an explicit nest `presence=0` record may be converted to count zero;
5. an island-year missing any focal species observation is excluded;
6. no interpolation;
7. transitions are primary-eligible only when contributing site coverage is
   identical in the two years.

The strict species-completeness rule can make the primary panel small. That is a
diagnostic, not a reason to silently fill zeros. If APBP metadata permit a
stronger survey-effort rule later, it must be added as a new contract version.

## Functional summaries

For each retained island-year:

- relative abundance of the three Pygoscelis species;
- community-weighted bill length;
- community-weighted bill depth;
- community-weighted flipper length;
- community-weighted body mass (reported separately because condition-sensitive);
- effective species diversity (e^H).

For adjacent observed years:

- relative-abundance turnover (0.5\sum_s |p_{s,t+1}-p_{s,t}|);
- change in each CWM;
- replacement contribution
  (sum_s (p_{s,t+1}-p_{s,t})\bar z_s);
- a numerical identity check between total CWM change and the replacement
  component;
- site-coverage stability flag.

## Hypotheses

**L1 — directional functional reassembly.** Islands with sustained shifts from
Adélie toward gentoo or chinstrap abundance should move toward the replacing
species' trait centroid.

**L2 — assembly before trait evolution.** Large changes in community trait
centroids should be explainable from species-abundance turnover without
inventing within-species historical trait change.

**L3 — asynchronous islands.** Neighboring islands need not move in parallel;
colonization history and breeding-habitat filters can generate different
trajectories under shared regional forcing.

**L4 — regional forcing, local realization.** Sea ice is a later mechanism
layer. Island-specific snow/geomorphology/phenology may explain deviations among
islands, but only after the abundance panel and outcome rules are frozen.

## Falsification

The island-reassembly story is weakened if focal islands show little
composition change; if functional centroids remain nearly flat despite large
composition shifts because species trait centroids overlap; if transitions are
carried by changing site coverage; or if the result is driven by one poorly
sampled island.
