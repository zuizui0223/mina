# Dynamic colony history and limits of static island architecture for Antarctic penguin demographic coupling

**JBI submission draft v0.5**

**Running title:** Island information across scales

## Abstract

**Aim:** To test which ecological information transfers across scales: whether recent biological state is associated with within-island redistribution, and whether static breeding-island architecture predicts site-specific temporal coupling across Antarctica.

**Location:** Palmer Archipelago, western Antarctic Peninsula, and Antarctic breeding sites spanning the distributions of three *Pygoscelis* penguins.

**Taxon:** Adélie (*Pygoscelis adeliae*), chinstrap (*P. antarcticus*) and gentoo (*P. papua*) penguins.

**Methods:** We analysed 1991–2017 Palmer censuses for within-island concentration and the lagged association between late-season colony-wide state and redistribution, including an independent nest-level metric. We then analysed 1980–2025 abundance records for 104 predictor-complete site × species units. The Antarctic-wide test asked whether breeding-space amount and habitat-complex richness predicted site-specific coupling to species-wide annual forcing using 9,999 block-preserving permutations.

**Results:** Palmer decline involved concentration into fewer breeding components. Late-season state predicted redistribution at lag 2 (β = 0.0409, one-sided *p* = 0.00327) and lag 3, but not a predeclared 4–5-year recruitment echo. Mean chicks reaching crèche per monitored nest did not replicate the association (β = 0.0296, *p* = 0.232). A predeclared breeder-arrival test stopped at its frozen information gate: 69 matched colony-seasons across 18 predictor seasons did not meet the required 100, so no arrival coefficient was estimated. Antarctic area × heterogeneity interactions were negative in all three species but non-confirmatory across species (median γ_AH = −0.318, *p* = 0.0947); a simpler area effect was also unsupported.

**Main conclusions:** Palmer provides fixed-specification evidence for short-lived information in dynamic colony state, but not for a specific individual mechanism. Static landscape descriptors did not yield a confirmed Antarctic-wide rule for temporal coupling. This is not evidence that state replaces place.

**Keywords:** Adélie penguin, Antarctic Peninsula, breeding islands, colony state, demographic coupling, island ecology, scale, spatial concentration

## Introduction

Island ecology often treats persistent geography—area, isolation and environmental heterogeneity—as predictors of richness, persistence and extinction, with theory linking finite area to the amount and arrangement of usable habitat [@kadmon2007; @allouche2012]. Yet a breeding island is also a dynamic biological system whose realized value can depend on occupancy history, density and recent demographic state.

For seabirds and penguins, reproduction occurs on discrete terrestrial patches while most trophic acquisition occurs at sea. The breeding landscape therefore constrains reproduction without containing the dominant resource field. Marine subsidies already complicate island-biogeographic expectations [@obrist2020; @mulder2011; @grant2022]; here we ask whether terrestrial structure remains a stable response filter under largely external forcing.

We therefore separate two forms of island information. **Static information** describes persistent breeding-landscape properties such as ice-free area, relief and habitat-complex diversity. **Dynamic information** describes occupancy, breeder distribution and recent biological state. They can covary without being interchangeable: physical structure can constrain suitability while density, social processes and history update year-to-year use.

Performance-based breeding-habitat selection is not itself a new hypothesis. In Black-legged Kittiwakes, local reproductive success predicted subsequent breeder redistribution, and experimental manipulation of neighbouring breeding success altered attendance, site fidelity and recruitment [@danchin1998; @boulinier2008]. In Adélie penguins, a 24-year study at Pointe Géologie reported a strong association between colony breeding success and one-year-lagged growth and interpreted that pattern as coherent with public-information use [@meheust2024]. Those precedents make a simple positive one-year performance–growth association neither mechanistically diagnostic nor novel on its own. The unresolved problem is narrower: whether colony state contains temporal information after shared-denominator structure and persistent colony differences are separated, how long that information persists, whether it survives translation to an independently measured reproductive endpoint, and whether the resulting local signal can be compressed into static landscape descriptors that transfer across Antarctica.

The Palmer Archipelago provides a system in which these levels can be separated. Adélie penguin populations near Palmer Station have undergone major long-term declines while neighbouring islands share much of their regional context [@fraser2013; @pickett2018; @cimino2019; @cimino2025]. Previous Palmer analyses show that decline is not merely a reduction in total abundance: breeders become concentrated into a smaller effective set of within-island groups. Independent work also demonstrates that snow, topography and geomorphology structure subcolony persistence [@cimino2025]. The unresolved question is therefore not whether physical place matters, and not whether a one-year breeding-performance association can occur, but whether recent colony state carries additional temporal information about subsequent redistribution beyond persistent colony identity, abundance and the mechanically coupled one-year transition.

