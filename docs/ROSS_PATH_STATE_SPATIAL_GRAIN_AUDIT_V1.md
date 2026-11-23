# Ross path-versus-state spatial-grain audit v1

**Date:** 2026-10-07  
**Status:** post-result descriptive robustness.  
**Result:** \`results/ROSS_PATH_STATE_SPATIAL_GRAIN_AUDIT_V1.json\`

## Question

Does the focal path-versus-state result depend on using six census components rather than three colony-level units?

The six-component representation is:

- Cape Royds;
- Cape Bird South / Middle / North;
- Cape Crozier West / East.

The three-colony representation aggregates these to:

- Cape Royds;
- Cape Bird;
- Cape Crozier.

## Results

| Quantity | 6 components | 3 colonies |
|---|---:|---:|
| Aggregate loss restored | 96.97% | 96.97% |
| Loss/rebound cosine | 0.99695 | 0.99672 |
| Inverse-path fidelity | 90.59% | 93.27% |
| Baseline→trough TV | 5.09% | 4.93% |
| Baseline→rebound TV | 4.97% | 3.54% |
| Baseline displacement erased | 2.4% | 28.3% |
| Exact-inverse endpoint TV from baseline | 0.0717% | 0.0695% |

At the three-colony scale, local restoration was:

- Royds: 38.7%;
- Bird: 68.3%;
- Crozier: 105.2%.

Thus differential recovery persists after aggregation.

## Interpretation

The **magnitude** of state restoration depends on spatial grain.

The six-component result should not be presented as if 2.4% were a scale-invariant property of the population.

However, the qualitative result is robust:

> **aggregate recovery and path reversal were high at both grains, while observed endpoint composition remained much farther from baseline than the exact inverse-path counterfactual.**

At both grains, exact proportional reversal at the observed aggregate rebound would have returned composition almost exactly to baseline (~0.07% TV). The observed endpoint remained 4.97% away at six-component scale and 3.54% away at three-colony scale.

Therefore:

> **coarsening hides some spatial reorganization but does not remove the path-versus-state discrepancy.**

## Consequence for manuscript

Prefer:
- raw baseline→trough and baseline→rebound distances;
- both six-component and three-colony sensitivity;
- “incomplete state restoration” rather than a universal single percentage.

Treat the 2.4% six-component restoration score as the primary fine-grain description, not a scale-free recovery index.

## Stop rule

Do not search additional arbitrary aggregation schemes.

The biologically natural six-component census and three-colony aggregation are sufficient to establish the spatial-grain boundary.
