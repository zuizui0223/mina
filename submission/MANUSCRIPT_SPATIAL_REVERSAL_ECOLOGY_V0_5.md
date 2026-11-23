# Breeding rebound largely retraces spatial loss after a mega-iceberg disturbance

**Ecology candidate v0.4 — PR189 spatial-reversibility paper**

## Abstract

Recovery after disturbance is usually summarized by whether abundance returns, but spatial recovery also asks whether abundance returns to the places from which it was lost. We quantified that reversibility in a colonial breeding network. A documented mega-iceberg disturbance reduced Ross Island Adélie penguin breeding abundance across six monitored components from 207,411 pairs in 1999 to 94,798 in 2001. By 2002, abundance had rebounded to 203,996 pairs, restoring 96.97% of the aggregate loss. Spatial recovery was also strong: normalized loss and rebound allocations overlapped by 90.6%, so 9.41% of rebound abundance would need to be reallocated to reproduce exact proportional reversal. The residual excess was concentrated at Cape Crozier West. This mismatch was similar to other Ross down–up episodes, indicating that the severe disturbance did not produce unusually large compositional reorganization. Prospectively frozen Gentoo and emperor-penguin tests further showed that aggregate change alone does not predict the direction of spatial reallocation. Thus a severe breeding disturbance was followed by rapid, largely reversible spatial reassembly, while exact local restoration remained incomplete.

**Keywords:** colonial breeding; disturbance; effective number; metapopulation; penguin; population recovery; spatial allocation; spatial redundancy

## Introduction

Recovery is often represented by a scalar: the fraction of population abundance regained after disturbance. A spatially structured population, however, can also recover in configuration. The biologically informative question is therefore not whether a rebound is mathematically identical to the preceding loss, but **how closely a real breeding network retraces that loss in space**.

This question sits within established work on spatial population dynamics rather than defining a new mathematical principle. Metapopulation theory has long separated regional abundance from local occupancy, rescue and patch-specific persistence, spatial-synchrony theory shows how shared environmental forcing and dispersal couple local trajectories [@bjornstad1999; @liebhold2004], and spatial-recovery theory shows that dispersal, network structure and spatially uneven disturbance can produce qualitatively different recovery regimes [@zelnik2019; @wilson2023]. Community-recovery experiments likewise show that abundance can recover more completely than multivariate composition [@hillebrand2020]. The narrower issue considered here is within-species spatial reversibility among persistent breeding nodes: after a shared disturbance, how much of the rebound returns in the spatial pattern from which breeding abundance was lost?

Colonial penguins are useful for this problem because breeding abundance is naturally partitioned among repeated monitoring units and because environmental forcing can act simultaneously across a region while being filtered by local access, habitat and demography. Ross Island Adélie penguins provide an especially informative natural experiment. Annual aerial censuses follow Cape Royds, Cape Bird and Cape Crozier, with Bird and Crozier further divided into repeated census components [@lyver2014]. In the early 2000s, giant icebergs B-15A and C-16 altered sea-ice conditions, access routes and breeding conditions around Ross Island [@lyver2014; @dugger2010; @dugger2014]. The disturbance produced a pronounced region-wide breeding trough, followed by rapid rebound, while mark–recapture and field studies document spatial heterogeneity in breeding participation, dispersal and apparent survival [@dugger2010; @dugger2014].

Our analysis began with a broader question about whether decline and recovery had opposite effects on spatial concentration. A pre-effect Ross Island contract fixed decline and recovery periods before breeding-count magnitudes were opened. The frozen prediction that recovery would increase effective colony number failed. We then recognized from independent natural-history evidence that 2001 was not an ordinary recovery baseline but a documented disturbance trough. We therefore treat the sharper 1999–2001–2002 disturbance–rebound decomposition as a transparent **post-result refinement**, not as a preregistered test. Its value is that the disturbance supplies a physically interpretable reference vector against which spatial reversal can be quantified.