We addressed that question with a mechanism-motivated Palmer follow-up. We first quantified redistribution during decline, then defined a relative late-season colony state from colony-wide chick counts conditional on contemporaneous breeding-pair abundance. We asked whether that state predicted later relative growth among colonies exposed to the same island-scale annual conditions. A denominator-separated lag was used as the primary bias-resistant endpoint so that the predictor-year breeding-pair count was not reused as the denominator of the demographic transition being predicted. We further tested whether the signal behaved like a delayed 4–5-year recruitment echo and whether an independent nest-level measure of reproductive success reproduced the association.

Antarctic-scale relationships between penguin geography and demography also have substantial precedent. Ainley et al. tested whether *Pygoscelis* colony size was related to neighbouring colony abundance and distance within foraging range [@ainley1995], and Santora et al. later showed that colony size, clustering and distribution around Antarctica covary with social neighbourhoods, breeding-habitat availability, polynyas and submarine canyons [@santora2020]. Temporal structure is likewise well documented: Ross Sea Adélie colonies show strong synchrony in annual growth [@lyver2014], while a range-wide multiscale analysis found that prevailing sea-ice conditions explained much of the among-site variation in multidecadal Adélie growth but annual sea-ice anomalies explained little of the year-to-year variation [@iles2020]. Thus neither geographic structuring nor temporal synchrony is novel here.

The broader Antarctic system instead provides a narrower transferability test. Even if dynamic local history is informative within Palmer, it does not follow that static terrestrial breeding architecture predicts **site-specific coupling to demographic variation shared through time within each species**. The Antarctic Penguin Biogeography Project compiles long-term abundance records across Adélie, chinstrap and gentoo penguins [@checastaldo2023]. We used those data to ask whether breeding-space amount and habitat-option heterogeneity predict that temporal coupling under a predeclared cross-species test. This response differs from the colony-size and spatial-clustering responses used in earlier Antarctic geographic studies.

The study therefore asks a hierarchical question about **information transfer**. **Part I** asks whether local decline contains history-dependent state information beyond abundance and persistent identity. **Part II** asks whether static breeding-island architecture provides a confirmed, scale-invariant rule for **site-specific temporal coupling to shared demographic forcing** across Antarctica. The parts remain inferentially independent: the Palmer state result cannot rescue a non-confirmatory Antarctic-wide test, and the Antarctic-wide result cannot identify the mechanism of Palmer redistribution. This is **not a head-to-head predictive model comparison**: the two parts use different response definitions, spatial grains and species panels, so their coefficients, explained variance and predictive performance are not directly comparable. The synthesis is instead claim-based: the repaired Palmer state association is evaluated under a fixed specification with an explicit provenance caveat, whereas static architecture is tested against its own predeclared Antarctic-wide transferability criterion. The question is what information survives each scale transition, not whether “state” beats “place.”

## Materials and Methods

### Part I: Palmer discovery system

#### Demographic census

The Palmer analysis used annual breeding-pair censuses from five Adélie breeding islands monitored by the Palmer Station Antarctica Long Term Ecological Research program: Christine, Cormorant, Humble, Litchfield and Torgersen. The synchronized panel spans 1991–2017 with 27 complete island-year observations. Colony-level counts were summed to island totals, and abundance was analysed as log(1 + N). Data provenance and checksums are frozen in the project receipts (Palmer LTER census DOI: 10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e).

We standardized each island's log-abundance trajectory and used principal component analysis to quantify the common temporal component. Annual log growth was

$
g_{i,t}=\log(1+N_{i,t})-\log(1+N_{i,t-1}).
$

Year and island factors were also used descriptively to partition shared temporal and persistent island-level variation. These terms are descriptive and are not interpreted as identified environmental mechanisms.

#### Within-island concentration

For island-year (t), let (p_j) be the fraction of breeding pairs assigned to colony code (j). We defined effective colony number as

$
N_{\mathrm{eff}}=\frac{1}{\sum_j p_j^2}.
$

The concentration analysis was restricted to Cormorant, Humble and Litchfield, the three islands whose reported colony-code rosters remained unchanged across the synchronized period. For Litchfield, only positive-abundance years were retained.

For each island, the observed statistic was the ordinary least-squares slope of annual (N_{mathrm{eff}}) against centered calendar year. We tested whether that slope could arise from proportional thinning under a fixed-composition null. A time-invariant colony-code composition was estimated from cumulative counts, multiplied each year by the observed island total, and subjected to prespecified independent count-error models: Poisson sampling plus Gamma–Poisson sensitivities with 10% and 20% multiplicative CV. We generated 100,000 realizations per model. The one-sided island-specific probability was the fraction of simulated slopes at least as negative as observed; a joint probability required all three island slopes to be simultaneously at least as negative as observed.

