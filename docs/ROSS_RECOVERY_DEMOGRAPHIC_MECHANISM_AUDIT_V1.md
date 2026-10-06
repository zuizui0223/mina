# Ross Island recovery mechanism audit v1

**Status:** post-result mechanism audit. This document does not convert any post-result mechanism into confirmatory evidence for the Ross V2 effect test.

## Observed recovery pattern to explain

Under the frozen Ross Island V2 roster, 2001 -> 2012 abundance multipliers were:

- Cape Crozier: 272,340 / 67,114 = **4.058x**
- Cape Bird: 75,696 / 26,317 = **2.876x**
- Cape Royds: 3,083 / 1,367 = **2.255x**

Thus the amplification rank is:

    Crozier > Bird > Royds

All three colonies increased, but Crozier gained enough extra share that E3 declined by 10.7%.

The mechanism question is therefore not why some colonies survived while others disappeared. It is why the same regional recovery was converted into different local multiplication rates.

## Independent individual-level demographic evidence

Dugger et al. (2026) analysed 25 years of mark-recapture data from the same three Ross Island colonies, 1996-2020.

Their main colony rankings are informative because they resolve demographic components that cannot be recovered from aerial census totals alone.

### Recruitment probability

Age-specific recruitment probabilities for birds remaining at their colony were:

    Crozier > Bird > Royds

at the ages analysed, with Crozier highest and Royds lowest.

This rank matches the census recovery multiplier exactly.

### Apparent survival

Pre-breeder apparent survival did **not** have the same rank. It was highest at Bird, with Crozier and Royds lower and similar.

Therefore simple survival advantage is not the cleanest explanation for Crozier's disproportionate census amplification.

### Breeding propensity

Breeding propensity among established breeders was highest at Crozier, intermediate at Royds, and lowest at Bird.

This partially supports a Crozier demographic advantage but does not reproduce the full census growth rank.

### Movement

Movement between colonies was highest for pre-breeders but very low for breeders (<0.20%). Recruitment involving movement to a new colony was also very low (<0.10%).

This makes large-scale redistribution of established breeders an implausible sole explanation for the 2001-2012 census concentration.

The most concordant individual-level signal is therefore **local recruitment**, with breeding propensity as a plausible secondary contributor.

## Independent nesting-quality evidence

A Ross Island subcolony study comparing Cape Crozier and Cape Royds reported:

- higher mean reproductive success at Crozier;
- lower temporal and spatial variation in reproductive success at Crozier;
- a higher proportion of edge nests and greater potential skua-predation penalty at the smaller Royds colony;
- strong effects of subcolony geometry and local nesting habitat on reproductive success.

This independently supports persistent local differences in demographic return among colonies.

It also argues against treating all hectares of nominally ice-free land as equivalent breeding capacity.

## Mechanistic interpretation: quality-weighted amplification

A minimal decomposition is:

    log n_i(t+1) - log n_i(t)
        = R_t + q_i + c_i(t) + epsilon_it

where:

- R_t = regional forcing shared among colonies;
- q_i = persistent local demographic advantage (recruitment, reproductive success, breeding propensity, foraging access);
- c_i(t) = time-varying capacity release or constraint;
- epsilon_it = residual annual variation.

If regional forcing is positive and q_i differs among already occupied colonies, every colony can grow while high-q colonies gain share.

That produces:

    N up
    all n_i up
    E down

without requiring adult aggregation or colony loss.

This is the Ross pattern.

## Contrast with Beaufort: capacity-opening recovery

Beaufort provides a different configuration.

There, glacial retreat increased usable nesting habitat and the new within-island subcolony gained approximately 3.15 times its proportional expected share of 2004-2010 growth, while independent band/resighting evidence indicated reduced export to Ross Island after local habitat became available.

This is consistent with a large positive c_i(t) on previously unavailable or newly usable breeding space.

That can produce:

    N up
    smaller/new unit gains share
    E up locally
    inter-island export down

The Ross and Beaufort cases therefore suggest two recovery modes rather than one universal rule.

## Generated recovery-mode hypothesis

### Mode A — quality-weighted amplification

When the roster of usable breeding nodes is stable and persistent demographic quality differs among nodes, recovery is allocated disproportionately to the highest-return nodes.

Prediction:

    regional N increases
    -> high-quality persistent nodes grow fastest
    -> effective number can decline

### Mode B — capacity-opening recovery

When environmental change creates substantial new usable breeding capacity away from the dominant node, recovery can be redirected toward smaller or new breeding units.

Prediction:

    regional N increases
    -> newly released capacity gains disproportionate share
    -> effective number can increase
    -> export beyond that capacity envelope can decline

## What is actually supported now

Supported as **mechanistic concordance**:

1. Ross recovery amplification rank is Crozier > Bird > Royds.
2. Independent age-specific local-recruitment rank is Crozier > Bird > Royds.
3. Adult movement is too rare to be an obvious sole driver.
4. Crozier has higher and more stable reproductive success than Royds in independent nesting studies.
5. Beaufort supplies a contrasting capacity-opening case.

Not supported yet:

- a causal mediation estimate from recruitment to colony growth;
- a universal two-mode recovery law;
- a threshold amount of spare habitat that switches modes;
- a claim that colony size itself causes recruitment;
- a claim that terrestrial habitat alone explains Crozier growth.

The mark-recapture record overlaps in time and geography with the census record, so this is an independent **data stream**, not an independent system.

## Next independent test

The next test must leave Ross Island.

A suitable pre-existing system is Southwell et al. (2015), which standardized historical and recent direct counts at 99 Adélie breeding sites in five East Antarctic regional populations. All five regional totals increased over roughly three decades, but local growth rates were strongly heterogeneous.

Before the site-level Supporting Information is inspected for concentration outcomes, a separate contract should freeze whether widespread recovery generally preserves, increases, or reduces spatial redundancy.