We ask two main questions. First, how reversible was the Ross disturbance in aggregate and in space? Second, can the direction of spatial change be inferred from aggregate change alone? We address the second question with prospectively frozen external tests in a six-unit Gentoo penguin network at Bird Island and a 50-colony emperor penguin network around Antarctica. Prospectively specified mechanism tests are reported only as an inferential boundary because none yielded a confirmed general predictor.

## Methods

### Ross Island breeding census

We used the public Ross Sea Adélie penguin aerial census (DOI 10.7931/kf06-x745), summarized in the long-term Ross Sea analysis of Lyver et al. [@lyver2014]. The focal fixed six-component roster was:

1. Cape Royds;
2. Cape Bird South;
3. Cape Bird Middle;
4. Cape Bird North;
5. Cape Crozier West;
6. Cape Crozier East.

For colony-scale summaries, Bird South/Middle/North were summed as Cape Bird and Crozier West/East as Cape Crozier.

The counts represent occupied breeding territories or breeding-pair abundance near incubation, not the total adult population. Accordingly, annual differences can contain changes in breeding participation, abandonment, survival, recruitment and movement.

The original pre-effect Ross contract fixed 1985–1999 as decline and 2001–2012 as recovery. That test is retained in the audit trail. After the recovery prediction failed, independent published evidence identified 2001 as a severe B-15A/C-16 disturbance trough. The focal natural-experiment decomposition therefore uses:

- 1999: last complete pre-shock six-component census;
- 2001: documented disturbance trough;
- 2002: immediate rebound.

This three-state decomposition is explicitly post-result.

### Aggregate and spatial restoration

For component i, let A_i, B_i and C_i denote breeding abundance in 1999, 2001 and 2002.

Shock loss was

L_i = A_i - B_i,

and rebound gain was

R_i = C_i - B_i.

All six L_i and R_i were positive.

Aggregate restoration was

f = sum(R_i) / sum(L_i).

To compare the observed rebound with an exact spatial reversal while allowing the observed rebound total to differ slightly from total loss, we defined the inverse-path reference

R_i* = [sum(R_i) / sum(L_i)] L_i.

The minimum amount of rebound abundance that must be redistributed among components to convert the observed allocation into this reference is the half-L1 mismatch

M = 0.5 sum |R_i - R_i*|.

We report M / sum(R_i) as the fraction of rebound allocated differently from exact proportional reversal.

We also calculated cosine similarity between L and R to distinguish broad directional alignment from exact proportional restoration.

### Spatial concentration

For breeding abundance n_i, total abundance N = sum(n_i), and local share p_i = n_i/N, we calculated inverse-Simpson effective breeding-unit number

E = 1 / sum(p_i^2) = [sum(n_i)]^2 / sum(n_i^2).

E is an abundance-weighted concentration measure expressed as an effective number of equally represented breeding units. It is not occupancy richness, physical breeding area or genetic effective population size.

We also used total-variation distance between two composition vectors,

TV = 0.5 sum |p_i,1 - p_i,0|.

### Ross calibration and measurement boundary

To avoid presenting the focal mismatch as intrinsically large, we identified all complete successive Ross triplets in which all six components declined from the first to second observation and increased from the second to third. We calculated the same inverse-path mismatch and cosine similarity for those triplets. This comparison is descriptive and post-result.

The historical Ross source provides no component-specific standard errors or validated count-error model for the 1999, 2001 and 2002 counts. We therefore treat the 9.41% mismatch as a descriptive effect size. A separate deterministic sensitivity asks how large symmetric multiplicative perturbations of reported counts must be before exact inverse reversal becomes algebraically feasible; it is not interpreted as a confidence interval or estimate of census precision.

### Prospective Bird Island Gentoo sign test

To test whether positive aggregate change imposes a fixed direction of spatial change, we used the British Antarctic Survey Bird Island Gentoo penguin monitoring series [@birdisland2026]. Before endpoint magnitudes were opened, a contract fixed six breeding units and mechanically selected the earliest and latest complete six-unit seasons.