This null preserves the empirical decline in island total while removing temporal change in latent colony composition. Rejection therefore establishes demographic redistribution beyond proportional thinning plus independent count error. It does not identify physical nesting polygons or a causal mechanism.

#### Late-season colony state and lagged redistribution

For each eligible island-season, we combined the independent November adult breeding-pair census with the January chick census assigned to breeding season by the frozen `PALYYZZ` study identifier. For colony *i* in season *t*, expected chicks under proportional production were

$
E_{i,t}=C_t\frac{N_{i,t}}{N_t},
$

where (C_t) is total island chick count, (N_{i,t}) is colony breeding-pair abundance and (N_t) is island breeding-pair abundance. We calculated a Pearson-type residual,

$
Q_{i,t}=\frac{C_{i,t}-E_{i,t}}
{\sqrt{\max\{E_{i,t}(1-N_{i,t}/N_t),10^{-12}\}}},
$

and standardized (Q_{i,t}) within island-season to obtain the late-season colony state (S_{i,t}). This state is relative by construction: it identifies colonies whose late-season chick abundance is high or low compared with contemporaneous colonies on the same island after accounting for breeding-pair abundance.

For adjacent adult censuses we defined colony growth as

$
G_{i,u}=\log(1+N_{i,u+1})-\log(1+N_{i,u}),
$

and relative redistribution (R_{i,u}) by subtracting the mean (G) of eligible colonies within the same island-transition. Prior colony size was standardized within the same transition. For lag (k), (S_{i,t}) predicted (R_{i,u}) with (u=t+k-1), controlling prior size and an island × colony-code fixed effect.

Lag 1 is mechanically coupled because (S_{i,t}) and growth from (t) to (t+1) both contain (N_{i,t}). We therefore treated lag 2—state in season (t) predicting redistribution during (t+1\rightarrow t+2)—as the primary bias-resistant endpoint. Inference used 100,000 Monte Carlo permutations in which (S_{i,t}) was reassigned among eligible colonies within each predictor island-season while outcomes, missingness and controls were fixed.

We also froze a lag-profile diagnostic for lags 1–5. A delayed local recruitment echo was defined as

$
C_{\mathrm{recruit}}
=\frac{\beta_4+\beta_5}{2}
-\frac{\beta_2+\beta_3}{2},
$

with the prediction (C_{\mathrm{recruit}}>0). This contrast tests whether the association strengthens near the age at first breeding; it is not treated as a unique signature of public-information use.

The lag specification underwent one provenance repair. The first implementation assigned chick season from calendar date, conflicting with an earlier outcome-blind contract that had already established `PALYYZZ` as the canonical season key. We repaired only that key and left lags, model, performance metric, sensitivities and decision thresholds unchanged. Because observed coefficients had been exposed before the repair, we treat the repaired analysis as **fixed-specification validation**, not as a fully outcome-blind preregistered test.

#### State persistence and independent nest-level validation

To ask whether the lagged association could be explained by simple persistence of the measured colony state, we estimated colony-specific state memory,

$
S_{i,t+h}=\rho_h S_{i,t}+\alpha_i+\epsilon_{i,t+h},
$

for (h=1,2,3), with colony fixed effects and within-season permutation inference. We also used a non-causal bridge diagnostic in which redistribution during (t+1\rightarrow t+2) was modeled using both (S_{i,t}) and measured (S_{i,t+1}), along with prior size and colony identity. Because (S_{i,t+1}) is post-(t), this is explicitly not interpreted as causal mediation.

We then tested whether the result generalized to independently monitored nest reproductive histories from the Palmer LTER REPRO archive. For each monitored nest we counted the number of chicks with a positive recorded crèche date (0–2). Colony-season nest success was the mean number of chicks reaching crèche among monitored nests, requiring at least five nests per colony-season. This endpoint does not use the colony adult census in its denominator. It was standardized within island-season and tested against next-year relative colony growth with the same prior-size and colony-identity controls and 100,000 within-season permutations.

Historical REPRO files encode absent crèche dates as zero whereas recent files use blanks. Before fitting the performance-growth coefficient, we froze a source-semantic repair that counts only positive numeric crèche dates as successful events. A binary “any chick reached crèche” metric was retained as a prespecified sensitivity and could not rescue a failed primary endpoint.

A subsequent same-panel comparison between the colony-wide state and REPRO state is reported only as a post-result diagnostic. It tests whether failure of the independent endpoint arose because the REPRO validation subset lacked the original signal or because the two metrics represent different biological states.

#### Independent spatial triangulation

We used published Torgersen mapping as phenomenon-level spatial triangulation rather than as a merged response dataset [@cimino2025]. That work reconstructs historic active subcolonies and links persistence/extinction to snow- and terrain-related landscape conditions. Agreement with the colony-code analysis is interpreted as independent evidence that concentration reflects a real spatial-demographic process, not proof that nominal colony codes correspond one-to-one with mapped footprints.

