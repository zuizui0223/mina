# Polynya manuscript — current state, 22 November 2026

## v0.7.4 current state (22 November 2026)

The hypothesis fixed before between-colony calculation has been tested and **failed**: original 85-colony site-mean B1 = −1.295‰/10pp (CV3 eight-region 95% [−4.965,+2.376]); the existing within-colony M_P remains −1.003‰/10pp (CV3 [−1.675,−0.331]). A positive spatial-vs-annual sign inversion is **not identified**; dropping Wilkes Land changes the sign of B1. Same-source R1000 and observation-year-sensitivity slopes remain negative but uncertain. [Numerical result](RESULT_BETWEEN_WITHIN_POLYNYA_NO_GO_20261122_JA.md), [pre-result frozen decision](FROZEN_SCALE_BETWEEN_WITHIN_COLONY_TEST_20261122_JA.md) and [CI SUCCESS](https://github.com/zuizui0223/mina/actions/runs/45011139260). The negative test was added to manuscript §3.5 and Supplement S4. No fifth/new figure or further radius/lag tests.

Current review Word: main 23 pages / 1,720,183 bytes; supplement 10 pages / 50,651 bytes; unchanged five figures. No submission, public DOI, merge or new third-party licence. Author-only scientific review and declarations remain the next indispensable input. The earlier v0.7.3 text below remains historical.

## One active objective

Single polynya-centred **v0.7.3 author-review manuscript** in Draft PR #214. Its fixed 439-colony-season data and v0.7.1 CV3 uncertainty results remain unchanged. Current work concerns reviewer-proof interpretation and manuscript readiness—not more favourable ecological model searches.

## Completed in this revision

1. **Measured the support of the effect-size unit from the real frozen 439 rows.** Raw winter coastal-polynya SD was 6.3115 percentage points (pp); after colony and region-by-season effects and frozen M0 covariates, conditional exposure SD was 1.6011pp (1.6273pp on the 425 informative records). The unchanged M_P slope −1.0031‰/10pp corresponds to −0.1606‰ per one conditional residual SD. M_SP is −0.1463‰ per conditional residual SD of 1.5879pp. This is a descriptive algebraic change of unit, not a new p value, environmental intervention, or mechanism.
2. **Implemented a separate source-locked audit**: `audit_polynya_estimand_scale_20261122.py` with a concise `source_inputs/polynya_estimand_scale_audit_20261122.json`. It checks the original source archive hashes, reconstructs the exact 860→439 join, reabsorbs the frozen fixed effects using independent QR/Frisch–Waugh–Lovell algebra, and verifies unchanged M_P/M_SP coefficients. [GitHub Actions #45009422843 succeeded](https://github.com/zuizui0223/mina/actions/runs/45009422843).
3. **Revised the main Methods/Results and Supplement S2**, retaining all five main figures, point estimates, CV3 intervals, negative prediction result, exploratory provenance and measurement limitations. Added the bounded [reviewer note](SCIENTIFIC_REVIEW_ESTIMAND_SCALE_V073_JA.md).
4. **Regenerated MEPS review files**. The main DOCX is 22 pages, 1,719,285 bytes and 4,803 visible document words. The supplement is 8 pages, 48,972 bytes, with the new source-locked table. Figure packet 5 pages, alternate text 2 pages, cover letter 1 page and author sheet 2 pages; six Word deliverables total 40 pages. The [current build receipt](document_build_receipt.json) and [declared visual QA](document_visual_qa_v073.json) record the method and checks. Modified pages were viewed at full size; all 30 current main/supplement pages were reviewed in contact sheets.

## Scientific status and stop rules

- The pre-analysis positive direction was not supported: the retained negative association is exploratory. Its M_P CV3 95% interval is [−1.675,−0.331]‰ per 10pp; the direct preceding–following winter difference is −0.688 [−1.470,+0.095] and uncertain.
- Identifying support is 425 records, 82 sites and eight unequal regions within the original 439-record, 85-site, 11-nominal-region sample. Victoria Land supplies 55.0% of M_P residual-exposure SS.
- Optical δ¹⁵N remains a proxy rather than a direct seasonal diet measure. Prey fractions, isotope baselines and optical mixing are not separately identified. Same-winter ice extent was not fixed. No out-of-sample predictive improvement or independent biology validation was obtained.
- Stop searching new radius, lag, threshold, favourable period, or null models on the same data to improve the already selected negative result. Retain all existing negative and no-go checks. The observed 1.6pp residual scale must accompany discussion of the 10pp slope.

## Awaiting author-only decisions

Scientific author review and facts for name/order, affiliations, contributions, funding, conflicts, ethics/data reuse, prior submission, AI disclosure, code/data rights and release scope are in `submission_preparation/AUTHOR_INFORMATION.md`. **Do not submit, assign a blanket new licence, publish a DOI, or merge PR #214 without author direction.**

Earlier v0.7.1 and v0.7.2 work is preserved in Git history. The nest-weighted v0.6 and frozen physical datasets remain historical/supplementary, not another active paper.