The frozen comparison was 1981–2024. We calculated total incubating nests and E at both endpoints. This interval was **not** defined as a disturbance–recovery episode; it is an external sign test.

The contract also pre-authorized a secondary audit of all successive complete-season transitions. For each transition we recorded the signs of delta log N and delta log E.

### Prospective global emperor penguin sign test

We used public colony-level model output from the global emperor penguin analysis of LaRue et al. [@larue2024] and its associated public repository. Before endpoint magnitudes were summarized, a contract fixed:

- all structurally paired colonies;
- 2009 and 2018;
- posterior median colony-level seasonal abundance index;
- global E;
- regional sensitivity across source-defined ice regions with at least three colonies.

The frozen support audit yielded 50 paired colonies. Because one colony had posterior median zero in 2009, colony-wise multiplication factors were not defined for the full roster; no colony was removed. Global N, E, composition and the zero-safe norm identity were calculated on all 50 colonies.

These are posterior-median point-estimate summaries. Public output does not expose jointly indexed colony posterior draws sufficient to calculate a posterior distribution for E, so no posterior probability of E decline is claimed.

### Mechanism analyses

Mechanism analyses were separated from the state/allocation result.

At Bird Island, a pre-effect chicks-per-nest predictor showed a strong association with next-season local share, but post-effect audit revealed shared-denominator and monitoring-semantic problems. A post-result ratio-free diagnostic remained weakly positive but was not confirmatory.

A prospective ratio-free replication at Signy Island used seven fixed Chinstrap penguin colonies from the BAS long-term breeding dataset [@signychinstrap2021] and late fledgling output adjusted for current breeding abundance. The frozen directional test failed (beta = -0.0225, permutation p = 0.6837).

A separate prospective Ross subcolony test used the mapped subcolony data of Schmidt et al. [@schmidt2021]. Perimeter-to-area ratio, independent of current abundance, was used to predict next-season local breeding growth while adjusting current abundance, mapped area and colony-by-year effects. Its frozen effect was negative but not supported by geometry-assignment permutation (beta = -0.0196, p = 0.1514).

No alternative lags, productivity measures, terrain variables or favorable subsets were opened as rescue analyses. Mechanism searching was closed after these failures.

## Results

### Ross aggregate abundance almost returned

Ross Island breeding abundance fell from 207,411 pairs in 1999 to 94,798 in 2001, a loss of 112,613 occupied breeding territories.

By 2002, breeding abundance had rebounded to 203,996, a gain of 109,198 from the trough. The immediate rebound therefore restored **96.97%** of the aggregate shock loss, and the 2002 total was **98.35%** of the 1999 pre-shock total.

### Spatial rebound closely retraced the preceding loss

The six-component loss and rebound vectors were nearly collinear: cosine(L,R) = 0.99695. After normalizing both vectors to unit total, their allocation overlap was 90.6% (total-variation distance = 0.0941).

Thus the rebound occurred broadly where the disturbance loss had occurred.

The rebound was not perfectly proportional across components. Relative to the inverse-path reference, residual rebound was:

- Royds: -1,313 pairs;
- Bird South: -3,891;
- Bird Middle: -931;
- Bird North: -1,213;
- Crozier West: **+10,271**;
- Crozier East: -2,924.

The half-L1 mismatch was 10,270.6 breeding pairs, equal to **9.41% of the observed rebound**.

At the broader three-colony scale, fractions of shock loss restored by 2002 were 38.7% at Royds, 68.3% at Bird and 105.2% at Crozier. At six-component scale they ranged from 10.8% at Bird South to 109.8% at Crozier West.

Effective breeding-unit number was also not fully restored: E_2002/E_1999 = 0.9366 at the three-colony scale and 0.8848 at the six-component scale.

### Residual spatial mismatch was moderate and ordinary-scale

The two other complete universal down–up triplets in the frozen Ross series had inverse-path mismatches of 9.12% (1989–1990–1991) and 10.63% (2002–2003–2004), with cosine similarities of 0.994 and 0.984, respectively.