### Part II: Antarctic-wide transferability test

#### Outcome-blind analysis frame

The broad-scale analysis used MAPPPD/APBP abundance data pinned to a fixed source commit. Gate 0 contained 152 Pygoscelis site × species units. A common 1980–2025 breeding-season window and predeclared temporal-coverage rules yielded 107 bridged units and 2,100 nest-count records. After joining the prespecified terrestrial predictors and preserving missingness at unsupported sites, the final predictor-complete frames contained 41 Adélie, 34 chinstrap and 29 gentoo site × species units.

Predictor construction was completed without demographic outcome magnitudes. At the primary 2 km radius, breeding-space amount was

$
A=z\left\{\log\left[1+\mathrm{ice\text{-}free\ area}\right]\right\}.
$

and breeding-option heterogeneity was

$
H=z\left\{\mathrm{Tier\ 2\ Habitat\ Complex\ richness}\right\}.
$

The focal interaction was \(A \times H\). Terrain relief was frozen as a separate predictor but was not used to rescue the primary interaction.

#### Observation model and recovery gates

Direct counts were the reference observation method. Image-based counts received one shared mean offset, supported by repeated direct/image observations within the same site × species × season. Observation precision was represented by two frozen accuracy groups: class 1 versus pooled classes 2–5. Unknown-vantage records were retained in the primary cohort but excluded from method-offset calibration.

Before real count magnitudes were opened, we required the complete estimation pipeline to recover prespecified null, simple-buffering and interaction scenarios on the real temporal and observation schedules. Candidate forcing partitions and estimators that failed these gates were rejected rather than retuned. The retained model used one species-wide latent annual forcing per species, while geography entered only as a loading-adjustment stratum (CCAMLR blocks for Adélie; APBP regions for chinstrap and gentoo). Full gate history and failed candidate estimators are reported in the Supplement and reproducibility receipts.

Within each species, site coupling was modelled conceptually as

$
\lambda_i =
1+\alpha_{b(i)}
+\gamma_A A_i
+\gamma_H H_i
+\gamma_{AH}A_iH_i
+b_i.
$

where \(\alpha_{b(i)}\) is the frozen spatial-block effect and \(b_i\) is a residual site loading deviation. Site-trait terms were centered within the frozen spatial block. The latent annual forcing had mean zero and site loadings were identified to a species-wide mean of one.

The process model used log1p abundance and propagated endpoint observation variance into interval likelihoods. Pre-outcome synthetic recovery required the estimator to recover null, simple-buffering and crossover scenarios under the real observation schedule. Species-wide forcing, the focal interaction and the cross-species median estimand all passed the frozen recovery rules before real outcomes were opened.

#### Primary hypothesis and inference

The primary paper-level statistic was the median \(\gamma_{AH}\) across the three species. The directional alternative was more negative. We used 9,999 permutations. Within each species and frozen spatial block, the complete site-trait tuple \((A,H,A\times H)\) was permuted among site time series, singleton blocks were fixed, and the complete V3 model—including forcing, drift, process variance, block intercepts and residual loadings—was re-estimated.

The paper-level p-value was

