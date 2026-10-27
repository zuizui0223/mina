# V45 diagnostic contract — 2-epoch counting asymmetry in V44 nesting-guild contrast

2026-10-27 | **POST-RESULT DIAGNOSTIC**. Original V44 (11 Scottish Country×Master network pairs; 3 large gulls vs Black-legged Kittiwake; D=-0.10001721634243599) is already known. This checks whether its direction may arise from measurement-count asymmetry. It is not prospective confirmation and cannot retroactively rescue the failed V44 predator prediction.

## Design invariants
- Do not modify original first-party JNCC comparable revised workbook SHA256 9edf05b8af0a44c3ca770f390120c4b99bcaae3ae35fd844a82982d6ad8116d4, existing 17-species nest-accessibility source trait coding, ≥3 child original Site.ID panels, same original count unit, ≤1 year matched survey windows, within-5-km centroid, or both-guild-declining criterion from V44.
- Reconstruct exactly **11** Scottish Master networks / **17** eligible original pairs and require original V44 T from direct independent helper recomputation to reproduce -0.10001721634243599 within 1e-10. If any invariant fails, STOP. No Stanbury/RSPB predator probability map, GBIF source, or Antarctic bird outcome.
- Each Master gets one difference D_g between equal-species-mean accessible E and cliff E. Every eligible parent has original counts N0,N1>=2; site count k, first and later survey-year metadata retained for sanity check. Unique parent panels, not every child as an independent observation.

## Counting-theory diagnostic (mathematical, not fitted empirical field error)
- Observed Simpson share concentration C_t = sum_i (n_ti/N_t)^2.
- Original V44 E_late = C1 - [C0 + (1-C0)/N1] is centered only if baseline vector p0 treated as error-free.
- If both original and recent counts are independent multinomial snapshots with fixed latent p, Q=sum_i p_i^2, exactly:
  E[E_late] = - (1-Q)(1-1/N1)/N0.
  Therefore E_late is negatively biased under that *sampling model*, especially for small baseline N0. This formula is a model check, NOT a claim real Seabird 2000 adjusted census counts are independent random samples.
- Exactly unbiased within that two-epoch independent multinomial model: U_t = sum_i n_ti(n_ti-1)/[N_t(N_t-1)] = (N_t C_t - 1)/(N_t-1), and E_both = U1-U0. It has zero expected value for a constant true source-site composition even with different N0,N1. This can be noisy at N1 very small and does not correct undetected nest groups / non-random source survey effort.
- Freeze primary V45 diagnostic: equal-network mean D_both = mean_g (mean_accessible E_both - mean_cliff E_both) on **exactly V44 11**. Compute paired sign difference positive networks, median and 5/95% network quantiles. Report V44 original D unchanged alongside to avoid endpoint switching.
- Freeze *parametric* two-epoch null with 3,999 replicates, seed 20261027: for each exact original species parent separately set pooled null site probabilities p_pool=(n0+n1)/(N0+N1), draw independent multinomial (N0,p_pool) AND (N1,p_pool). Preserve species parents' N0,N1 and original site roster k. For each simulation compute both E_late and E_both, and the same within-Master signed D. Do not use original n0 as ground truth under this diagnostic. Report null 5th/50th/95th percentiles and both tails for E_late and E_both; do not call them real observation-error-calibrated p-values.
- Freeze exact **analytical expected bias** of original E_late under p_pool: - (1-sum(p_pool^2))*(1-1/N1)/N0 for each eligible original panel, aggregate with the same Master/guild weights. Report observed original D vs pooled-null analytical bias T and residual difference, with caveat p_pool fitted from observed counts (double use).
- Freeze sample-support counts, **without screening original result sign**: tally source panels by guild with N0<10, N1<10 and N1/k<3; median N0, N1, k, N1/k, original C0 by guild. As purely descriptive checks, show V44 matched networks where ALL eligible guild panels have (a) N0>=20 and N1>=20; (b) N1/k>=3; (c) N1/k>=10. Preserve each network denominator and do not use a reduced subset as new primary analysis or claim significance with <10 source Masters.
- Freeze leave-one-Master-out D_both range and sign stability. Do not reassign taxon guilds/years/count units/localities or introduce weights to force sign.
- Code test: under synthetic fixed p with independent N0,N1, E_late approximate mean negative bias, E_both approximate mean ~0, and exact original V44 matched fixture counts remain unchanged; no raw animal data included in Git commit.

## Decision

If V45 correction moves original negative D toward zero or changes sign, call V44 negative **not robust to the two-epoch sampling model**. If it stays negative, say **negative association persists under specified hypothetical multinomial observation process** but do not infer predation because real effort, physical colony sites and true observer error are unmeasured. Neither outcome changes original V44 **positive predator-accessibility prediction NOT SUPPORTED**, nor V36 physical-island predator effect **NOT IDENTIFIED**. No new line of biodiversity database downloads.
