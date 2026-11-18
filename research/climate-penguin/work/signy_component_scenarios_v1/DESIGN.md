# Signy diet-component scenarios

2026-11-06. Exploratory, conditional scenario extension of the known Signy association. This design is written before calculating the new future p/c/m outcomes. It is not a preregistration or a new independent ecological sample.

## Goal and approach

Translate the existing sea-ice conditions into observed meal components: p, the fraction of valid stomachs with recorded positive fish wet mass; c, the equal-stomach fish fraction conditional on positive mass; and m, the equal-stomach fish fraction across all valid stomachs. Use the existing nine gentoo seasons and 73 stomachs without changing their denominator or QC.

The primary approach retains equal-season OLS and the previously fixed additive climate deltas. A fractional-logit fit of each of the same three responses is a bounded response-shape sensitivity, with point contrasts only. A new mechanistic or population model is outside this extension: the existing data do not identify its parameters. These implementation choices are the assistant's choices under the user's instruction to continue autonomously.

## Fixed inputs and climate conditions

- `INPUT_MANIFEST.json` pins the 16 existing input files before new scenario outcomes are computed.
- Reconstruct GOPT/loc020 from the nine tracked CMIP6 monthly files. Use four complete, unique August–November months, equal month weights, then equal weights over each 20-year period.
- Observed baseline: GOPT 0–100 km SIC, 1995–2014, 48.68273700076806%. For each climate model/member and SSP, target = observed baseline + model future mean − model historical mean. Retain all three available models and all 12 conditions. Do not form a probability ensemble, exclude BCC after looking at its delta, or silently clip corrected SIC.
- The primary scenario is evaluated at each **future mean SIC**. Annual corrected climate values are retained only for support diagnostics: a supported mean can contain unsupported years. Do not call the evaluated response a mean of future annual diets.
- Observe the original diet support, 21.90128214834321–66.68284803598858% SIC. Keep the climate row but leave all future diet values and contrasts NA outside this range, including bounded-link results. Within-range interpolation is not dense local validation.

## Response and uncertainty calculations

- Fit intercept plus SIC/10 separately for p, c and m, using nine equal-weight seasons and no stomach-count weights. Reproduce the existing OLS slopes and HC3 t7 slope intervals.
- Reference diet values are regression evaluations at the 1995–2014 observed climate mean, not observed diet means for that period.
- A contrast uses slope × delta SIC/10. The coefficient-only 95% interval multiplies both HC3 slope limits by the fixed delta and reorders them. Do not add this interval to the reference point and label it an interval for a future absolute level.
- Fractional-logit uses the same rows, equal weights, an intercept and SIC/10, with p=1 retained. Do not transform observed responses with an arbitrary epsilon, calculate new significance tests, select the best model, or add another forecast-validation gate.
- Although m_y = p_y c_y in each observed season, separate fitted marginal responses generally satisfy fitted(m) != fitted(p) × fitted(c). Predict m from its own model. Preserve this distinction explicitly.
- Translate the existing mean-centred frequency, composition and covariation term slopes to the same fixed climate deltas and check that their contrast sum is the m contrast. This is algebraic allocation of the single-species mean, not causal contributions or decomposition of the original three-species distance.
- Show controlled SIC reductions of 5, 10 and 20 pp; include 30 pp only as a withheld outside-support case. Preserve coefficient uncertainty, model differences, temporal dependence, and relation-invariance assumptions as distinct limits.

## Deliverables and completion

Create portable analysis, independent climate and numerical checks, complete model-specific CSVs, a four-panel figure, a Japanese report and validation record. Integrate one concise additional scenario section and supplement into the existing diet manuscript and positive-evidence ledgers. Retain the three-species result and Palmer transfer findings. Publish the verified changes to the existing Draft PR #206; do not merge or modify main or frozen papers.

## Implementation plan

1. Test temporal aggregation, support, contrast interval signs, and the non-product prediction distinction before implementation.
2. Reconstruct climate inputs, fit the fixed responses, export 12 × 3 scenario rows and source hashes; independently compare inputs and outcomes.
3. Render and inspect the figure; integrate the results into report, manuscript and evidence ledgers.
4. Run the focused tests, existing manuscript verification and the repository suite once; document the three previously reproduced baseline failures separately. Commit, publish with an expected-head check, and confirm the remote tree equals the verified local tree.