The focal 9.41% mismatch is therefore ordinary in magnitude relative to other Ross reversals. What makes the focal episode informative is the independently documented disturbance and the near-complete aggregate rebound.

### Ross traversed several aggregate–spatial states

From 1999 to 2001, all six components declined and E increased. From 2001 to 2002, all six increased and E sharply decreased. From 2002 to 2012, total breeding abundance increased further while E modestly increased.

The system therefore did not follow a single monotonic relationship between total abundance and concentration.

### Positive aggregate change did not impose concentration at Bird Island

In the prospectively frozen Bird Island comparison, incubating nests increased from 3,331 in 1981 to 4,470 in 2024 (**+34.2%**). Effective breeding-unit number increased from 3.569 to 4.128 (**+15.7%**).

The initially small Square Pond unit increased from 224 to 911 nests, producing the largest positive residual relative to proportional aggregate change.

Across 42 pre-authorized complete-season transitions, all four sign combinations occurred:

- N up, E up: 12;
- N up, E down: 9;
- N down, E up: 8;
- N down, E down: 13.

Continuous annual changes were moderately correlated, so this result indicates that signs are not deterministically locked, not that aggregate and spatial changes are statistically independent.

### Global emperor decline concentrated, while regions spanned all directions

In the prospectively frozen 50-colony emperor penguin comparison, the sum of posterior median abundance indices declined from 239,178 in 2009 to 209,572 in 2018 (**-12.4%**). Effective colony number declined from 25.31 to 22.08 (**-12.8%**).

The local arithmetic was mixed: 30 colonies declined and 20 increased, with gross gains equal to 55.1% of gross losses.

The eight predeclared regional sensitivities contained all four combinations of aggregate and spatial direction.

### Candidate local predictors did not close the mechanism

The independent Signy ratio-free reproductive-output test failed its positive-direction criterion (beta = -0.0225, permutation p = 0.6837).

The Ross subcolony configuration test estimated the predicted negative perimeter-to-area coefficient (beta = -0.0196), corresponding to a 0.981 next-season growth multiplier per +1 SD, but the frozen permutation test did not support it (p = 0.1514). Crozier and Royds descriptive signs differed.

We therefore retain no general local predictor of spatial reallocation.

## Discussion

A severe breeding disturbance on Ross Island was followed by rapid recovery in both abundance and broad spatial configuration. Ninety-seven percent of lost breeding abundance returned within the immediate rebound, and normalized loss and rebound allocations overlapped by 90.6%. Spatial recovery was therefore highly reversible at the scale of the monitored breeding network, although about 9% of rebound allocation differed from exact proportional reversal, with the balancing excess at Cape Crozier West.

The calibration matters. The 9.41% mismatch was not unusually large relative to other Ross down–up episodes, so the mega-iceberg event did not leave an exceptional compositional displacement. The focal result is instead the degree of reversibility: a >50% temporary collapse in breeding abundance was followed within the next complete census by near-restoration of the aggregate and strong reconstruction of its spatial pattern.

The Ross natural history provides a plausible explanation for why exact reversal should fail. The B-15A/C-16 disturbance was shared regionally but filtered differently by colony position, sea-ice persistence and access to open water [@lyver2014; @dugger2014]. Mark–recapture work documents altered breeding dispersal and colony-specific apparent survival during iceberg years [@dugger2010]. A common disturbance can therefore produce local demographic responses that are similar in sign yet unequal in magnitude. We treat this as case-specific biological interpretation, not a fitted general mechanism.

The external tests show why the Ross direction should not be promoted into a recovery law. Bird Island Gentoo penguins showed positive aggregate change with increased effective breeding-unit number. Within the same Bird Island network, annual changes occupied all four aggregate–spatial sign quadrants. Global emperor penguins showed decline and concentration at the continental scale, yet prespecified regions again occupied all four directional quadrants. Together these results support a deliberately narrow statement: the direction of aggregate breeding change does not uniquely specify the direction of spatial reallocation.

