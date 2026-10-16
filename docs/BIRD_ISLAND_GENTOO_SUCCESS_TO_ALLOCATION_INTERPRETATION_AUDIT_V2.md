# Bird Island Gentoo success-to-allocation interpretation audit v2

**Status:** post-result interpretation audit. The frozen primary statistic remains unchanged; this document narrows what that PASS is allowed to mean.

## Frozen primary result

The pre-effect test reported:

    beta = +0.32383
    permutation p = 0.0001
    fully standardized beta = 0.579.

This remains the correct result for the exact frozen statistic:

    predictor = chicks_t / nests_t
    response  = log(p_i,t+1 / p_it).

## Why the primary PASS is not a clean confirmatory mechanism test

### 1. Shared current denominator

The predictor contains:

    1 / nests_it.

The response contains:

    -log(p_it),

and therefore includes:

    -log(nests_it)

after the annual common component is removed.

A transiently small or underestimated current nest count can therefore mechanically:

- inflate chicks/nests;
- inflate the following share-change response.

The frozen year-vector permutation breaks that same-year denominator alignment in the null, so a very small permutation p does not by itself establish prospective biological information.

### 2. Operational success is not literal local fecundity

Nine eligible unit-years have:

    chicks / nests > 2.

Maximum:

    Upper Mountain Cwm, 2019
    181 chicks / 23 nests
    = 7.87.

BAS metadata calls the dataset breeding success and uses standardized nest and later chick counts, but row comments explicitly document delayed nesting and additional nests after the initial standardized count in some years.

Therefore the local ratio is best treated as an **operational breeding-performance/phenology index**, not a literal fledglings-per-pair quantity in every sub-colony-year.

## Direct mechanical diagnostics

After the same unit/year fixed-effect removal:

    corr(success index, -log current nests) ~= +0.640

and:

    corr(next-year share change, -log current nests) ~= +0.433.

A denominator-only negative-control index constructed as:

    annual mean chick count / current local nests

still produces a standardized association with next-year share change of approximately:

    0.472.

This shows that the current nest denominator alone can generate a large positive forward association.

A time-reversed diagnostic is also nearly symmetric:

    current success index vs previous share change
    beta ~= -0.314.

Equivalently, using next-year success against the current share transition gives a comparably large negative association.

This geometry is not what should be expected from a simple one-directional "higher reproductive success causes next-year share gain" mechanism.

## Evidence that the signal may not be entirely mechanical

Post-result denominator-safer diagnostics remain positive.

### Ratio-free count model

Model:

    log nests_i,t+1

against:

    log nests_it
    + log(1 + chicks_it)
    + unit FE
    + year FE.

The chick term is:

    beta = +0.0833
    standardized beta ~= +0.153
    year-vector permutation p = 0.0126.

This asks whether chick count adds next-year local-abundance information beyond current nest count without constructing chicks/nests.

### Timing-colony sensitivity

Using Johnson and Square Pond, which define the laying chronology:

    beta > 0
    permutation p = 0.0082

under the original ratio formulation.

### Extreme-ratio sensitivity

Removing years containing any local chicks/nests >2 does not reduce the primary coefficient.

Therefore the primary PASS is not simply driven by a few extreme rows.

## Confirmatory versus suggestive status

### Confirmatory

Only this is confirmatory under the frozen contract:

> the exact predeclared chicks/nests statistic is strongly positively associated with the exact predeclared next-year share-change statistic.

### Not confirmatory

Do not claim from that primary result alone:

- reproductive success causally drives next-year allocation;
- local reproductive performance contains independent prospective information beyond current abundance;
- win-stay/lose-switch behavior;
- movement.

### Suggestive post-result evidence

The ratio-free diagnostic suggests:

> local chick output may contain a smaller prospective signal beyond current nest abundance.

But this was diagnosed after the primary effect was opened.

It therefore remains **suggestive**, not an independently confirmed mechanism.

## Independent replication attempt

A denominator-safer Port Lockroy Gentoo mechanism route was frozen before outcome opening.

It failed at the support gate because the required late/crèche chick endpoint is not available at fixed sub-colony resolution.

The earlier hatch-chick field is not substituted.

Thus there is currently **no independent prospective ratio-free confirmation** of the Bird mechanism signal.

## Paper consequence

The mechanism status is:

    state/allocation result = strong
    predictor of contrast mode = unresolved.

Bird success belongs in a short Discussion/inset as a qualified lead, not as a major Results pillar.

The next mechanism paper should use a dataset in which:

- local current abundance;
- local reproductive output;
- next-year abundance/share

are measured independently enough to avoid shared denominators, and the endpoint is frozen before values are opened.
