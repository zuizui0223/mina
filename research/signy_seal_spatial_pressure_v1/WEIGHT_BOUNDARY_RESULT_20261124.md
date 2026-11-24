# Signy three-species weighting boundaries — exact conditional reaggregation

Date: 2026-11-24. Status: CONDITIONAL_WEIGHT_BOUNDARY_NOT_ECOLOGICAL_EFFECT. This is a deterministic sensitivity calculation on the same 216-cell panel (12 years × six zones × three taxa) in Actions run 45387988565, artifact 14917157831; not a new biological observation, preregistered test, fitted function or confidence interval. ZIP SHA256 9e0a8b1684221c5874d8e23d7307d051d6fecddf0c8dfc91f0207fc1c162f781 checked locally; CRC and exact coverage verified. Early 2010, 2012–14; late 2016–20, 2022–24. No added years. Same weights across periods and zones; nonnegative, fur normalized to 1. Counts are February census observations, including adjacent sea ice, not animal-days or observed ecological effects.

Let d_F, d_E, d_W be late-minus-early equal-year mean counts and P = N_F + r_E N_E + r_W N_W. Delta P = d_F + r_E d_E + r_W d_W. The equal-other-weight break-even is -d_F/(d_E+d_W) when the denominator is positive. For independently varying 0 <= r_E,r_W <= R the maximum delta P is d_F + R[max(d_E,0)+max(d_W,0)]. Its zero determines the largest threshold below which every allowed pair implies a decline. We take the minimum threshold across the full panel and 12 leave-one-year-out variants. This is deterministic robustness to deletions, not a statistical CI.

| Unit | d_F | d_E | d_W | Equal other weights break-even | Independent box full threshold | Box threshold robust to single-year omission |
|---|---:|---:|---:|---:|---:|---:|
| Island | -8668.875 | 88.25 | 4.25 | 93.717568 | 93.717568 | 32.589623 |
| 1 | -3784.875 | 14.625 | 0.125 | 256.601695 | 256.601695 | 54.824786 |
| 2 | -611.375 | -81.875 | 0.375 | no positive solution | 1630.333333 | 1168.333333 |
| 3 | -1952.25 | 118.125 | 1.25 | 16.353927 | 16.353927 | 9.876817 |
| 4 | -865 | 18.625 | 2.75 | 40.467836 | 40.467836 | 22.853462 |
| 5 | -692.5 | 8.5 | -0.5 | 86.5625 | 81.470588 | 23.928 |
| 6 | -762.875 | 10.25 | 0.25 | 72.654762 | 72.654762 | 17.211409 |

Island equal-other-weight break-even ranges 32.5896–991.5 across deletions. With r_W fixed at an illustrative 5, island E break-even is 97.9901 (32.9534–1809.7597 across deletions); zone 3 E break-even 16.4741 (9.9237–25.1855). Thus for any 25.18552 < r_E < 32.95336 with r_W=5, zone 3 increases while island total decreases in the full and every deletion panel. Strict inequalities shown rounded conservatively in prose; use exact source code for boundary. Example r_E=30, r_W=5: island -15.9672% (deletion range -23.4904 to -2.3101%); zone 3 +16.6380% (+4.7485 to +38.8580%). This example illustrates the derived feasible region, not a plausible-weight calibration or a result chosen as a test.

| r_E | r_W | Island change % | Island LOO range % | Zone 3 change % | Zone 3 LOO range % |
|---:|---:|---:|---|---:|---|
| 1 | 1 | -56.481 | -63.233 to -50.987 | -46.191 | -57.877 to -39.589 |
| 5 | 5 | -44.852 | -51.822 to -40.091 | -28.516 | -40.224 to -18.450 |
| 10 | 5 | -35.053 | -42.210 to -28.742 | -13.363 | -25.132 to +0.241 |
| 20 | 5 | -23.046 | -30.433 to -12.473 | +5.435 | -6.409 to +24.179 |
| 30 | 5 | -15.967 | -23.490 to -2.310 | +16.638 | +4.749 to +38.858 |
| 50 | 10 | -7.945 | -15.620 to +9.724 | +29.394 | +17.471 to +55.951 |
| 100 | 10 | +0.217 | -8.579 to +22.676 | +42.566 | +29.805 to +74.070 |

Interpretation: numerical losses are geographically widespread but possible functional compensation is heterogeneous conditional on fixed species weights. Island-level census decline alone cannot identify local ecological pressure. No positive estimate of pressure, biomass, trampling, nutrient transfer, competition, plant response or causal replacement. No independent replication and weights may change across years, sexes, ages, activities and habitat. Negative and positive mechanisms (e.g., trampling versus nutrient addition) require separate estimands; cannot infer a net plant outcome from a nonnegative weighted sum.

Source context: Australian Antarctic Program species profiles (https://www.antarctica.gov.au/about-antarctica/animals/seals/antarctic-fur-seals/ ; https://www.antarctica.gov.au/about-antarctica/animals/seals/elephant-seal/ ; https://www.antarctica.gov.au/about-antarctica/animals/seals/weddell-seal/) document substantial species and sex differences in mass. They do not establish the weight distribution at Signy or impact per counted animal. Dunn et al. 2025 DOI 10.1111/gcb.70290 documents summer fur seals mainly juvenile/adult males and censuses during moult periods. BAS annual source DOI 10.5285/8e910ac8-6f52-4548-bbcb-78474b559294 and Signy daily monitoring portal document counts, not calibrated impacts; the local daily source remains unavailable. Laws' historic observations and later moult literature emphasize season and age/sex-dependent haul-out, not a transferable contemporary duration ratio. Body mass cannot be directly substituted for ecological impact. Obtain actual species-specific terrestrial animal-days and mechanism-specific effects before any calibration. No further reopening of closed vegetation, tracking or spectral classification gates.

Reproduce locally from the original ZIP, without repackaging:
```sh
python research/signy_seal_spatial_pressure_v1/weight_boundary.py artifact.zip result.json
```
The script was executed in the current session, exact rational arithmetic and additivity/zero identity checked. Local code SHA256 d7ca275fdadee186a5e0fc704de638db194e579463911332363373ac742b4f60, output SHA256 6c9127b4ec3e6756195a947579da2cbbc08ec1875a0f0755263ee27438514d5b. PR219 draft only, existing results and manuscripts unchanged. No data request submitted.