$
p=\frac{1+\#\{T_{\mathrm{perm}}\leq T_{\mathrm{obs}}\}}{9{,}999+1}.
$

Species-specific interaction p-values used the same one-sided rule and were Holm-adjusted across the three species.

A full point-estimate option–fragmentation crossover required

$
\gamma_{AH}<0,
$

$
\gamma_H-\gamma_{AH}\geq 0
$

at \(A=-1\) SD, and

$
\gamma_H+\gamma_{AH}<0
$

at \(A=+1\) SD.

#### Prespecified secondary and robustness analyses

The simple breeding-space buffering hypothesis was evaluated with A-only versions of the same spatially adjusted model. Species-specific one-sided permutation p-values were Holm-adjusted.

Observation robustness re-estimated the shared image/direct offset using exact-date direct/image pairs and pairs separated by no more than 14 days, then refit the unchanged V3 process model.

Spatial-support sensitivity used 1 km and 5 km area/richness predictors and 2 km Shannon diversity. These variants were descriptive only; none could replace the frozen 2 km richness analysis.

Because the raw interaction changed sign across radii, we performed a post-inference interpretation diagnostic. The entire 1/2/5 km trait tuple for each site was permuted jointly within species × spatial block, preserving cross-radius covariance. Across 9,999 permutations we recorded the probability of reproducing both the observed negative 2 km / positive 5 km sign switch and a 5 km minus 2 km contrast at least as large as observed. Ecological scale-dependence language was allowed only if this joint probability was (leq 0.05).

Finally, we quantified the information content of a non-rejected primary result using a retrospective operating-characteristic analysis. The unchanged V3 simulation/model and real observation layout were used to generate common three-species interaction magnitudes from -0.20 to -0.60. Each synthetic paper-level statistic was evaluated against the realized frozen 9,999-permutation null. We report raw detection fractions plus interpolated 80% and 90% detectable-effect thresholds. This analysis is not an equivalence test or confidence interval.

## Results

### Part I: coherent decline, concentration and short-lived colony-state history

The five Palmer island populations shared a dominant long-term decline. The first principal component of standardized log abundance explained **96.4%** of total trajectory variation. Despite that shared temporal component, island endpoints differed, including persistence, strong decline and local extinction.

Within-island organization changed systematically during decline. Effective colony number fell from **3.54 to 2.86** on Cormorant, from **4.62 to 2.28** on Humble and from **5.78 to 1.00** on Litchfield before local extinction, corresponding to declines of approximately **19%**, **51%** and **83%**. Under the most severe prespecified 20% multiplicative-CV count-error model, Cormorant remained unusual (**p = 0.038**); no realization reached the observed negative slope on Humble or Litchfield in 100,000 simulations (plus-one **p = 0.000010** for each), and no simulation produced slopes simultaneously as negative as all three islands (joint plus-one **p = 0.000010**). Independent Torgersen mapping provides phenomenon-level spatial triangulation of this contraction [@cimino2025].

The late-season colony-wide state contained additional temporal information about redistribution. The lag-1 coefficient was positive (β₁ = **0.1004**, one-sided permutation **p < 0.00001**) but is not mechanistically interpretable because predictor construction and the (t\rightarrow t+1) growth transition share the (t) adult count. At the denominator-separated primary endpoint, state in season (t) predicted relative redistribution during (t+1\rightarrow t+2) (**β₂ = 0.0409, p = 0.00327**). The association remained positive at lag 3 (**β₃ = 0.0511, p = 0.00136**) and then faded: β₄ = 0.0223 (*p* = 0.121) and β₅ = −0.0148 (*p* = 0.770). The predeclared delayed-recruitment contrast was negative (**C_recruit = −0.0422, p = 0.988**), providing no support for a 4–5-year recruitment echo as the dominant explanation.

The lag-2 coefficient remained positive under the frozen exclusion, size-threshold and alternate-state sensitivities and in every leave-one-island-out fit. Measured colony state itself showed only weak persistence: (\rho_1 = 0.0639) (*p* = 0.0378), whereas two- and three-year state memory were non-confirmatory ((\rho_2) *p* = 0.0764; (\rho_3) *p* = 0.111). In the bridge diagnostic, past state retained a positive coefficient after measured next-year state, prior size and colony identity were included (**δ_past = 0.0296, p = 0.00154**). We treat this as a history diagnostic, not causal mediation.

The independent nest-level validation narrowed the biological interpretation. Mean chicks reaching crèche per monitored nest produced a small positive but non-confirmatory lag-1 coefficient (**β = 0.0296, p = 0.232**) and a slightly negative lag-2 coefficient (**β = −0.0164, p = 0.629**). A prespecified binary-any-crèche sensitivity was positive, but the failed primary endpoint prevents using that result as a rescue.

The original colony-wide state was not simply erased by the narrower REPRO validation panel. In the **61 colony-seasons** shared by the two metrics on Humble Island, the original state retained a substantially larger association with next-year redistribution (post-result diagnostic β = **0.1040**) whereas mean nest success remained weak (β = **0.0291**). The standardized states were only weakly correlated (**r = 0.132**), and adding nest success barely altered the colony-wide-state coefficient. In a post-result detectability diagnostic, the REPRO design detected an effect as large as β = 0.104 in **89.8%** of simulations; nest bootstrap resampling gave median state stability **r = 0.799**. Mean brood size among successful nests showed no positive association (β = **−0.0330**, post-hoc *p* = **0.779**). The informative Palmer variable is therefore best described as a **late-season colony-wide biological state**, not generic nest reproductive success.

A separate colony-level breeder-arrival dataset passed its prospective schema gate but failed the frozen information minimum: only 69 matched colony-seasons across 18 predictor seasons remained versus the required 100. No arrival coefficient or *p*-value was fit, and the threshold could not be lowered post hoc. This closes the predeclared arrival route at the information gate rather than producing a null result. Thus Palmer supports a pattern consistent with history-dependent redistribution, but does not identify adult arrival, retention, dispersal, prospecting or public-information use as its carrier.

[**Figure 1–2 near here**]

### Part II: local island organization did not yield a confirmed Antarctic-wide rule

At the frozen 2 km richness scale, fitted area × heterogeneity interactions were negative in all three species:

- Adélie: (gamma_{AH}=-0.304);
- chinstrap: (gamma_{AH}=-1.184);
- gentoo: (gamma_{AH}=-0.318).

The preregistered paper-level statistic, the median across species, was **-0.318**. The frozen one-sided block-permutation test did not reject the null (**p = 0.0947**). Species-specific raw p-values were 0.2162, 0.0661 and 0.0563 for Adélie, chinstrap and gentoo, respectively; no species-specific interaction survived Holm adjustment.

The point-estimate geometry nevertheless differed among species. Chinstrap and gentoo satisfied the full crossover sign pattern. For chinstrap, the fitted low-area and high-area heterogeneity slopes were +1.901 and -0.467; for gentoo they were +0.427 and -0.209. Adélie had a negative interaction but the high-area heterogeneity slope remained slightly positive (+0.045), indicating attenuation rather than a sign-reversing crossover.

The primary result is therefore **directionally concordant but non-confirmatory**. We do not interpret the chinstrap/gentoo subset as a rescued positive result.

[**Figure 3 near here**]

### Simple breeding-space buffering was also unsupported

A-only estimates were negative in all three species:

- Adélie: (gamma_A=-0.280);
- chinstrap: (gamma_A=-0.200);
- gentoo: (gamma_A=-0.071).

However, raw one-sided permutation p-values were 0.1426, 0.4225 and 0.3067, and Holm-adjusted values were 0.4278, 0.6134 and 0.6134. Thus the simpler prediction that greater breeding-space amount consistently weakens coupling to shared forcing was also unsupported.

### Observation calibration did not explain the interaction direction

The primary image/direct multiplicative offset was approximately **1.040**. Exact-date matching estimated a factor of **1.069**, and matching within 14 days estimated **1.058**. Refit cross-species median interactions were -0.326 and -0.323, respectively. All three species retained negative interaction estimates under both calibrations, and chinstrap and gentoo retained the full point-estimate crossover classification. Thus the direction of the primary interaction was not an artifact of the broad same-season image calibration.

### Radius sensitivity did not establish biological scale dependence

Raw cross-species median interaction estimates varied across spatial support:

- 1 km: **-0.058**;
- 2 km, primary: **-0.318**;
- 5 km: **+0.107**.

At 2 km, replacing richness with Shannon diversity produced a median interaction of **-0.163** and retained the chinstrap/gentoo crossover classification but not the Adélie negative interaction.

The apparent radius reversal was not sufficiently unusual under the joint multi-radius null. A negative 2 km and positive 5 km sign switch occurred in **24.78%** of null permutations. A 5 km minus 2 km contrast at least as large as the observed **0.425** occurred with plus-one probability **0.0971**. The preregistered joint event—sign switch plus an observed-size contrast—occurred 809 times, giving plus-one probability **0.0810**. The total 1/2/5 km range was at least as large as observed in **26.45%** of null permutations.

Accordingly, we treat the radius result as **sensitivity to spatial support**, not as evidence for biological scale dependence.

[**Figure 4 near here**]

### The non-confirmatory result constrains very large, but not moderate, common effects

The 5% lower tail of the realized paper-level permutation null was approximately **-0.424**. In retrospective simulations, a common true interaction of -0.20 was never detected in 300 replicates; -0.30 was detected in **4.7%**, -0.35 in **11.7%**, -0.40 in **38.0%**, -0.45 in **59.7%**, -0.50 in **81.0%**, -0.55 in **92.7%**, and -0.60 in **96.7%**.

Interpolated detectable-effect thresholds were **|gamma_AH| = 0.498** for 80% detection and **0.539** for 90% detection. The observed absolute cross-species median, 0.318, was only about 64% of the 80% threshold.

The primary non-rejection therefore does not establish absence of an interaction around the observed magnitude. It does, however, make a very large and consistently expressed three-species interaction less plausible: common effects around 0.50–0.55 would usually have crossed the frozen rejection rule.

## Discussion

### Local demographic history did not reduce to static island architecture

The central result is a cross-scale asymmetry in ecological information. At Palmer, decline had both a spatial structure and a short-lived history: breeders became concentrated into fewer effective colony-code groups, and a dynamically updated late-season colony state predicted where relative growth occurred over the following two to three years. Across Antarctica, however, static breeding-space amount and habitat complexity did not provide a confirmed, scale-invariant rule for population coupling to shared demographic forcing. This asymmetry is **evidentiary rather than a comparison of effect sizes**: we do not claim that the Palmer state explains more variance than the Antarctic landscape predictors, because the two analyses operate on different responses and grains. The defensible contrast is that Palmer yielded a fixed-specification local association with an explicit provenance caveat, whereas the static macroecological rule did not pass its predeclared transferability criterion.

This is not evidence that state matters while place does not. Palmer work independently shows that terrain, snow and geomorphology influence subcolony persistence [@fraser2013; @cimino2019; @cimino2025]. Instead, the results show that **realized breeding-landscape value has a dynamic component**. Persistent physical structure can shape the set of possible sites, while recent biological state can update which parts of that landscape accumulate breeders. The macroecological difficulty is that those dynamic histories are not necessarily recoverable from coarse static descriptors.

### Relation to performance-based habitat selection and public information

The Palmer result should be positioned as an extension of, not a first demonstration of, performance-associated habitat selection. Long-term observational work in kittiwakes showed that breeders redistributed toward previously productive patches, and an experimental manipulation later demonstrated that neighbouring reproductive performance could alter attendance, fidelity and recruitment [@danchin1998; @boulinier2008]. In Adélie penguins, Méheust et al. already reported a strong one-year-lagged breeding-success–growth association and explicitly noted its consistency with public-information use [@meheust2024]. Our lag-1 coefficient therefore has little standalone mechanistic novelty.

What differs here is the structure of the test. The primary Palmer endpoint separates the predictor-year adult count from the demographic transition being predicted, conditions on shared island-transition growth, prior group size and persistent colony identity, and examines the full lag profile rather than only the immediately following year. The association persists at the denominator-separated lag 2 and at lag 3, but the predeclared 4–5-year recruitment echo is not supported. Just as importantly, an independent nest-level reproductive metric fails to reproduce the primary association. The novel inference is therefore not “penguins use public information,” but that a **specific late-season colony-wide state carries short-lived demographic history that is not interchangeable with generic nest productivity**.

That distinction matters mechanistically. A public-information explanation remains compatible with the aggregate pattern, but so do retention, prospecting, latent local environmental persistence and other social or demographic processes. Colony counts cannot identify which individuals carry the history or which cue they perceive. The present manuscript therefore treats public information as a motivated hypothesis with strong precedent, not as the demonstrated mechanism.

### What the late-season colony state represents

The independent REPRO test is crucial for interpreting the Palmer result. Limited sample size alone is unlikely to explain the non-replication: on the exact common panel the REPRO design had about 90% simulated detection probability for an effect as large as the colony-wide-state coefficient. Nest bootstrap stability was moderate rather than negligible, although monitored-nest measurement error and sampling selectivity remain plausible contributors. Decomposition also gave no positive signal for brood size among successful nests; the positive any-crèche sensitivity remains non-rescuing because the frozen mean-production endpoint failed.

The original predictor should therefore not be called “reproductive success” without qualification. It is a late-season colony-wide state measured after breeding pairs have occupied the island and chicks have accumulated at colony scale. That state may integrate several processes: chick survival, late-season spatial aggregation, local density, social conditions, persistent but incompletely measured habitat quality, and observation-process components. The present data do not separate these contributions.

The lag profile nevertheless constrains some explanations. The signal persisted beyond the mechanically coupled one-year transition and remained at lag 3, but did not strengthen at lags 4–5. The predeclared recruitment-echo contrast was strongly negative. A simple story in which locally produced chicks return four to five years later and recreate the association is therefore not supported. Conversely, weak one-year state autocorrelation means that a perfectly persistent measured colony state is also insufficient as the whole description. The positive bridge coefficient suggests temporal information remains in past state after measured next-year state is included, but because that model conditions on a post-(t) variable it is not causal mediation and cannot identify the carrier.

### Static geography can structure colony distribution without predicting temporal coupling

The non-confirmatory Part II result does not overturn earlier geographic evidence. Colony size and spacing have been linked to neighbouring colonies and foraging-range competition [@ainley1995], while Antarctic-wide work relates colony size and clustering to social neighbourhoods, breeding habitat, polynyas and submarine canyons [@santora2020]. Those studies address **where colonies occur and how large or clustered they are**; Part II instead asks whether static terrestrial architecture predicts site-specific temporal coupling to shared within-species variation.

Likewise, Ross Sea colonies can fluctuate synchronously [@lyver2014], and prevailing sea ice can predict multidecadal Adélie growth even when annual sea-ice anomalies explain little annual variation [@iles2020]. Spatial distribution, long-term mean trend and annual coupling are distinct responses. Our result is restricted to the last of these, not a general failure of geographic or environmental explanation.

### Dynamic state and physical habitat are complementary

Palmer distinguishes **potential breeding landscape** from **realized breeding landscape**. Terrain and snow can constrain persistent suitability, while occupancy history and biological state can generate path dependence within those constraints. Static habitat-complex richness or ice-free area summarizes potential landscape structure but not which subcolonies were occupied, how breeders recently redistributed, or what late-season state developed. Static predictors can therefore be biologically relevant yet incomplete representations of short-term demographic organization.

### Externally subsidized breeding islands are not simple resource islands

Island theory links finite area and habitat heterogeneity because area constrains effective habitat availability [@kadmon2007; @allouche2012], while marine subsidies can alter island relationships [@obrist2020]. Penguins add a complementary geometry: terrestrial space is essential for reproduction, but most trophic acquisition occurs at sea. Breeding-space amount can therefore matter locally without being a general proxy for energetic carrying capacity, and heterogeneity can create alternatives, barriers or snow traps depending on scale and history. The non-confirmatory Antarctic result is consistent with terrestrial architecture being one component of response rather than a dominant, scale-invariant filter.

### The area × heterogeneity pattern remains suggestive, not established

All three 2 km interaction estimates were negative, but the preregistered paper-level test was non-confirmatory. Retrospective operating characteristics show why the result should remain bounded: effects near the observed magnitude were weakly detectable, whereas common interactions around 0.50–0.55 in magnitude would usually have crossed the frozen rule. The analysis therefore constrains very large common effects more strongly than moderate ones; it is a limit on transferability, not evidence of equivalence.

### Radius variation is a robustness problem, not a new ecological finding

The interaction changed markedly across 1, 2 and 5 km, but the joint null assigned probability 0.081 to the observed 2-to-5 km sign switch plus contrast. We therefore treat radius as sensitivity rather than biological scale dependence. The result still demonstrates that habitat heterogeneity is not scale-free and that conclusions about static architecture depend on spatial support.

### A hierarchy of ecological information

The combined analyses suggest three levels of information. First, **physical structure** constrains where breeding can occur and can influence persistence locally. Second, **dynamic colony state** records recent occupancy and biological history and can carry short-lived information about subsequent redistribution. Third, **individual behaviour** must determine how that history is actually carried through retention, prospecting, immigration or settlement.

The present study resolves the first two levels only partially. Palmer shows a pattern consistent with history-dependent local redistribution, but colony counts cannot identify the individuals or cues carrying that history. The Antarctic-wide analysis tests static transferability but cannot reconstruct local occupancy histories at every site. A recent 25-year Ross Island mark–recapture analysis shows that Adélie pre-breeders move among colonies much more frequently than established breeders, making prospecting and first settlement a biologically plausible level at which to test how colony history is carried [@dugger2026]. Such individual-level tests are a natural next step, but no Ross movement result is part of the present evidentiary chain.

More generally, ecological information can be valid at one hierarchical level without transferring to another. Island ecology should distinguish **local explanatory structure**, **dynamic state information** and **transferable macroecological structure**.

### Implications and limitations

The strongest Palmer inference is now narrower and more biological than simple concentration, but also more carefully bounded. The denominator-separated lag-2 association is a fixed-specification validation after a provenance repair, not a fully outcome-blind preregistered result. The bridge analysis is diagnostic rather than causal. Colony codes are repeated census units, not demonstrated one-to-one physical polygons. The late-season state itself is composite and does not reveal which causal cue, if any, penguins perceive.

The independent REPRO failure is also a limitation rather than a nuisance result. It shows that the association does not generalize automatically across plausible measures of breeding performance. The HUMPOP arrival test was not estimable under its frozen information rule, so arrival cannot be used to support or reject the mechanism. No preregistered mechanism-validation route remains pending in this manuscript. These closed failures prevent the local result from being inflated into a claim of public-information use.

At the Antarctic scale, the habitat metrics describe potential breeding landscapes around sites rather than annually occupied nesting footprints. Species-wide forcing factors are latent demographic summaries, not identified environmental drivers. The primary cross-species interaction was weakly detectable near the observed magnitude, and radius sensitivity shows that the landscape summary depends on spatial support.

Together, these constraints point to a more specific research program than further searching across static covariates. Future tests should link individual movement and first settlement to prior colony state, map occupied breeding footprints rather than only potential surrounding habitat, and incorporate local snow or substrate histories at the scale at which breeders actually redistribute.

## Conclusion

Antarctic penguin breeding landscapes contain ecological information at more than one timescale. At Palmer, a shared regional decline was accompanied by within-island concentration, and a late-season colony-wide state carried short-lived information about subsequent redistribution beyond prior abundance and persistent colony identity. That state did not generalize to an independent measure of mean nest reproductive success and therefore should not be treated as a generic productivity signal. Across Antarctica, static breeding-space and habitat-complex metrics did not yield a confirmed, scale-invariant rule for demographic coupling to shared forcing.

The resulting lesson is not that state replaces place. It is that **local demographic history is only partly represented by static island architecture**. Physical landscape, dynamic biological state and individual behaviour occupy different levels of the causal hierarchy, and information at one level need not transfer cleanly to another.

## Data Accessibility Statement

All analyses are tracked in an anonymized reproducibility workflow with frozen source versions, pre-outcome contracts, simulation-recovery receipts, permutation receipts and claim boundaries. Public source datasets retain their original licences and citations. A permanent archive of the exact submission code and derived non-restricted outputs will be provided before publication.
