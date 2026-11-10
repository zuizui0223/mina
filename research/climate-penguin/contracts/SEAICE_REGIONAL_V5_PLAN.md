# Fixed44 regional versus within-region sea-ice identification plan

2026-10-29. Continuation of exposed V4 effects, not preregistered or independent confirmation. The user authorized execution. No alteration of original44 response, 100km masks, calendar lag, source labels or predictor months; no p-value search. Existing216-test correction and frozen Paper1/PR199 untouched.

Question: does the previously negative prior marine-ice association reflect shared regional/year variability, or comparisons among local sites in the same original region/year?

Implementation: pure NumPy nested orthogonal projections: site; site+year; site+region×year. Component sea-ice sums of squares and sea-ice×response products must exactly add to the site-adjusted totals. Fractions describe predictor information in this unbalanced sample, not the fraction of ecological change causally explained. Region fixed effects alone cannot answer the question (already absorbed by site); site×year would saturate the whole sample. The chosen region×year diagnostic changes the estimand and can remove true regional climate effects as well as confounding.

Source: run40881769676 original96 monthly fields; SHA-pinned original44 pair table,34272 pixel rows and V4 numeric JSON. Fixed original 2 regional labels,7 site IDs. Regional marine union summaries deduplicate exact original cells within each region and verify identical month-to-month cell support; no nearest substitute or missing-to-zero operation. These are fixed7-site unions, not all the ocean in the named regions.

Steps: test-first synthetic projection/duplication/missing/rank guards; implement and replay source44; independently recalculate via full dummy QR and original96 HDF5 files; save code/tests/result/decision in PR206 and confirm CI output matches local. Delete-one-site/year diagnostics preserve unestimable fits. Same40 exact-land sample is kept separate from full44; show which land deletions remove all remaining predictor information rather than just extrema among successful fits.

Local evidence:8 tests initially failed for absent behavior and subsequently passed;110 coefficients or rank-exhausted refits independently checked, maximum difference1.16e-13;192 monthly regional means reconstructed directly from96 original files, maximum error0. Full repository tests and remote replay are checked separately. Companion session ZIP includes source inputs, tests, complete result and independent verification code. Original raw96 files remain in original V4 artifact.
