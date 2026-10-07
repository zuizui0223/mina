# Ross path versus state recovery audit v1

**Date:** 2026-10-07  
**Status:** post-result descriptive reinterpretation.  
**Result:** `results/ROSS_PATH_VERSUS_STATE_RECOVERY_AUDIT_V1.json`

## Why this audit was necessary

The prior integrated framing treated the 1999→2001→2002 Ross episode as evidence that a severe breeding-abundance shock was followed by restoration of a previous spatial template.

That interpretation conflated two different questions:

1. **Path reversal:** did local gains occur where local losses had occurred?
2. **State restoration:** did the final relative allocation of breeders return toward the pre-disturbance state?

The existing inverse-path analysis answered the first question, not the second.

## Focal Ross episode

### Aggregate abundance

- 1999: 207,411 breeding pairs
- 2001: 94,798
- 2002: 203,996
- breeding-abundance loss: 54.3%
- aggregate loss restored by 2002: 96.97%

### Path reversal

The six-component loss and rebound vectors were strongly aligned:

- loss/rebound cosine = **0.99695**
- inverse-path mismatch = **9.41% of rebound**
- inverse-path fidelity = **90.59%**

Thus most absolute rebound abundance occurred in components that had contributed most absolute loss.

### State restoration

Using the total-variation distance between the six-component relative-abundance vectors:

- pre-shock 1999 → trough 2001: **5.089%**
- pre-shock 1999 → rebound 2002: **4.967%**

Therefore the rebound erased only

[
1-rac{0.049672}{0.050892}=0.02396,
]

or **2.4%**, of the compositional displacement measured at the trough.

The 2001→2002 composition shift itself was **9.753% TV**, the largest of the 25 complete adjacent transitions in the frozen Ross series (series median 3.219%; upper quartile 4.444%).

The effective-number summaries give the same warning:

- E3: 1.609 → 1.729 → 1.507
- E6: 2.056 → 2.292 → 1.819

Relative to the 1999 baseline, the E3 log-distance improved only 8.3%, while the E6 log-distance became 12.5% larger. The rebound crossed past the pre-shock state toward greater dominance.

Cape Crozier West illustrates the reweighting:

- 1999 share: 67.2%
- 2001 share: 62.4%
- 2002 share: 72.2%

It lost the most breeding pairs during the shock and gained the most during rebound, but it also overshot its pre-shock share.

## Calibration against other Ross down→up episodes

The same distinction appears in the other two complete six-component down→up episodes.

| Episode | Aggregate restoration | Inverse-path fidelity | Baseline→trough TV | Baseline→rebound TV | State-distance restored |
|---|---:|---:|---:|---:|---:|
| 1989→1990→1991 | 34.8% | 90.9% | 0.93% | 1.20% | −29.2% |
| 1999→2001→2002 | 97.0% | 90.6% | 5.09% | 4.97% | +2.4% |
| 2002→2003→2004 | 122.1% | 89.4% | 2.91% | 4.46% | −53.4% |

High inverse-path fidelity is therefore not equivalent to restoration of the starting composition in this series.

## Correct ecological interpretation

Withdraw:

> the old spatial state was largely restored / re-expressed.

Retain:

> **recovery occurred largely in the same breeding components that had lost abundance, but differential rebound reweighted the breeding network.**

The focal Ross natural experiment therefore shows:

> **path reversibility can coexist with state reorganization.**

In plain language:

> **the population recovered where it had declined, but not in the same proportions.**

This distinction is stronger and more precise than the prior spatial-memory interpretation.

## Consequence for the integrated manuscript

The manuscript should pivot away from latent spatial-memory restoration.

A better central question is:

> **When a spatially structured population recovers, does reversing local losses restore the previous spatial state?**

Ross answers **no** in the focal episode: aggregate recovery was nearly complete and the local rebound strongly retraced local losses, yet composition was not restored and the rebound produced the largest adjacent compositional shift in the series.

Palmer/Signy and Beaufort then provide biological contrasts for how local multipliers can reweight a breeding network during persistent decline or capacity release.

## Stop rule

Do not rescue the withdrawn state-restoration framing with alternative composition metrics.

TV and effective-number summaries already agree that state restoration is weak or absent.

Any future spatial-memory claim requires independent individual-level or latent-state evidence, not further re-expression of these aggregate counts.
