# Long-term climatic legacy v2 — completed exploratory test (2026-11-08)

**Conclusion:** Under the pre-fixed *2001–2020 site-level growth-rate* response (rather than annual changes), **1979–1990 absolute sea-ice concentration did not predict site trends better than contemporary 2001–2020 concentration**. Both were modestly useful for a spatial leave-one-site-out prediction. As an **independently prelisted but secondary** indicator, the *change* in SIC between eras had the lowest error in this limited regionally stratified sample. Its apparent signal is primarily **between regions**, not within region. This is **not a demonstration of 10–20-year climate debt, penguin philopatry, or a calibrated causal warming coefficient**.

## Provenance and execution

- Frozen before the new response-specific fit and scores: [FROZEN_LONGTERM_SLOPE_V2_20261108.md](FROZEN_LONGTERM_SLOPE_V2_20261108.md), commit `017e3d21e7b235f5cb6cd189e00316014aa34518`.
- Frozen calculation code: [longterm_slope_v2.py](longterm_slope_v2.py), first committed `baac08715586ae48f500d67cbf483b5362e7cebd`.
- Successful GitHub Actions [run #42440306026](https://github.com/zuizui0223/mina/actions/runs/42440306026), artifact **penguin-climatic-legacy-longterm-slope-v2** ID **13601222672**, includes full source SHA manifest, 26 site slopes and climate exposures, site-out / region-out predictions and metrics.
- Inputs pinned by Git blob SHA: original MAPPPD site seasons `fc134e364cf38699fa7611d7dee5fbbbcb370c0a`, original 39-site cohort `2b6c0793ea9f9ea9acf0771052cf7a2ad9ab335b`, monthly 1991–2020 satellite SIC `4fcea71c2d8b1069b6ad143f6522061ed434daf5`, 40 site coordinates `5a211a0eaa63b6a5d3516353dd9431428618dbd3`.
- 1979–1990 monthly OSI-450-a1 v3.1 reconstructed again with **1,920/1,920 site-months supported**; the fixed 1991/2001/2020 overlap-bridge audit used 120 site-months, median absolute difference 0.0807 percentage points.
- A slope-site is not a geographically independent climate replicate. This new study is outcome-aware exploratory follow-up, although the precise windows and metrics were committed before scores were computed.

## Fixed data and contrasts

Original 39-site ADPE long-series cohort → keep 2001–2020 original counts from the *same* known method at each site, at least four census seasons spanning 10 years → **26 sites, 257 site-year counts**, four regions: Victoria Land 17, Central-west Antarctic Peninsula 5, South Shetland Islands 3, Adélie Land 1. No source observations were synthesized to fill missing years; genuine recorded zero allowed via `log1p`. Response = per-site actual-year OLS slope in log1p(nest count), multiplied by 10.

SIC is the source-matched August–November nearshore (0–100km) concentration for each site. Compare past historical `H=mean(1979–1990)` (12y), contemporary `C=mean(2001–2020)` (20y), equal-width recent `C12=mean(2009–2020)` (12y), and auxiliary `ΔSIC=C−H`. All months require source support and all 12/20 years are fully observed.

Models include zero-growth, source-trained global mean, region ridge, region+H, region+C, region+H+C, region+C12, and region+ΔSIC, all with the same predetermined ridge penalties and training-only standardization. **LOSO predicts unseen *locations*, not unknown future *years***. LORO holds out an entire geographic region, but only four distinct regions exist.

## Numerical model comparison

### Leave-one-site-out (26 folds): MAE in log1p nests per decade

| Model | MAE |
|---|---:|
| Growth rate = 0 | 0.426000 |
| Prior-site global mean | 0.397761 |
| Region only | 0.309733 |
| Region + historical SIC 1979–1990 | 0.293330 |
| **Region + contemporary SIC 2001–2020** | **0.288443** |
| Region + equal 12-year recent SIC 2009–2020 | 0.287323 |
| Region + both historical and contemporary SIC | 0.287451 |
| **Region + era-to-era SIC change, ΔSIC (secondary)** | **0.266403** |

The primary historical advantage score, MAE(current)−MAE(history), was **−0.004887** (wrong sign for the long-lag hypothesis). Region-equal LOSO scores were 0.25038 current vs 0.25702 historical; refitting without all 17 Victoria Land sites yielded 0.28367 current vs 0.28545 historical. The equal-width 2009–2020 comparison also favored current (0.28732 vs historical 0.29333). Region-block bootstrap sensitivity (2,000 replications) of primary historical advantage: **[−0.007414, −0.004342]**; this is not a calibrated 95% inference with four independent climate units.

### Leave-one-region-out (four folds): MAE

| Model | 26 sites pooled MAE |
|---|---:|
| Growth rate = 0 | 0.426000 |
| Region only | 0.579050 |
| Historical SIC | 0.491896 |
| Contemporary SIC | 0.478959 |
| Both periods | 0.476267 |
| **SIC change ΔSIC (secondary)** | **0.390991** |

The ΔSIC model beat the zero-growth model by 8.2% in pooled LORO MAE and beat region-only by 32.5%, but those are **retrospective spatial holdouts of four regions** (one with a single site), not time-forward prediction of population change. LOSO the ΔSIC model beat region-only MAE by 14.0%.

## Critical ecological interpretation and geographic dependence

- Old/current absolute SIC climatologies were nearly indistinguishable across sites: **Pearson r=+0.99709**; **r=+0.96026** after removing region means. The previously fixed |r|≥0.95 collinearity threshold was crossed. Era-specific absolute effects **cannot be separately identified**, even though the model ranking slightly favors contemporary SIC.
- Site slope versus absolute past SIC: **r=+0.5541**, region-residual r=+0.0365; versus contemporary SIC **r=+0.5781**, region-residual r=+0.0800**.** These are descriptive spatial associations.
- Site slope versus ΔSIC=C−H: **r=+0.64774**, but only **r=+0.16491 within region**. Region-level means largely produce the pooled climate-change–growth correspondence.
- Region means (each site equal weight):

| Region | Sites | Mean SIC change (percentage points) | Mean growth (log1p nests / decade) |
|---|---:|---:|---:|
| South Shetland Islands | 3 | −7.05 | −0.293 |
| Central-west Antarctic Peninsula | 5 | −5.16 | −0.349 |
| Victoria Land | 17 | +2.00 | +0.343 |
| Adélie Land | 1 | +1.43 | +0.328 |

The directional contrast **is visible** but geographic history, sampling method, shelf and oceanographic gradients, prey supply, site accessibility, recruitment and terrestrial habitat remain viable alternative explanations. This study does *not* isolate a biological sea-ice change response within sites across time. The longer-duration slope response is less dominated by single-year variability, but the signal remains spatial, not a demonstrated site-level multidecadal lag. Absence of support for the old-absolute-SIC advantage should not be interpreted as absence of inherited population state.

## Prior-work and novelty guardrail

- **Iles et al. 2020, Global Change Biology**, DOI [10.1111/gcb.15085](https://doi.org/10.1111/gcb.15085), already reported a strong association of prevailing sea ice with long-term Adélie trends and weak (<10% explained) annual response. This scale contrast is therefore **not itself a novel discovery**.
- **Şen et al. 2023, Ecological Indicators**, DOI [10.1016/j.ecolind.2023.110239](https://doi.org/10.1016/j.ecolind.2023.110239), analyzed spatiotemporal model transfer in Adélie abundance over 24 sites. Spatial vs temporal transfer failure alone is not a novel unclaimed principle.
- **Youngflesh et al. 2026, Current Biology**, DOI [10.1016/j.cub.2026.06.028](https://doi.org/10.1016/j.cub.2026.06.028), linked sea-ice dynamics, penguin diet, and continent-scale population trends; a diet-to-abundance link is not new.
- The **narrow additional evidence** is a source-reconstructed 1979–2020 **historical vs contemporary vs change** exposure comparison against long-term slopes at 26 eligible source sites, with pre-fixed site/region holdout benchmarks, together with a separately documented failure to time-transfer annual and five-year nest predictions. The specific *historical-SIC advantage* was NOT supported, and the ΔSIC model was **secondary and exploratory**.
- The positive 6 genuinely co-breeding site ADPE↓/GEPE↑ series, the 2001–2009 Signy dietary association and the Palmer/Signy breeding-space contraction remain real but cannot be simply combined into a single warm→demography coefficient.

**Decision:** close this one-time exploratory long-term slope test as `WEAK_INCONCLUSIVE_OR_NONIDENTIFIABLE`. Do not hunt other lag years or retune the 2001–2020 census support to optimize the result. Preserve the ΔSIC spatial pattern as exploratory and use it in the existing one-paper climate scale/transfer discussion, not as a stand-alone demonstration of warming causality, climate debt or 2050/2100 penguin forecasts.