This distinction is mathematically straightforward. If local abundances are n_i, aggregate change depends on the abundance-weighted common component of local growth, whereas changes in relative shares depend on each local growth rate relative to that common component. The algebra is established; the ecological contribution here is empirical calibration against a documented disturbance and prospectively frozen external sign tests.

The finding is related to, but different from, spatial metapopulation recovery scenarios in which aggregate abundance can recover while patch occupancy or local populations remain impaired [@wilson2023]. The Ross breeding nodes all rebound from the 2001 trough. The mismatch instead concerns their **relative abundances among retained nodes**. Likewise, pulse-disturbance experiments show that community abundance can recover much more completely than multivariate species composition [@hillebrand2020]; here the composition is spatial and within a single species.

Our attempts to identify a transferable local predictor were intentionally conservative and ultimately unsuccessful. The strong Bird Island reproductive-output association proved measurement-sensitive and did not replicate in a prospectively frozen ratio-free Signy test. Mapped subcolony perimeter-to-area ratio at Crozier and Royds was directionally consistent in the pooled analysis but failed the frozen permutation criterion. These failures matter because they prevent the paper from turning a state-space result into an unsupported mechanism story. What selects the local contrast mode remains open.

Several limitations constrain inference. Ross count uncertainty is not reported at a resolution that permits a formal confidence interval on the 9.41% mismatch. The deterministic bounded-count analysis is only a robustness threshold, not an error model. The sharper Ross disturbance–rebound decomposition was developed after the original frozen recovery prediction failed, and we therefore treat it transparently as post-result. Bird Island provides a prospectively frozen sign test but not a second identified recovery event. Emperor results use posterior-median point estimates without joint posterior draws for E.

The monitoring implication is nevertheless useful. A total abundance index answers how much breeding activity is represented, but not how that activity is distributed across the monitored network. Spatial allocation need not replace abundance as a recovery metric, and effective unit number is not universally the appropriate conservation target. Rather, when component-resolved counts already exist, retaining the abundance vector preserves information that cannot be reconstructed from the total after aggregation.

The central conclusion is therefore calibrated rather than spectacular. **Near-complete numerical rebound can leave a moderate, structured failure of exact spatial reversal, and the sign of aggregate breeding change is not sufficient to infer the sign of spatial reallocation.** Future mechanism work should begin with prospectively measured, abundance-independent local predictors—such as disturbance-induced access cost or individual movement and survival—rather than additional post-hoc screening of the datasets opened here.

## Acknowledgments

OpenAI ChatGPT (GPT-5.6 Sol) was used to assist with code drafting and review, literature searching, statistical sensitivity-analysis scripting and editorial drafting. All analyses, source verification, scientific decisions, interpretations and final text were reviewed and remain the responsibility of the authors.

[Add non-AI acknowledgments and funding acknowledgments after author confirmation.]

## Data availability

Ross Sea Adélie aerial census: DOI 10.7931/kf06-x745.

Bird Island Gentoo monitoring: DOI 10.5285/8fedb5a0-b98c-4457-9d86-aae9c6d3ed8e.

Global emperor colony model output: public davidiles/EMPE_Global repository; frozen analysis source and checksums are recorded in the PR189 result receipts.

Schmidt et al. Ross subcolony processed data and code: public pointblue/adpe_subcol_success repository and linked data archive.

Signy Chinstrap monitoring: DOI 10.5285/d0633a9b-8c56-4ae5-88bf-6ec6ba9017b9.

All frozen contracts, support receipts, result receipts and reproducible analysis scripts used here are maintained in the public mina repository.

## Reproducibility and computational assistance

OpenAI ChatGPT (GPT-5.6 Sol) assisted with code drafting and review, literature searching, statistical sensitivity-analysis scripting and editorial drafting. All scientific decisions were checked against version-controlled contracts and result receipts. The authors remain responsible for all analyses, interpretations and text.

## References

Bibliography file: `submission/REFERENCES_SPATIAL_REVERSAL_V2.bib`.
