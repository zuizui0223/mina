# Frozen post-result four-region growth alignment diagnostic (2026-11-21)

**Scope:** PR #214 only. The positive original parent23 and matched17 between-region sea-ice reweighting components were already known before writing this contract. This is not a preregistered causal inference or a population significance test.

## One non-algebraic question

Is the assignment of four observed regional growth ratios to the four reporting regions unusually aligned with the pre-existing geographic differences in mean sea-ice exposure, rather than simply producing a positive between-region accounting component?

Inputs: original matched_support.csv, comparison=long and radius=0; use fixed 23 original Adélie sites with original 1993–2000 and 2011–2020 median recorded nests, and the 17-site complete-GLORYS subset. Preserve original observed 0-to-0 PLEN; no imputation. The 23 and 17 are overlapping supports, not independent samples.

## One frozen exhaustive algorithm

For each of the two cohorts separately, calculate regional baseline total N_r0, observed late total N_r1, growth ratio G_r=N_r1/N_r0, and original within-region late site shares v_ir1=n_i1/N_r1. Preserve early site counts, original physical sea-ice series, source region labels and the observed within-region late shares.

Enumerate the exact 4! = 24 permutations of the **four entire regional growth ratios** in alphabetical reporting-region order, without random draws or seed. For permutation pi, set synthetic late site values n_i1^pi=N_r0 * G_pi(r) * v_ir1; normalize all early and late counts into cross-region colony shares, then calculate symmetric Kitagawa reweighting R and its exact between/within region components B and W with the same original formulas. The identity R=B+W must hold to 1e-10 in all 24 assignments. The identity assignment must numerically reproduce the known parent23 and matched17 observed R/B/W to 1e-9.

Predeclared primary summaries: how many of 24 assignments have B>0; number of assignments with B>=actual B (including identity); exact minimum/median/maximum and 2.5/97.5 quantiles of B. Secondary: W and R distributions. Additionally save the same median-centered absolute-rank tail for B. These are **enumeration frequencies/ranks**, NOT inferential p-values.

Decision rule: only if the observed B ranks within the highest two of 24 assignments is the conditional observed geographic alignment unusual enough to note descriptively; otherwise explicitly do not claim preferential climate sorting from it. Even a top-two rank cannot prove an adaptive or causal mechanism: regional growth ratios cannot in general be exchanged due to unmeasured habitat and census differences; n region = 4, non-synchronous source medians, and the observation is post-selected.

Do not optimize physical window, site roster, regional units or tail direction after viewing the result. Do not modify main, v0.5, existing manuscript figures, or other papers.
