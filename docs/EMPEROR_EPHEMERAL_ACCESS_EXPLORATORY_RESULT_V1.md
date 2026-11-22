# Exploratory emperor other-open-water proxy — completed, not a confirmation (2026-11-22)

**Status:** exploratory proxy was specified *after* seeing the frozen primary null; empirical output complete and association NOT supported.

Execution: https://github.com/zuizui0223/mina/actions/runs/45021723416

## Why this analysis was chosen
Labrousse et al. (2019, GRL, https://doi.org/10.1029/2019GL084347) found that tracked emperor penguins used ephemeral openings in/along fast ice. Lin et al.'s (2024, https://doi.org/10.1038/s41597-024-03848-2) tuned `SIC60_6.25km_20d` coastal-polynya ID filter rejects open-water sequences that last <20 d or never exceed 100 km2. Its other-open-water category `Map == -1` may include transient small openings, but it also includes other non-polynya waters/noise and misses narrow leads/cracks at 6.25 km.

## Frozen *post-hoc* proxy definition
- Outcome: LaRue modeled emperor spring abundance/attendance index, log1p, same 50 colonies.
- Exposure: log1p(mean daily nominal km2 of `Map == -1` within great-circle 50 km), April–August 2009–2018, excluding 2012 due missing months. **Exactly one post-hoc main exposure** tested.
- Design: colony+year FE, 8 regional clusters, sign flips over 256 sign combinations; secondary colony+region×year FE.
- Joined dataset N=450; 50 colonies, 9 eligible years.
- New proxy had 50-km mean 43.05 km2, median 32.17 km2, 4.2% zero, and Pearson correlation about −0.05 with 50-km persistent coastal-polynya mean area. Descriptive `any-open-water within 50 km` occurred on median 54.3% of observed days; it was not fitted as a second hypothesis.

## Result
| Design | Standardized beta (log1p response) | Region t 95% CI | Region clustered p | 256-sign-flip p |
|:--|--:|:--|--:|--:|
| Colony+year FE | −0.03158034 | [−0.20054946, +0.13738878] | 0.67186 | 0.6640625 |
| Colony+region×year FE | −0.01339999 | [−0.15344815, +0.12664817] | 0.82747 | 0.8203125 |

The signed cluster coefficient changed under leave-one-region-out, and a positive prediction is not supported. No predictive or causal ecological claim follows from this proxy result.

## Link to the frozen main result
The original persistent coastal-polynya 100 km association was recomputed in the same Actions run **unchanged**: beta +0.018271683215944738, p-signflip 0.6640625, 450 colony-years. The initial official analysis is at https://github.com/zuizui0223/mina/actions/runs/45018808042 and the immutable original claim is in `docs/EMPEROR_POLYNYA_PRIMARY_SCREENING_RESULTS_V1.md`.

## Decision and data limitation
**Stop** adding neighboring radii, lags, thresholds and flexible seasons to this same outcome: it would turn a failed primary test into a specification search. A proper distinct experiment needs independent performance outcomes (e.g. chick survival/breeding success) and genuinely fine-grained fast-ice-edge / leads / accessibility maps, plus full LaRue posterior uncertainty and an independent sea-ice-concentration baseline.

No existing Adélie δ15N manuscript or active submission is modified.
