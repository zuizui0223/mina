# Matched-species macro growth implementation plan

Goal: execute the approved continuation beyond Palmer using source-matched positive annual abundance changes, without claiming unsupported climate effects.
Architecture: stdlib source retrieval with pinned SHA values -> unique species-site-season records -> within-source adjacent pairs -> same-site/year/source/method species pairs -> site-balanced descriptive summaries. Preserve raw source, rows, and uncertainty limitations.
Spec: research/climate-penguin/contracts/MAPPPD_MATCHED_SPECIES_GROWTH_V1.md

Task 1: source and matched-pair code with synthetic tests. Tests must reject duplicate IDs/groups, mismatched citations/vantages, nonadjacent years, missing calendar precision and nonpositive endpoints. Numerical test recovers log(1.5) from ADPE 100->80 and GEPE 50->60; unequal monitoring effort does not alter equal-site weighting. Local red phase: 8 expected missing-implementation failures. Local green phase: 8 passed and syntax compilation passed.
Task 2: execute exact original source download and contrast on GitHub Actions; save original bytes, hashes, CSVs and JSON. Stop on source changes; never rewrite the frozen source to fit expected outcomes.
Task 3: inspect actual biological estimates, regional scope and site influence; persist concise result with original run/commit IDs; verify core repository tests. New code must not rerun unrelated acquisition workflows by modifying their triggers.

Review focus: biological presence is not abundance; source sites are not physical islands; shared references are not identical visits; positive-only conditioning excludes colonization/extinction; leave-site ranges are not confidence intervals. Primary result may be null, negative or geographically restricted. No post-result threshold rescue or inferential claims.
