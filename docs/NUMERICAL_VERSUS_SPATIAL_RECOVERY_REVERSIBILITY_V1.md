# Numerical rebound versus spatial reversal v1

**Status:** post-result mathematical synthesis. The identities are algebraic and are not claimed as new mathematics.

## Central distinction

Let breeding unit i have measured breeding abundance n_i.

Define:

    N = sum_i n_i
    p_i = n_i / N.

If local instantaneous change is:

    d n_i / dt = r_i n_i,

then:

    d log(N) / dt = r_bar

where:

    r_bar = sum_i p_i r_i.

But composition obeys:

    d log(p_i) / dt = r_i - r_bar.

Therefore aggregate breeding abundance and spatial composition are controlled by different modes of the same local demographic vector.

### Common mode

    r_bar

controls whether total breeding abundance rises or falls.

### Contrast mode

    r_i - r_bar

controls whether each breeding node gains or loses share.

A reversal in the common mode does not mathematically require a reversal in the contrast mode.

## Shared forcing cancels from composition

Suppose:

    r_i(t) = R(t) + q_i(t),

where R(t) is a shared regional forcing term and q_i(t) contains local differences.

Then:

    r_bar = R(t) + q_bar

but:

    d log(p_i)/dt = q_i - q_bar.

The shared forcing R(t) cancels exactly from compositional dynamics.

Thus a common environmental improvement can reverse aggregate decline while leaving the direction of spatial reallocation unchanged, altered, or non-monotonic.

This is the simplest mathematical reason why numerical recovery need not be spatial reversal.

## Finite-interval allocation

For an interval a -> b define:

    G_i = n_ib / n_ia
    G_bar = N_b / N_a.

Then exactly:

    p_ib / p_ia = G_i / G_bar.

So spatial composition is restored between a and b iff:

    G_i = G_bar

for every local unit i.

Equivalently:

    n_b = c * n_a

for one common scalar c.

If total abundance itself is restored, N_b=N_a, then c=1 and exact state restoration requires:

    n_ib = n_ia

for every i.

Restoring the sum does not restore the vector.

## Disturbance and rebound

Let:

    D_i = n_i1 / n_i0

be the disturbance multiplier and:

    R_i = n_i2 / n_i1

the rebound multiplier.

Then:

    Q_i = D_i R_i = n_i2 / n_i0.

Exact spatial-composition reversal requires all Q_i to be equal.

Exact abundance + composition reversal requires:

    Q_i = 1

for every i.

A rebound of total N alone only constrains the weighted mean of Q_i.

It does not constrain their equality.

## Ross Island natural experiment

Use the last complete pre-shock six-component season, the documented mega-iceberg trough, and the immediate rebound:

    1999 -> 2001 -> 2002.

### Aggregate abundance

    N1999 = 207,411
    N2001 = 94,798
    N2002 = 203,996.

Thus:

    N2001/N1999 = 0.457
    N2002/N1999 = 0.9835.

By 2002, total occupied breeding territories had returned to **98.35%** of the last complete pre-shock count.

### But spatial redundancy did not return

Three-colony E:

    1999 = 1.6095
    2001 = 1.7286
    2002 = 1.5074.

So:

    E3_2002 / E3_1999 = 0.9366.

Six-component E:

    1999 = 2.0558
    2001 = 2.2919
    2002 = 1.8190.

So:

    E6_2002 / E6_1999 = 0.8848.

The shock temporarily increased E; the rebound overshot toward a more concentrated configuration than before the shock.

### Local restoration factors, 2002 / 1999

Three biological colonies:

- Royds: 0.6185
- Bird: 0.8591
- Crozier: 1.0296

Six census components:

- Royds: 0.6185
- Bird South: 0.6547
- Bird Middle: 0.7072
- Bird North: 0.9484
- Crozier West: 1.0562
- Crozier East: 0.8124

Only Cape Crozier West exceeded its 1999 count among the six frozen components.

Its over-rebound, combined with its very large starting share, was sufficient for aggregate breeding abundance to return almost to the pre-shock total while most other components remained below their pre-shock counts.

## Composition mismatch after aggregate rebound

At the three-colony scale:

    TV(p1999, p2002) = 0.0354.

At the six-component scale:

    TV(p1999, p2002) = 0.0497.

These values are modest in absolute composition distance but biologically structured: the residual is concentrated toward the dominant Crozier component.

The stronger signal in E6 than E3 shows that the mismatch is amplified at finer breeding-component resolution.

## What Ross establishes

The clean statement is not:

> recovery reduces spatial redundancy.

It is:

> **aggregate breeding abundance can rebound to almost its pre-disturbance level without reversing the spatial redistribution generated through disturbance and rebound.**

This is a direct failure of scalar abundance to reconstruct spatial state.

## Prospective external counterexample: Bird Island Gentoo

The pre-effect Bird Island test fixed six breeding units before counts were opened.

1981 -> 2024:

    N: 3,331 -> 4,470 (+34.2%)
    E: 3.569 -> 4.128 (+15.7%).

So positive long-interval breeding-abundance change can end with **greater**, not lower, spatial redundancy.

The secondary temporal audit shows all four annual sign combinations:

    N up, E up: 12
    N up, E down: 9
    N down, E up: 8
    N down, E down: 13.

This independently demonstrates that the signs of aggregate and compositional change are not locked together.

## Relation to existing spatial recovery theory

Existing metapopulation recovery theory already shows that aggregate recovery can mask:

- patch extirpation;
- reduced occupancy;
- local nonrecovery;
- impaired production.

The added empirical axis here is the **allocation of abundance among still-occupied breeding nodes**.

Ross is especially informative because the immediate rebound increases every frozen local breeding count relative to the trough, yet nearly restored aggregate abundance still corresponds to a different spatial configuration than before the disturbance.

## Relation to recovery debt

Recovery-debt frameworks compare recovering abundance/diversity/function against a reference state over time.

The Ross result is compatible with that broad idea but makes the reference comparison explicitly compositional:

    N can be near-reference
    while p is off-reference.

Do not introduce a new named "spatial recovery debt" unless a broader prospective analysis validates such a metric.

## Relation to hysteresis

A loop in N–composition or N–E space is **hysteresis-compatible** but is not by itself proof of endogenous hysteresis.

Ross pre- and post-shock states differ in external environment as well as history.

Prior frozen-herd work provides a plausible endogenous mechanism, but the current census cannot distinguish environmental forcing from configuration memory.

Use:

> path dependence / failure of spatial reversal.

Reserve:

> causal hysteresis

for a future matched-environment, matched-abundance test with configuration history measured.

## General ecological proposition

> **Reversing aggregate population change requires a change in the common demographic mode; reversing spatial organization requires reversal of the relative local demographic modes. These are different conditions.**

This is why decline and rebound should not be assumed to be spatial inverses.
