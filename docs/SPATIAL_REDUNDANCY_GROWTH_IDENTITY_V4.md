# Spatial redundancy growth identity v4 — zero-safe vector form

**Status:** current mathematical synthesis. Supersedes v3 for finite-interval calculations when zero local abundance is possible. The identities are algebraic and are not claimed as new mathematics.

## State variable

For local abundances n_i:

    N = sum_i n_i
    p_i = n_i / N
    E = 1 / sum_i p_i^2.

Equivalently:

    E = N^2 / sum_i n_i^2.

This vector form is valid when some local abundances equal zero.

## Instantaneous form

For positive-abundance nodes with local log-change rates r_i:

    r_bar = sum_i p_i r_i
    r_D = sum_i [p_i^2 / sum_j p_j^2] r_i

and:

    d log(E)/dt = 2(r_bar - r_D).

This describes the instantaneous direction of abundance-weighted spatial redundancy.

## Finite zero-safe identity

For two endpoint abundance vectors n_0 and n_1 define:

    G_bar = N1 / N0

and:

    G_D* = sqrt(
        sum_i n_i1^2
        /
        sum_i n_i0^2
    ).

Then exactly:

    E1/E0 = (G_bar / G_D*)^2.

No local ratio n_i1/n_i0 is required.

Therefore the identity remains defined if:
- a zero-baseline node becomes positive;
- a positive node becomes zero.

## Relation to the earlier local-multiplier form

If every n_i0 > 0, define:

    G_i = n_i1/n_i0
    H0 = sum_i p_i0^2
    w_i0 = p_i0^2/H0.

Then:

    G_D*^2
      = sum_i w_i0 G_i^2.

So the starting-dominance-weighted RMS multiplier is a special case of the zero-safe vector norm.

## Interpretation

The decomposition separates:

### Common scalar mode

    G_bar = N1/N0

which describes change in total abundance.

### L2 / concentration mode

    G_D*

which describes change in the Euclidean magnitude of the local-abundance vector.

Their ratio determines E.

This is another way to state the common-versus-compositional distinction:

> restoring the scalar total does not require restoring the local-abundance vector.

## Exact composition restoration

Composition is restored iff:

    p_i1 = p_i0

for every i.

Equivalently, one scalar c must exist such that:

    n_i1 = c n_i0

for every i.

If a node is zero at baseline and positive later, exact composition restoration is impossible.

## Emperor penguin example

The prospective 50-colony emperor-penguin endpoint contains:

    Ledda Bay N_median 2009 = 0
    Ledda Bay N_median 2018 > 0.

Its individual G_i is therefore undefined.

No pseudo-count and no colony exclusion are required.

All 50 colonies give:

    G_bar = 0.876216
    G_D*  = 0.938166
    E2018/E2009 = 0.872296

and:

    (G_bar/G_D*)^2 = 0.872296.

Thus the full-roster spatial decomposition remains exact.

## Ross examples

Ross colony/component counts are positive at the focal anchors, so either finite form may be used there.

The zero-safe vector expression is now preferred in shared code because it also handles establishment/zero-index cases without changing rosters.

## Biological boundary

A zero count or zero posterior median is not automatically:
- colonisation;
- extinction;
- true absence.

The identity describes the frozen abundance vector only.

Biological interpretation of zeros requires separate observation and search-history evidence.
