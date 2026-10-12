# V21 — Béchervaise tagged visitors versus first nesting: the same-ID observation link is ALREADY proven in 2019

Date: 2026-10-10. Exploratory Antarctic island ecology and data-access audit, not original tagged penguin source analysis. The standalone Ecology scientific manuscript PR189, USAP original bird data gate PR142 and emperor source audit PR195 remain frozen.

## Correcting an important V20 understatement

[Emmerson, Walsh & Southwell (2019), *Ecology and Evolution* 9:4637–4650](https://doi.org/10.1002/ece3.5067) **already linked actual individual RFID detections at the Béchervaise Island weighbridge to breeding/nonbreeding classifications derived from handheld nest scans and original direct nest censuses**.

That study covered **1998/99–2002/03**, which is earlier than the new AAS_4086 published 2006–2018 gate source, but proves the **method and original programme can make individual-level gate↔nest joins**. In the actual publication:

- Tagged adults from a fenced set of Béchervaise Island subcolonies passed the sea/colony weighing gateway; unique electronic TIRIS tag identities allowed body-mass records to be followed.
- Handheld on-nest tag identification was performed across the island **23–29 November** (predominantly males) and **11–18 December** (predominantly females). Direct nest observation supported laying/hatching/failed reproduction for a smaller group of tagged birds.
- The reported **>98%** handheld detection refers to **birds sitting tightly on nests**, NOT all tagged visiting nonbreeders, adults that failed early, other islands or never-returning nonbreeders.
- The paper calls a bird **nonbreeder** when it was detected visiting the island but was not recorded attempting to breed that year. Its methods recognize the potential for early failures to be misclassified as nonbreeders.
- The published 2019 analysis examined **breeders vs nonbreeders' seasonal mass patterns** (up to ~150 breeders and ~50 nonbreeders in a single five-day observation window), and for a subset classified known failed and successful breeders. It found unexpectedly similar qualitative within-season mass rhythms despite different incubation/chick-rearing burdens. The authors proposed hormonal/appetite synchronization as one possibility but did **NOT** collect simultaneous hormone measurements. **This biological pattern, the breeder/nonbreeder gateway comparison, and same-season linking are PRIOR ART.**

What remains *unverified and potentially distinguishable* is whether a **known-aged bird that VISITED in season t without a first egg**, then *the SAME tag* next season initiated its **first breeding attempt**, with identifiable social/food conditions and detection controls. The 2019 publication's seasonal mass analysis did not itself test that exact future transition. We cannot assert source files contain enough data to perform it.

## Publisher access obstacle now has a known mechanism

The AADC EDS public download links used in V20 are:

- [AAS_4518 direct source archive](https://data.aad.gov.au/eds/5516/download), containing demographic original resight and other files.
- [AAS_4086 weighbridge technical guide](https://data.aad.gov.au/eds/5228/download), **NOT** the original RFID gate event archive.
- [Publisher data download/access guide](https://data.aad.gov.au/docs/help/download-guide/).

The publisher's public download interface typically **requests a recipient email address** to send a one-time downloadable ZIP link or **S3 credentials**, depending on file size. [An independently observed AADC example](https://data.aad.gov.au/eds/5455/download) explicitly presents the email-required download form. The no-JavaScript HTML shell observed by our automatic probes in [V20 CI #38045283533](https://github.com/zuizui0223/mina/actions/runs/38045283533) is therefore **NOT proof that data are corrupted or absent**: the interactive email credential mechanism was not completed. We have **not** submitted anyone's email address, requested S3 credentials or retrieved any genuine original RFID/resight observations.

The AAS_4086 metadata specifically cautions about **unprocessed raw crossing data** requiring technical normalization, and requests **consultation with Louise Emmerson** before applying it. Her 2019 publication lists correspondence at Louise.Emmerson@aad.gov.au (2019 published contact, current delivery unverified). Publisher data sharing norms request consultation with custodians; do not silently extract an unauthorized individual tag dataset from alternate file mirrors.

Recommended human source-intake sequence, without sharing personal credentials in GitHub:

1. Open AAS_4518 data download in a regular browser; follow publisher's email-based access process and obtain the official ZIP/S3 URL or credentials privately.
2. Follow the AAS_4086 publisher metadata's dataset/technical-guide access paths to the **actual gate event archive**, not merely the guide; confirm with Louise Emmerson which 2006–2018 seasons have processed/usable IDs and timestamp corrections.
3. Ask whether **the same stable tag encoding** appears in AAS_4518 handheld on-nest resights, whether on-nest resight includes *egg laid, clutch and direct chick outcomes*, and how scan effort is recorded. Original 1998/99–2002/03 codebook and the relevant 2006–2018 technical corrections are needed.
4. Keep downloaded human-requested credentials and original sensitive source files **outside public repositories**. Use a controlled local copy for source checksum/source parser checks; report only source-proven aggregate QA in PR193.

## A mathematically honest synthetic inclusion gate, NOT penguin data

[Source-free simulation workflow](https://github.com/zuizui0223/mina/actions/runs/38056562688) tests a mock four-tag example and enforces four logically different observation states:

- One tag with repeated gate entries and a same-tag egg **after** first recorded entry;
- One with an on-nest tag scan, but **NO independently verified egg**;
- One with first documented egg **before** a later first observed gate entry;
- One inbound tagged adult with **no nest observation** and thus unknown egg state.

The number of **gate entry events** is not the number of distinct tagged birds. The example has **five inbound event records belonging to four tagged bird-season identities**, of which **one** has a documented subsequent same-tag egg. Even with this deliberately synthetic complete sample, the observed first-documented-egg-after-recorded-gate fraction is bounded **from 1/4 to 3/4** when no-egg statuses remain unknown, **not** a precise future first-breeding probability. A tag's first recorded gate passage is **not** necessarily its first actual arrival at the colony, and an initial egg observed AFTER passage is **not** necessarily that penguin's FIRST LIFETIME reproductive attempt without natal-age history.

Earlier toy simulation 1/4 to 1 mistakenly included an egg documented BEFORE first gate among those potentially eligible for a first documented egg AFTER; corrected in V21 and synthetic CI. This exercise is only a source/causal-label falsification, not a novel population mechanism.

## New causal ecological question to preserve only when original data exist

One useful contrast is *within incoming nonbreeders with the same observed prior breeding experience and age*: does **return to a colony without laying** change the subsequent probability of first breeding, compared with incoming individuals that successfully initiate an egg, after accounting for tag availability, individual quality, annual food/ice variation and adequate on-nest surveillance? Even that is not automatically causal and existing 2019 work already compares current-status body mass; to claim island biogeography requires independent recipient islands and some exogenous change in nest opportunities or arriving candidate supply.

A second test would compare individual season-t body mass against t+1 first laying **among birds classified as nonbreeders in season t**, but body mass/sex/age are selection-biased and the 2019 paper already examined broad breeder-vs-nonbreeder condition; novelty and ethics require original authors' involvement. We MUST check original methods before proposing new analyses.

**Verdict:** Already published source confirms the exact SAME-SEASON individual tag↔breeder status link is feasible; obtaining and validating extended 2006–2018 individual trajectories remains a **publisher-mediated/source-owner-dependent gate**, not a solved analysis. No 2026 penguin first-breeding effect or causal Antarctic island-law is identified.

Files: `contracts/BECHERVAISE_2019_TAG_NEST_PRIOR_ART_AND_ACCESS_V21.json`, `scripts/simulate_bechervaise_tag_to_egg_denominator_v21.py`, `tests/test_bechervaise_tag_to_egg_denominator_v21.py`, dedicated workflow. Ecology manuscript PR189 and USAP PR142 untouched.
