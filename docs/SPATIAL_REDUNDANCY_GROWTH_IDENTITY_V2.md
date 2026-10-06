# Spatial redundancy growth identity v2 — path-aware interpretation

**Status:** superseded by `SPATIAL_REDUNDANCY_GROWTH_IDENTITY_V3.md`. The algebra is unchanged; V3 replaces the single 2001-2012 Ross example with the biologically resolved shock/rebound/later-recovery sequence.

## 1. State variable

For local breeding units i,

    N = sum_i n_i
    p_i = n_i / N
    H = sum_i p_i^2
    E = 1 / H.

E is an abundance-weighted effective number of breeding units.

## 2. Instantaneous identity

Let

    r_i = d log(n_i) / dt
    r_bar = sum_i p_i r_i
    w_i = p_i^2 / H
    r_D = sum_i w_i r_i.

Then exactly:

    d log(E) / dt = 2 (r_bar - r_D).

At an instant:

- E falls iff currently dominant units, in the p_i^2-weighted sense, grow faster than the population average;
- E rises iff they grow more slowly.

This is a **local-in-time** statement.

## 3. Finite-interval identity

Over an interval define:

    G_i = n_i1 / n_i0
    G_bar = sum_i p_i0 G_i = N1/N0
    w_i0 = p_i0^2 / H0
    G_D = sqrt(sum_i w_i0 G_i^2).

Then exactly:

    E1/E0 = (G_bar/G_D)^2.

Thus:

- E1 < E0 iff G_D > G_bar;
- E1 > E0 iff G_D < G_bar.

This is an endpoint identity.

## 4. Important correction

The endpoint condition **does not imply** that the unit dominant at time 0 remained dominant or had the largest growth factor.

Because G_D is a weighted RMS, a formerly small unit can grow so strongly that its squared multiplication term dominates the endpoint arithmetic.

Therefore V1's sentence

> "Spatial redundancy declines whenever demographic change is preferentially amplified in already dominant breeding units"

was too narrow as a general finite-interval interpretation.

That description is correct for Ross recovery, but not for every route to E decline.

## 5. Two distinct recovery-concentration routes

### A. Persistent-dominance amplification

A node that is already dominant grows faster than the rest and remains dominant.

Ross Island recovery:

    Crozier share 70.8% -> 77.6%
    N 3.70x
    E3 ratio 0.8925.

All three colonies grew, but Crozier remained dominant and gained share.

### B. Dominance-reversal amplification

A subordinate node grows so rapidly that it first approaches equality and then overshoots to become the new dominant node.

Heard Island Spit Bay:

    1963: North 13, South 5
    1969: North 49, South 37
    1980: North 82, South 400
    1988: North 215, South 3,100.

Both colonies grew at every observed interval.

E:

    1963 1.670
    1965 1.471
    1969 1.962
    1980 1.393
    1988 1.138.

The system became more even and then re-concentrated around a **different** node.

## 6. Recovery can be non-monotonic in spatial redundancy

Heard establishes an important geometric point:

    N can rise monotonically
    while
    E rises and falls non-monotonically.

Therefore "spatial recovery" cannot be assumed to be a monotonic function of numerical recovery.

An endpoint comparison can miss a transient maximum in spatial redundancy.

## 7. Three descriptors are needed

Two axes are insufficient to reconstruct recovery history.

At minimum report:

1. total abundance N;
2. spatial redundancy E;
3. compositional identity / dominance turnover.

Ross:

    N up
    E down
    dominant identity retained.

Heard:

    N up
    E down at long endpoint
    dominant identity reversed.

Beaufort:

    N up
    E slightly up
    established main colony remains dominant, but small/new unit gains share.

## 8. Relation to decline

The same instantaneous identity still unifies decline and recovery.

- Differential attrition: total N down, dominant units lose less, E down.
- Persistent amplification: total N up, dominant units grow faster, E down.
- Equalizing recovery: total N up, subordinate units catch up, E up.
- Dominance reversal: continued unequal recovery can carry the system through maximum E and back to E down under a new dominant node.

Thus concentration is not a demographic mechanism. It is a spatial state that can be reached through multiple demographic paths.

## 9. What is invariant and what is historical

Invariant:

    the exact algebra linking abundance shares and local growth.

Historical/path dependent:

- which node is dominant;
- whether dominance changes identity;
- whether E passes through a maximum;
- which vital rates or capacity changes produce local growth differences.

## 10. Implication for the paper

The strongest general statement is now:

> numerical recovery and spatial redundancy are distinct, and even continuous growth at every local breeding unit can produce non-monotonic spatial reorganization, including concentration around either the original or a newly dominant node.

The Ross result remains the frozen focal result.

Heard is an external post-result triangulation showing that recovery concentration without local decline is not restricted to Adélie penguins or to persistence of the original dominant node.
