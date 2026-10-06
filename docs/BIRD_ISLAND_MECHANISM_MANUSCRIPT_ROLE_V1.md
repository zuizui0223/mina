# Bird Island mechanism result — manuscript role v1

**Status:** interpretation guide after the frozen Bird success-to-allocation test. Does not supersede the preferred manuscript spine v0.8.

## Statistical result

Frozen Bird Island mechanism contract:

    local operational success_t
      -> next-year log breeding-share change.

Primary two-way fixed-effect result:

    beta = +0.3238
    9999 year-vector permutations
    p = 0.0001.

A +1 SD difference in the two-way-demeaned success index corresponds to:

    +0.1447 log share-change

or approximately:

    1.156x

the next-year relative share multiplier.

All six leave-one-unit-out coefficients remain positive.

This is strong **prospective predictive information**.

## Why it is not a clean causal mechanism result

### Shared denominator

Primary predictor:

    chicks_t / nests_t

and primary response:

    log(p_t+1/p_t)

both contain current nests.

Thus current count error or transient nest-count depression can contribute positive coupling.

### Operational success index

Nine eligible unit-year rows have chicks/nest > 2.

Maximum:

    Upper Mountain Cwm 2019
    23 nests
    181 chicks
    ratio 7.87.

The provider dataset is explicitly a monitoring breeding-success dataset, but at split sub-colony/year resolution the ratio cannot always be interpreted literally as biological fledglings per original breeding pair.

Phenology/count timing and chick spatial redistribution can contribute.

### Rebound geometry

After unit/year demeaning:

    success vs current log share
    r = -0.640.

Success_t versus previous share change:

    beta = -0.314.

Primary forward beta:

    +0.324.

This near-symmetric backward/forward pattern is consistent with:

    local share trough
      -> high operational success / low-density state
      -> next-year rebound.

That can be real compensatory ecology, mechanical denominator coupling, or both.

## Why the signal is not dismissed as a simple artifact

Post-result diagnostics, not replacements for the primary test:

### Current-share control

    beta_success = +0.286
    permutation p = 0.0001.

### Ratio-free chick-output diagnostic

Use:

    log(1+chicks_t)

with:

    log(nests_t)

as an explicit covariate.

Result:

    beta = +0.0833
    permutation p = 0.0126.

### Provider timing colonies only

Johnson + Square Pond:

    beta = +0.252
    permutation p = 0.0082.

### Remove every year containing any chicks/nest > 2

32 years remain:

    beta = +0.405
    permutation p = 0.0001.

Therefore the association is broader than the extreme-ratio rows, although all these diagnostics are post-effect.

## Allowed manuscript sentence

Use in Results/SI:

> In Bird Island Gentoo penguins, a preregistered local breeding-performance index strongly predicted next-season relative breeding share (beta=0.324, year-vector permutation p=0.0001), but the index shared the current nest-count denominator with the response and was strongly associated with low current share; we therefore treat this as prospective allocation information rather than a causal reproductive-success effect.

Optional Discussion follow-up:

> Ratio-free and current-share-adjusted diagnostics retained a positive signal, consistent with compensatory local dynamics, but an independent denominator-safer replication is required.

## Do not write

- successful sites attract breeders;
- birds use a win-stay/lose-switch rule;
- high reproductive success causes redistribution;
- juvenile recruitment explains a one-year lag;
- Bird establishes the Ross mechanism.

## Independent discriminating test

A pre-effect Port Lockroy Gentoo contract now uses:

    late chick output_t
    + current breeder abundance_t
    -> next-year breeding share

without a chicks/nests predictor ratio.

Port Lockroy is the appropriate test of whether the Bird signal transfers under a denominator-safer design.

Its outcome cannot change the main Ross/Bird/Emperor allocation paper.
