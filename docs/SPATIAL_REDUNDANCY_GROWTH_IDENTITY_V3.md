# Spatial redundancy growth identity v3 — sign changes across disturbance and recovery

**Status:** post-result mathematical synthesis. The identities are algebraic and are not claimed as new mathematics.

## Identity

For breeding units i:

    N = sum_i n_i
    p_i = n_i/N
    E = 1/sum_i p_i^2.

With instantaneous local log-growth r_i:

    r_bar = sum_i p_i r_i
    w_i = p_i^2 / sum_j p_j^2
    r_D = sum_i w_i r_i

and exactly:

    d log(E)/dt = 2(r_bar - r_D).

Thus E can increase or decrease independently of the sign of total abundance change.

## Finite interval

Define local multiplication factors:

    G_i = n_i1/n_i0
    G_bar = N1/N0
    G_D = sqrt(sum_i w_i0 G_i^2).

Then:

    E1/E0 = (G_bar/G_D)^2.

## Ross: one system changes sign three times

### 1999 -> 2001 shock

Three-colony factors:

    Royds   0.378
    Bird    0.556
    Crozier 0.429

    G_bar = 0.4571
    G_D   = 0.4410

Because G_D < G_bar:

    E3 ratio = 1.0740
    E increases.

The dominant Crozier colony loses share relative to Bird.

### 2001 -> 2002 breeding rebound

Three-colony factors:

    Royds   1.638
    Bird    1.546
    Crozier 2.400

    G_bar = 2.1519
    G_D   = 2.3044

Because G_D > G_bar:

    E3 ratio = 0.8720
    E decreases.

The rebound is disproportionately allocated to Crozier.

### 2002 -> 2012 longer recovery

Three-colony factors:

    Royds   1.377
    Bird    1.861
    Crozier 1.691

    G_bar = 1.7212
    G_D   = 1.7013

Because G_D < G_bar:

    E3 ratio = 1.0235
    E increases modestly.

Bird grows fast enough to reduce Crozier's share slightly.

## Why the staged example matters

The same metapopulation can move through:

    N down / E up
    N up / E down
    N up / E up.

Therefore there is no universal sign linking numerical change to spatial redundancy.

The local allocation of change matters at each stage.

## Heard: endpoint identities still do not reconstruct path

Heard Island shows monotonic increases in total and local breeding counts while E rises and falls and dominant identity reverses.

Thus even the exact finite-interval identity should be evaluated over biologically meaningful intervals rather than treated as a causal summary of a long heterogeneous phase.

## Interpretation

The ecological estimand is:

> how local changes are allocated relative to the current abundance distribution.

It is not:
- total growth alone;
- occupancy alone;
- initial dominance alone.

## Measurement boundary

For Ross, n_i is breeding-territory / breeding-pair abundance from the aerial census.

The identity is exact for those observed counts.

It does not convert them into total-adult population growth or identify the vital rates producing the changes.
