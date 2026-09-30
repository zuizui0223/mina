# Palmer history-dependent redistribution synthesis v2

## Current ecological result

The Palmer analyses support a narrower result than either “place determines colony fate” or “penguins follow public information.”

The evidence chain is now:

1. Palmer Adélie breeders progressively concentrate into fewer effective colony-code breeding groups during regional decline.
2. Larger breeding groups show higher colony-wide chick production per pair relative to a frozen proportional-productivity null.
3. Immediate pre-extinction chick-state deficits are directionally negative but too sparse to confirm reproductive collapse as the proximate trigger of durable colony-code loss.
4. The frozen **late-season colony-wide state** predicts later within-island redistribution after shared island-transition growth, prior group size and persistent colony identity are removed.
5. The association remains at the denominator-separated lag-2 endpoint and at lag 3, but fades at lags 4–5; the predeclared 4–5-year recruitment-echo contrast is negative.
6. The measured colony state has weak one-year colony-specific memory but no confirmed two- or three-year memory under the repaired eligible-colony null.
7. Past late-season state retains incremental information about subsequent redistribution after measured next-year state, prior size and colony identity are included.
8. An independent nest-level REPRO endpoint **does not replicate the primary association**: mean chicks reaching creche per monitored nest has a small, non-confirmatory lag-1 coefficient and a slightly negative lag-2 coefficient.
9. On the exact Humble REPRO validation subset, however, the original colony-wide chick state remains strongly associated with next-year redistribution. The failed REPRO test therefore reflects a biological mismatch between metrics rather than simple loss of the original signal in the validation panel.
10. A colony-level HUMPOP breeder-arrival test passed its schema gate but failed the prospectively frozen minimum-information gate before any performance-arrival coefficient was fit.

The defensible Palmer synthesis is therefore:

> **Adélie breeding distributions are history-dependent: a late-season colony-wide biological state carries short-lived information about subsequent within-island redistribution that is not reducible to static colony identity, current group size, or the measured persistence of that state itself.**

The state should not be relabeled as generic reproductive success. It may integrate chick survival, spatial aggregation, social conditions, latent habitat state and observation-process components.

## What the pattern does and does not distinguish

A simple, spatially general “the same colonies remain environmentally good for several years” explanation is insufficient as a complete description because measured state autocorrelation fades quickly and is spatially heterogeneous, whereas the bridge coefficient remains positive under every single-island exclusion.

Persistent local environment is nevertheless **not ruled out**. The measured colony state is an imperfect proxy for any latent environmental process, and the bridge model conditions on a post-t variable and is not causal mediation. Measurement error or an unmeasured persistent state can leave information in past state.

Likewise, Palmer colony counts do not identify the carrier of the history. Adult retention, breeding dispersal, immigration, prospecting and public-information use remain hypotheses, not results.

## Why the REPRO result changes the wording

The independent REPRO validation used monitored nest histories rather than the colony-wide chick census.

Frozen primary result:
- mean chicks reaching creche per monitored nest: beta = 0.0296, one-sided permutation p = 0.232;
- lag 2: beta = -0.0164, p = 0.629.

A prespecified binary-any-creche sensitivity was positive, but the failed primary endpoint prevents using it as a rescue.

The key diagnostic is that the original colony-wide chick state and REPRO mean nest success are only weakly aligned. On the same Humble common panel, the original state remains predictive while the nest-level mean does not, and adding nest-level success barely changes the original state coefficient.

Therefore:

- **allowed:** late-season colony-wide state predicts later redistribution;
- **not allowed:** local nest reproductive success generally predicts redistribution;
- **not allowed:** the Palmer result independently proves public-information use.

## Independent individual-level mechanism gate: Ross Island

A suitable independent mark–resight system has now been identified rather than merely hypothesized.

USAP-DC provides:
- resight dataset 601444, DOI 10.15784/601444;
- banding dataset 601443, DOI 10.15784/601443;
- Royds/Bird/Crozier known-age histories used in the 2026 25-year multistate analysis.

Public READMEs were retrieved while reading **zero behavioral rows**. They document:
- stable individual identifier: `Band`;
- observation date: `Date`;
- observed colony: CROZ / ROYD / BIRD / BEAU;
- nest reproductive fields: `Eggs`, `Chicks`;
- band-number ranges linked to natal colony and fledging cohort.

Published state semantics can therefore be reconstructed prospectively:
- age >=2, observed before first breeding and without egg/chick breeding evidence = pre-breeder;
- first season with egg/chick breeding evidence = first breeder;
- later observed nonbreeding seasons = non-breeder.

The primary Ross test is frozen as **prospecting-to-first-breeding settlement choice**, not adult breeding dispersal, because published breeder movement is extremely rare while pre-breeder inter-colony movement is materially more common.

Candidate set:
- colonies actually visited as a pre-breeder in the two seasons before first breeding.

Chosen option:
- first breeding colony.

Prior-year colony state:
- frozen banded-breeder chick-presence index, because the independent USAP-DC 600007 chick-count source covers Royds and Crozier but not Bird.

Controls:
- natal-colony indicator;
- prior-year MAPPPD breeding-pair size.

MAPPPD size reconstruction is frozen and viable for 21 common years in 1997–2019.

### Current Ross stop rule

The scientific schema gate is **GO_prebreeder_choice**, but execution remains blocked before behavioral data access because the exact CSV header has not been verified.

The USAP-DC file API requires an API key and repository secret `USAP_DC_API_KEY` is absent. A schema-only workflow and fail-closed access guard are already installed.

No full resight download is authorized until:
1. the API key is added;
2. the workflow reads only the exact CSV header;
3. parser/header agreement is frozen in a new receipt;
4. the existing model, state coding, performance definition and minimum-information gate remain unchanged.

No Ross settlement direction, event count, coefficient or p-value has been observed.

## Manuscript-level wording

Strong enough now:

> Recent late-season colony state carries temporal information about subsequent within-island redistribution, producing a history-dependent breeding landscape during population decline.

Still not allowed:

- Penguins were shown to use public information.
- Better-performing colonies attracted identifiable immigrants.
- Adults left poor colonies.
- Prospectors selected successful colonies.
- Generic reproductive success predicts redistribution.
- Static landscape no longer matters.

The clean conceptual link to Paper 2 is:

> **Static landscape architecture did not yield a transferable macroecological response rule, whereas within Palmer, dynamically updated colony state contains short-lived information about where breeders subsequently accumulate.**

Ross Island is the prospective individual-level test of the carrier of that history, not supporting evidence until its still-locked outcome gate is opened.
