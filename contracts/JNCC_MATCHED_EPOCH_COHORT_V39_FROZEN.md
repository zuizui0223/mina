# V39 — Two-census timing-comparability gate after observed V37/V38 dynamics

**Explicitly post-result robustness follow-up; proposed 2026-10-27, FROZEN before inspecting JNCC year-aligned subset counts/size scores.** Known results: 1,321 V30 exact-count panels including 959 with falling totals; V37 H1a score negative in 16/17 species; V38 concentration plus leadership turnover. This audit is not independent replication and cannot confer causal demographic meaning.

## Key original measurement risk

Original JNCC comparisons span Seabird 2000 (usually 1998–2002; gannet 2003–2005) and Seabirds Count (2015–2021). Different child Site.ID units within the same administrative Master site may have actually been surveyed in different years in either survey round. Apparent spatial compositional turnover can then confound a true change in site share with within-parent asynchronous census year.

## Pre-effect, source-only eligibility

1. Download original JNCC publisher revised XLSX, verify SHA256 \`9edf05b8af0a44c3ca770f390120c4b99bcaae3ae35fd844a82982d6ad8116d4\`. Require previous V29/V30 site metadata parent gates: 14,112 matched source site×taxon rows, 1,485 pre-guard and **1,483** guarded species × Country × Master × same original count-unit parents. Do not read either count cell L/O before this structural source gate.
2. Determine for each guarded parent using **original metadata only**: \`uniform_first_epoch\` when ALL child source years K are identical; \`uniform_second_epoch\` when ALL child source years N are identical. Primary stricter \`BOTH_YEARS_UNIFORM\` requires both. Do not select sites after looking at their actual size/share, do not relax year agreement to ±1 or 'same survey campaign' if exact uniform support is low.
3. Publish number of BOTH_YEARS_UNIFORM structural parents, original count units, number of species, distinct Country×Master networks, number of child records and source countries, before any biological score fit.
4. Exact integer matched original source count filtering and N0,N1≥2 as in frozen V30, with a final \`N1<N0\` cohort for original population decreases. Drop entire original parent with invalid count; unobserved missing count ≠ zero; preserve site IDs.
5. Source gate for new matched-year H1a V37 score: >=100 size-informative, integer-comparable, strictly year-uniform declining parents across >=8 species and >=30 distinct Country×Master networks and >=3 biological count-unit categories. Each eligible species must have >=3 of those panels for equal-species calculation. If sample gate fails STOP **before inspecting the new subgroup size-score**, not a negative biological effect.

## Frozen measurement-robustness estimands

- Reuse EXACT V37 site-size score \`S_g = sum_i(p1_i−p*_i)*[(log(1+n0_i)−mean_pstar log(1+n0))/sd_pstar]\` with \`p*=(n0_i+0.5)/(N0+.5k)\`; exclude only all-earlier-child-sizes-identical panels from this score.
- Species-equal mean S, number of species with positive mean, directional support as in V37, and source-country-leave-one-out sensitivity. **Do not change original V37 primary T**, negative result or null.
- Reuse exact V38 E>0, E>0 & S<0 and strict both-epoch-unique-leader switching, with original fixed denominator rules; report raw counts, raw fractions and species-equal means.
- For the size-score conditional ideal-count contrast, reuse exactly 1,999 multinomial null draws / parent, smoothed p0*, fixed later total, seed 20261027 and the same score/statistic. This is a *sensitivity*, not a new independent confirmatory test.
- Restrict V39 to this **one frozen timing restriction**, not choosing threshold/year windows or taxon selections retrospectively. No alternative "favorable" sensitivity if negative.

## Mechanism ceiling and STOP

- Passing temporal-source metadata alignment does **not** show identical site boundaries, similar coverage, survey effort, original count calibration, direct natal philopatry, social attraction, predator exposure or true physical-island dispersal.
- Large panel sizes and positive/negative conditional score contrasts cannot identify an Allee effect. They are observations over two survey epochs, not same-bird movements.
- V36 strictly mapped H2 refuge stops (3 mixed landmass parents, 0 with source mink variation). Predator reporting-niche associations from V34 are noncausal and are not fitted in V39.
- Source-only year-alignment counts are valuable even on a STOP: unequal-year detection bias and reassembly estimates should remain separately labeled.
