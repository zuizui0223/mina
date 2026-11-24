# Signy independent measured reproductive-stage outcome: exploratory winter coastal polynya comparison

Executed locally 2026-11-24, after matched demographic response gate 39c6e15406091b85ee18374a597aee0b8a2f37e9. The newly tested outcome is measured pre-fledging chick counts per counted pair, not individual survival, recruitment, or nest-count change. Reuse of existing BAS monitoring programme does not constitute independent geographic replication.

## Source recovery and exact support

[Run 45408427398](https://github.com/zuizui0223/mina/actions/runs/45408427398), source artifact 14925893778, SHA256 235d6c48a64a4926562cefd6876c474bf2891aff1e61887b34da05069970f7e4; original publisher CSV hashes verified by existing source parser (Git blob d0a3b8c3132193ea63d3b32496085421660e8b32) and source gate. Dunn et al. 2021 UK PDC: [Adelie](https://doi.org/10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d), [Chinstrap](https://doi.org/10.5285/d0633a9b-8c56-4ae5-88bf-6ec6ba9017b9), [Gentoo](https://doi.org/10.5285/883c6b40-024e-41e8-9c3e-2668a44b5751). Original 463 stage rows in standardized 1996–2019 window; 22 common species-seasons; 13 complete species seasons overlapping native polynya years. Original hatch mean source DOI 10.5285/274b49bd-40a4-4e5d-bd5f-69a1ba09d403, exact CSV SHA256 d86d42a581ec8f5bdf123a2073de17469714ce85031914c32b2489afc2187c94, 34 species-seasons, 17 matched years, 9 with P100/P25. These are model-derived mean hatching dates, not observed individual dates or independently observed laying dates. Native polynya artifact 14926710177 SHA256 b48ad3c97e35bc487ad6ebca955bbbec5478f75359e9f0300296910821a050b8; physical artifact 13829236358 SHA256 64a8e9832e254171139d78bb22351d6c9a3acf490356931b2635ed5b108d94b5.

Post-source-examination exploratory quality choices (not preregistered): exclude 2008 late fledgling counts, 2009 ambiguous nonbreeder/nest counts, 2013/14 nest surveys after hatching began, 2010 missing pair counts. Retain documented actual snow/failure in 2007 and 2015. Exclude composite or source-comment-ambiguous labels; select fixed literal colonies with positive pair counts, dated later fledgling count and count ratio in [0,2] in all nine retained years (2004–07 and 2015–19). Fixed A2/A3/A4, C15/C46/C47/C80, gentoo island aggregate. Spatial support differs by species, and gentoo is not a comparable set of subcolonies. All share same nine island years. Gourlay Point (GOPT) and North Point (NOPT) are nearby atlas proxy centres; neither is exact exposure for each nest nor independent geographic replication.

## Executed exploratory models

Annual median recorded pre-fledging chick count per breeding pair (species-specific fixed monitoring unit). Linear trend-adjusted coefficient per 1pp June–October P100; deletion ranges are sensitivity, not 95% intervals.

| Response | n | GOPT P100 slope | omit-one-year range |
|---|---:|---:|---:|
| Adelie |9| -0.007256 | -0.077984 to +0.047652 |
| Chinstrap |9| -0.010101 | -0.038977 to +0.022126 |
| Gentoo |9| +0.110860 | +0.018461 to +0.149313 |
| Gentoo minus Adelie |9| +0.118115 | +0.096444 to +0.135450 |
| Chinstrap minus Adelie |9| -0.002846 | -0.086629 to +0.093878 |

GOPT P25 gentoo-minus-adelie +0.077320, omit-year +0.024230..+0.115804. NOPT P100 contrast +0.117741 (+0.096203..+0.134854), P25 +0.045686 (+0.010144..+0.081426). Same fixed monitoring units, ratio-of-count-sums sensitivity GOPT P100 +0.112251 (+0.081750..+0.130281); NOPT P100 +0.111926 (+0.081623..+0.129893). At 25km the ratio-of-sums omission range includes negative values. Broader 13-year sensitivity with timing-compromised seasons GOPT P100 contrast +0.093979 (+0.039673..+0.121274). This is one island, not confirmation of the pan-Antarctic species contrast. Observed primary P100 range 0.7725–5.8489 pp, SD 1.6841 pp; do not extrapolate to a 10pp change. Full P100, SIC, SSS, SST and time trend design rank 6 in 9 years, residual df 3, fails earlier minimum 5; no such fitted coefficient claimed. No inferential p-values, no multiple comparison correction for exploratory diagnostics. Nine paired hatch seasons: P100 trend-adjusted Adelie +0.392197 days/pp (omit -0.345619..+0.650336), chinstrap +0.501118 (-0.058073..+0.612797), gap +0.108921 (-0.058840..+0.287546), no stable relation. Actual 2007 median success Adelie .387, Chinstrap .874, Gentoo .954; 2015 .503, .457, .143. Site quality comments prevent labeling delayed survey losses as mortality.

Reproducibility: local package signy_polynya_breeding_stage_20261124.zip SHA256 7ac42cbc6c51aed5657cb53936acf7507c96b783224142c23d6bb6e0faadeb7c; analyze.py 05ca0c2684c90a80a146584f712ad39fb71a1aa56e64fa407aa0235b48742ea1; sensitivity.py 235d03077e2d04aa6282b31d7ee1479d421fbbaca87bd6c760c29ab522f4c860. All 104 simple/trend/radius/site/response diagnostic slopes checked against residualized covariance. No raw BAS files republished.

Next distinct validation: NOAA NCEI accession 0171619 DOI 10.7289/V5Z036F7 contains nest-level camera/direct measurements, but source table not yet acquired or checked for independent overlap. Do not treat previously modeled BAS stage records as independent of census data. AADC Windmill reproductive success DOI 10.26179/wzem-0b04 catalog explicitly says data not yet publicly downloadable; no acquisition or redistribution. No merge or manuscript revision.
