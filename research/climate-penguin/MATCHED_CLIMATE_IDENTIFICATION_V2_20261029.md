# Same-site species temperature association: rank, chronology and land/year checks

2026-10-29. Post-exploration follow-through on PR206; frozen Paper1 and PR199 are untouched. This is not a new confirmation and does not alter the previous 216-test correction family.

## Main result and sign

All numbers here use SECOND species minus FIRST: ADPE|GEPE = Gentoo minus Adelie in annual change of log(1+nests). They are climate-change covariation slopes per degree C of year-on-year atmospheric temperature difference, NOT a causal effect of long-term anthropogenic warming.

The 45 source-matched Gentoo/Adelie year comparisons (7 site IDs, 2 regions) give:

| Predictor | Site fixed | Site + common year fixed |
|---|---:|---:|
| September | +0.0162120692 | -0.0289676303 |
| August–November | +0.0324004973 | +0.0698931214 |

The original 12 coefficients in run 40869241922 were independently reproduced by direct weighted/dummy design least squares on the downloaded 381-row source join, maximum absolute error 1.43e-14 after reversing the original first-minus-second sign.

## Temporal sensitivity, not confidence intervals

Leave one ending-season-year out of the unchanged 45-comparison sample:

| Predictor | Site fixed range | Site + year fixed range |
|---|---:|---:|
| September | -0.0010660183 to +0.0232776308 | -0.1243762404 to +0.0180886807 |
| August–November | +0.0065015382 to +0.0448911388 | -0.0018879804 to +0.1760958482 |

For Aug–Nov + year adjustment, omitting end-year 2000 (three comparisons) leaves 42 rows and slope -0.0018879804. Omitting end-year 2012 leaves +0.0018971235. Thus the adjusted positive association is sensitive to particular years, despite positive site/land deletion results. These ranges are not inferential confidence intervals.

## Same mapped-land sample

The climate-overlap sample differs from the earlier 51-comparison no-climate contrast. Here strict mapped-land containment excludes LION, leaving **41 comparisons, 6 source site IDs, 5 different SCAR land feature IDs**. Do not substitute the earlier 46-row sample.

Aug–Nov: unweighted exact-land sample slopes +0.0479448962 (site fixed) and +0.0680315256 (site + year). Equal total weight per mapped land, then equal site weight within land, gives +0.0681511128 and +0.0789805237 on exactly these same 41 rows. Deleting each mapped land yields +0.0347737449 to +0.0625289696 and +0.0488325384 to +0.0960403716, respectively. These checks separate geographic reweighting from sample exclusion; current mapped-land polygons are still not historical nest footprints or verified independent island populations.

## Correct an actual model-quality bug

The old sample-size gates were insufficient to prevent fully saturated site+year models. CHPE|GEPE has 22 rows, nuisance rank 21, full design rank 22, **zero residual degrees of freedom**. A unique algebraic interpolating slope exists, but no residual information remains to assess model error. The implementation now retains that number only in `algebraic_coefficient_audit_only`, returns null for the supported coefficient, labels `SATURATED_NO_RESIDUAL_DF`, and excludes saturated jackknife refits. ADPE|CHPE site+year has residual df 1 and is explicitly flagged; ADPE|GEPE has residual df 15. This is a mathematical diagnostic, not a post-hoc ecological significance threshold.

RED/GREEN evidence: original function failed the synthetic saturation regression (returned 2.0 where supported output must be null); the corrected function passes that test and preserves the known-effect positive control. Four further local tests validate source-date conflicts, no default census month, equal-land weights and weighted fixed-effects recovery.

## Original dates: fields exist, but timing is mostly unresolved

The original MAPPPD observation CSV **does include year, month, day and date**. Earlier descriptions that the API only contains a season year were inaccurate. These fields must be joined and checked, not declared absent or assumed complete.

For the 45 Gentoo/Adelie comparisons, all four original count records have known calendar year/month in 5 comparisons; only 2 also match calendar months across species. September ends before all four counts in 5. The full Aug–Nov window ends before all four counts in **1 comparison**. In **4 Petermann comparisons (2003→2004, 2004→2005, 2005→2006, 2006→2007)**, some Adélie surveys occurred during November, so that exposure explicitly includes days after counting. The remaining 40 comparisons cannot be certified due to incomplete dates; they are not all known to be temporally reversed. No dates were imputed. PCHA 2016→2017 is the single fully preceding Aug–Nov comparison, with original counts in December 2016 and January 2018.

The matching 24 ADPE|CHPE and 22 CHPE|GEPE cohorts each have one fully dated/preceding comparison. A true pre-census species contrast cannot be estimated from these alone. No direction of causation, competition, sea-ice pathway or guano/vegetation mechanism follows.

## Provenance and reproducibility

Original source runs: 40868420083 (381 joined rows), 40869241922 (matched 91-row climate estimates), 40869812618 (source-land crosswalk). User-supplied original ZIPs and downloaded original artifacts were inspected locally. Input hashes: joined CSV `364933cd254fa9b0a542da92432e02ff61ff8e9a14548d73a8a568bc95140b3e`; MAPPPD observation pages `cd751e43ab61d57a6e7d3c7e918d673cf699392ac4bfccd546d29b99ea62f075` and `c2b054fb687d13eb93e67d48a2b492cd47c94ccdef75b562680b770ad6be18f3`.

Complete numerical diagnostic JSON, pair-level chronological checks, independent calculation script, test logs and source inputs are in the accompanying session deliverable `mina_matched_climate_followthrough_v2.zip`. Scientific status: **positive exploratory seasonal covariation with substantial timing/year constraints; no causal warming claim**.
