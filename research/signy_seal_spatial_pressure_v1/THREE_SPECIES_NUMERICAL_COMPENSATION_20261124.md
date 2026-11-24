# Signy three-species numerical compensation — executed descriptive reaggregation

Status: DESCRIPTIVE_DERIVED_REAGGREGATION_ONLY. Same source, same eligible periods, same six zones as the existing PR219 result; not a new independent observation, preregistered confirmation, hypothesis test, or functional-pressure estimate. Computed locally from verified Actions artifact 14917157831 (run 45387988565), SHA256 9e0a8b1684221c5874d8e23d7307d051d6fecddf0c8dfc91f0207fc1c162f781. ZIP CRC passed; exactly 216 unique complete year × zone × species nonnegative integer rows (12 × 6 × 3). No addition of excluded years or missing-value substitution.

Equal-year mean counts, early 2010/2012/2013/2014 vs late 2016/2017/2018/2019/2020/2022/2023/2024. Island sum of the three monitored species (not all vertebrates, biomass, or animal-days) 15184.5 → 6608.125, -56.4811156%. Changes: fur -8668.875; elephant +88.25; Weddell +4.25. Net numerical offset by the other two taxa = (88.25+4.25)/8668.875 × 100 = 1.0670358%. Leave-one-year-out range 0.1008573–3.0684614% (12 deletions, not CI). Total count decline leave-one-year-out range -63.2331842 to -50.9867852%. Species shares of period mean sum: fur 94.8763542% → 86.8268230%; elephant 5.0791926% → 13.0067152%; Weddell 0.0444532% → 0.1664617%. Ratios of equal-year mean counts, not mean annual proportions.

| Zone | Early total | Late total | Change % | Leave-one-year-out range % | Other two species net numerical offset % |
|---|---:|---:|---:|---|---:|
| 1 | 6249.25 | 2479.125 | -60.329240 | -64.686048 to -57.549192 | 0.389709 |
| 2 | 1359.25 | 666.375 | -50.974802 | -61.428309 to -45.048791 | -13.330607 |
| 3 | 3968 | 2135.125 | -46.191406 | -57.877304 to -39.589031 | 6.114739 |
| 4 | 1389.5 | 545.875 | -60.714286 | -66.297078 to -50.881074 | 2.471098 |
| 5 | 995.75 | 311.25 | -68.742154 | -74.148671 to -43.511797 | 1.155235 |
| 6 | 1222.75 | 470.375 | -61.531384 | -67.952800 to -30.003720 | 1.376372 |

All six combined-count declines survive every one-year deletion. Zone 2 has a negative net offset (other species reinforce rather than offset the fur decline); zone 3 has the largest positive numerical offset of these six zones. Changes in relative species share coexist with lower combined counts. Arithmetic does not demonstrate density-dependent replacement or competitive release.

## Ecological interpretation and limits

The available result establishes numerical noncompensation within the three observed taxa, alongside assemblage reweighting. No inference of equal per-individual ecological impact is made. Species differ in body size, habitat (including adjacent sea ice), survey-day haul-out probability, diet, residence duration, fecal/nutrient supply, and trampling. Thus combined census count does not estimate terrestrial pressure or biomass. A true pressure budget requires independently supported species-specific animal-days on land and impact weights; a single island and six zones cannot establish regional generality. No change to previous concentration inference (fur sign reversal under deletion) or original vegetation and tracking gates. The plant linkage, spectral classification and competition lanes remain blocked pending genuinely new original data; no further model fit or classification is claimed here.

## Reproduce

Download original successful Actions artifact 14917157831 (see https://github.com/zuizui0223/mina/actions/runs/45387988565) without repackaging. Run `python research/signy_seal_spatial_pressure_v1/reaggregate_three_species.py artifact.zip result.json`. Locally executed with the pinned ZIP; pandas pivot and independent standard-library implementation agree on all totals, ratios and deletion ranges. No workflow rerun required. Do not merge automatically or alter existing manuscripts.
