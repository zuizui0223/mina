# V10: Source-matched species composition at the nest and chick stages

2026-10-30 JST. Post-exploration follow-through of V9, not independent confirmation.

## Question and fixed scope
Do the species rankings in recorded nest numbers, recorded chicks per nest, and
recorded total chicks coincide at the same source site and breeding season?
Primary taxon contrast CHPE--GEPE follows V7--V9, not selected from new outcomes.
ADPE--CHPE and ADPE--GEPE are supplementary, reported separately, never pooled.
No new weather month, lag, count correction, recruitment lag or p-value is tried.

Rebuild V9's 274 source-stage pairs from all 5,487 original SHA-pinned MAPPPD5 rows.
Pair species only by identical site_id, season_start, citekey and vantage; keep
all four original record IDs. Duplicate same-stage data stay excluded as in V9.
If more than one source supplies a site-season-species contrast, retain it in the
source ledger but exclude that ambiguous site-season contrast from primary results.
Metadata-only inspection before the new outcomes: CHPE--GEPE 41 source pairs,
21 with both nest dates strictly before their respective chick dates, and 8 with
both species counted on the same fully dated nest day and same fully dated chick
day. The last two are distinct thresholds, not dynamically tuned sampling windows.

## Metrics and denominators
For species a,b record N_a,N_b (nests) and C_a,C_b (chicks), with N>0.
- Nest share b: N_b/(N_a+N_b).
- Chick share b: C_b/(C_a+C_b), missing if both observed chick counts are zero.
- Difference in recorded output b-a: C_b/N_b-C_a/N_a.
- Stage share shift: chick share b minus nest share b (percentage points in prose).
- Nest-ranking/chick-ranking reversal: strict inequality N_b-N_a and C_b-C_a
  of opposite signs; ties reported separately.
- Higher-nest-count species having lower output: signs of N_b-N_a and
  C_b/N_b-C_a/N_a opposite. This is an observed contrast, NOT a density/Allee test.
- If C_a,C_b>0, check exact log identity:
  log(C_b/C_a)=log(N_b/N_a)+log((C_b/N_b)/(C_a/N_a)).
No regression of a count denominator against its own ratio, no pseudocount for
zero chicks, no exclusion simply because the recorded ratio exceeds two.

Primary cohort: unique source comparisons with confirmed nest-before-chick
chronology in BOTH species. Secondary: all uniquely sourced comparisons and
same-full-date species surveys. Timing is source-reported, not independent field
validation. Common date does not imply equal chick age or census footprint.
Summaries separate row weighting and equal-site weighting, count sites/regions
and sources, and report leave-one-site-out mean ranges as sensitivity, never CI.

## Geography and claim limits
Reuse immutable V6 exact current SCAR geography at the same frozen site IDs,
SHA256 9ab362853535e8bdbbc63cc83803d1e7636ec37eeab7d55d17151f27036360ff.
Source mainland polygon 17692 is flagged rather than called an island. Nearest
points do not become exact land assignments. A mapped land unit is not a field
nest boundary or statistically independent population. Source cohort has no
validated per-species colony footprint, same chick-age or fledging-stage guard.
Use 'recorded chick output', not successful fledging, survival or recruitment.
The proxies alone cannot identify temperature effects, resource competition,
density dependence, dispersal, intrinsic species traits or source/sink status.
V1--V9, the original 216-test correction and PR189/PR199 are unchanged.

## Implementation and verification plan
1. Add failing fixtures for stage-rank reversal, unchanged rank with output
   dilution, zero and missing counts, ties, duplicate/unknown sources, chronology,
   same-date precision, source nesting, algebraic identity and weighting.
2. Implement one standard-library analysis module reusing the unchanged V9 reader.
3. Execute fixtures and local raw-input run; independently rebuild all pair
   metrics using rational arithmetic and independent date parsing.
4. Commit module, tests, contract and artifact-reuse workflow to PR206, with
   fast-forward/expected-head protection. Run full repository tests in GitHub.
5. Download real outputs, compare with local files, pin source/runs/results and
   provide the inspected result and limitations. No complete-test claim for a
   local overlay; separate normal CI and optional source workflows.
