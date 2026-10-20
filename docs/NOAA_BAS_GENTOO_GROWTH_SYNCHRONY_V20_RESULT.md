# V20 — Original NOAA/BAS three-island Gentoo source-normalized synchrony

2026-10-20. **A real biological descriptive association was computed**, not just a schema gate. The source-hashed original analyses and 7 synthetic tests ran successfully on GitHub [original NOAA/BAS V20 Actions #39409408546](https://github.com/zuizui0223/mina/actions/runs/39409408546); independent pull request Actions #39409413224 also passed.

### Source and estimand

Pinned NOAA NCEI 0185113 original 38-year, 5-column census XLSX SHA256 a57370f82adf82b53da11ce5d85dada1ae3f3750ef246312b59d0f168763eef4, and BAS Signy Island 43-row stage-resolved Gentoo CSV SHA256 53fe3821f313ed35840376fcf4d11c8e0e8fbbd63f01ba84a5e21c2db4df6d6b. Both originals re-downloaded, SHA-verified and parsed with zero unobserved years filled. Only within-site log(n[t+1]/n[t]) was computed because NOAA publishes unspecified 'species census count', whereas BAS publishes a breeding-pair index from ten Signy colonies. If each source has a stable multiplicative counting factor, this cancels in the log ratio, but changes in census composition and effort can still bias it.

All 16 fixed V19 original common seasons (1998–2009 and 2011–2014) have strictly positive reported original count in each of the three series. Hence the **14 complete consecutive-year three-island comparison windows** were retained, with no added log1p term, missing->zero imputations, changed source versions or post-result subset choice. The original BAS malformed '1998-8895' is still excluded.

### Numeric result: shared locality versus penguin species

| Comparison | Pearson correlation of within-series Gentoo annual log growth | Unit |
|---|---:|---|
| King George (NOAA) vs Livingston (NOAA) | **+0.6349134** | 14 same-season change windows |
| King George (NOAA) vs Signy (BAS) | **+0.1236897** | 14 |
| Livingston (NOAA) vs Signy (BAS) | **−0.0280594** | 14 |
| Arithmetic mean over three pairwise r | **+0.2435146** | 3 island pairs, not 3 independent tests |
| Same NOA A: Copacabana Gentoo vs chinstrap | **+0.6259489** | 12 same-rookery annual windows |
| Same NOAA: Cape Shirreff Gentoo vs chinstrap | **+0.7140219** | 14 same-rookery annual windows |

Three-way strictly concordant growth sign was found in **4/14 annual windows (28.57%)**, not broad whole-system synchronization. The early 1998–2005 comparison had 3/8 same-sign windows, the late 2006–2014 comparison 1/6. Leaving out any one year-pair changes the overall mean pairwise r from **0.10905 to 0.30417**. No inferential p-value, invented independent year replicates, spatially tuned radius or biological causal effect was fitted.

### Ecological meaning and hard constraints

**Descriptive interpretation**: within-NOAA nearby monitored breeding sites, Gentoo annual changes are more aligned than the same Gentoo series between NOAA and BAS Signy. At both NOAA locations, Gentoo and chinstrap within-rookery source counts also change together. Thus there is a plausible shared local/regional influence across species, not an obvious universal penguin-specific abundance response.

**Decisive alternative**: geography and monitoring programme are **perfectly confounded** among the three original programmes. Both correlated South Shetland sites belong to NOAA's US-AML R census and the distant Signy site to BAS with different counted life stage and colonial survey protocol. Positive same-source correlations **cannot isolate distance/ice, prey, wind, snow or direct interspecies facilitation**, nor prove geographic region matters more than taxonomy. The fact that time-invariant scaling cancels from log ratios does NOT remove time-varying programme observation effects. These are only 3 physical islands and they are not entire island census populations.

This result has **a concrete follow-up discrimination**: a physically distinct *BAS-monitored site closer to the South Shetlands*, e.g. Port Lockroy Gentoo at Goudier Island (1996–2020, official DOI 10.5285/92e92c14-0ff2-4ce2-8305-83d5b3a4071d), would break the simple geography=programme matching. The official BAS publisher gives methods, but its RAMADDA dataset parent currently exposes no verified downloadable child file in the ordinary machine-readable page. Do not use Dunn 2018 article Table 1 as supposedly novel original monitoring data or invent a BAS original CSV path. Previous Goudier census/tourist and climatic analyses are direct prior art (Dunn et al. 2018) and a newer 2026 re-evaluation exists.

An independent climate descriptor is potentially retrievable: Forcada et al. 2025 Signy *seasonal sea-ice concentration 1982–2024* DOI 10.5285/0283c3e4-2164-4dfb-a066-0c49b816d7b6; this is an original measured external covariate, but is **Signy-specific**, not automatically comparable to Antarctic Peninsula coast without a matching source. Before fitting an ice-driven synchrony mechanism, original annual geography- and stage-aligned exposures need independent verification; the original V20 result must not be retuned.

**Scientific decision: DESCRIPTIVE_REGIONAL_ASSOCIATION_ONLY_NOT_CAUSAL.** V14–V17 remain closed, frozen Ecology PR189 unchanged. This 3-island result is not a macroecological law; prospective geographically replicated, observer-balanced records are necessary.

- [Frozen V20 contract](../contracts/NOAA_BAS_GENTOO_GROWTH_SYNCHRONY_V20.md)
- [Machine-readable V20 numerical receipt](../results/NOAA_BAS_GENTOO_GROWTH_SYNCHRONY_V20.json)
- [Original NOAA publisher field definition](https://www.fisheries.noaa.gov/inport/item/55436)
- [Original BAS Signy method](https://data.bas.ac.uk/full-record.php?id=GB%2FNERC%2FBAS%2FPDC%2F01540)
