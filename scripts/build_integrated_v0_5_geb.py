#!/usr/bin/env python3
"""Build the GEB-oriented integrated v0.5 manuscript from frozen v0.4.

This is a prose-only transformation. It does not recompute or alter any
scientific result, figure datum, inferential rule, or source receipt.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path


STRUCTURED_ABSTRACT = r"""## Abstract

**Aim.** To test whether demographic information measurable within breeding landscapes remains informative when compressed into static descriptors at broader scales.

**Location.** Palmer Archipelago, western Antarctic Peninsula, and breeding sites across Antarctica.

**Time period.** Palmer: 1991–2017. Antarctic-wide: 1980–2025.

**Major taxa studied.** Adélie penguin (*Pygoscelis adeliae*) locally; Adélie, chinstrap (*P. antarcticus*) and gentoo penguins (*P. papua*) across Antarctica.

**Methods.** We combined Palmer colony censuses, chick counts and nest histories with Antarctic-wide abundance data. We tested whether late-season colony state predicted later redistribution using denominator-separated lags and permutations, and whether an independent nest endpoint replicated the association. Separately, we preregistered a three-species test of breeding-space amount × habitat-complex heterogeneity.

**Results.** Palmer breeders concentrated into fewer colony-code groups. Colony state predicted redistribution at the denominator-separated lag 2 (β = 0.0409, *p* = 0.00327), remained positive at lag 3 and faded by lags 4–5; the predeclared 4–5-year recruitment-echo prediction was unsupported. Mean chicks reaching crèche per monitored nest did not replicate the association (β = 0.0296, *p* = 0.232). Across 104 predictor-complete site × species units, area × heterogeneity estimates were negative in all three species, but the preregistered cross-species test was non-confirmatory (median γ_AH = −0.318, *p* = 0.0947); radius variation did not establish biological scale dependence.

**Main conclusions.** A specific late-season colony-wide state carries short-lived local demographic history but is not interchangeable with generic nest productivity. Static island descriptors did not provide a confirmed scale-invariant transfer rule. Ecological information can therefore be valid locally without remaining transferable after spatial aggregation.

**Keywords:** Adélie penguin; Antarctic Peninsula; breeding islands; colony state; demographic redistribution; history dependence; island ecology; macroecology; spatial scale
"""

INTRODUCTION = r"""## Introduction

Island ecology seeks persistent geographic attributes that make ecological outcomes predictable. Area, isolation and environmental heterogeneity can structure richness and persistence because finite space constrains the amount and arrangement of usable habitat [@kadmon2007; @allouche2012]. Yet the realized value of a breeding island can also depend on recent occupancy, density and biological history. This distinction is especially important for seabirds: reproduction is tied to discrete terrestrial sites while most trophic acquisition occurs at sea, weakening any simple equivalence between terrestrial landscape structure and demographic carrying capacity [@obrist2020; @mulder2011; @grant2022].

We therefore distinguish **static information**—persistent features such as ice-free area, topography and habitat-complex diversity—from **dynamic information**—the current distribution and recent biological state of breeders. These forms of information need not be interchangeable. Snow, terrain and geomorphology can make some breeding locations persistently more suitable, whereas occupancy and recent biological history can update how the available landscape is used from year to year.

Performance-based breeding-habitat selection is not itself a new hypothesis. In Black-legged Kittiwakes, previous local reproductive success predicted breeder redistribution, and experimental manipulation of neighbouring success altered attendance, site fidelity and recruitment [@danchin1998; @boulinier2008]. In Adélie penguins, a 24-year study at Pointe Géologie found a strong association between colony breeding success and one-year-lagged growth and interpreted it as coherent with public-information use [@meheust2024]. A positive one-year performance–growth association is therefore neither mechanistically diagnostic nor novel on its own. The unresolved questions are whether colony state contains information beyond shared-denominator structure and persistent colony differences, how long that information persists, and whether it is reproduced by an independent biological metric.

The Palmer Archipelago offers a local test because neighbouring Adélie populations share much of their regional context while having undergone large long-term declines [@fraser2013; @pickett2018; @cimino2019]. Independent work also shows that snow, topography and geomorphology structure subcolony persistence [@cimino2025]. We first asked whether decline involved within-island redistribution beyond proportional thinning and whether a relative late-season colony state predicted subsequent redistribution after shared annual change, prior abundance and persistent colony identity were controlled. We treated a denominator-separated lag as the primary bias-resistant endpoint, examined the full temporal lag profile and tested the same biological interpretation with independent monitored-nest data.

We then asked a different, broader question: can local demographic organization be represented by static landscape descriptors that transfer among populations and species? Using Antarctic Penguin Biogeography Project data [@checastaldo2023], we preregistered tests of whether breeding-space amount and habitat-option heterogeneity predicted site-specific coupling to demographic variation shared within Adélie, chinstrap and gentoo penguins.

The two parts are inferentially independent and are **not a head-to-head predictive model comparison**. They use different responses, spatial grains and species panels, so coefficients, explained variance and predictive performance are not directly comparable. Instead, each part tests its own transfer claim against a frozen null: Part I asks whether local state contains temporal information; Part II asks whether static island architecture yields a confirmed, scale-invariant Antarctic-wide response rule. The synthesis concerns what ecological information survives a change in scale, not whether state “beats” place.
"""

METHODS = r"""## Materials and Methods

### Part I: Palmer local-history test

#### Census, concentration and colony state

We used annual breeding-pair censuses from five Adélie breeding islands monitored by the Palmer Station Antarctica LTER: Christine, Cormorant, Humble, Litchfield and Torgersen. The synchronized panel spans 1991–2017. Island trajectories were analysed as log(1 + abundance) and standardized to describe their shared temporal component; year and island terms were descriptive rather than identified environmental mechanisms.

Within-island redistribution was quantified with effective colony number,
\[
N_{\mathrm{eff}}=1/\sum_j p_j^2,
\]
where \(p_j\) is the fraction of island breeding pairs in colony code \(j\). The concentration test was restricted to Cormorant, Humble and Litchfield, whose reported colony-code rosters were unchanged across the synchronized period. Observed temporal slopes of \(N_{\mathrm{eff}}\) were compared with 100,000 fixed-composition simulations that preserved annual island totals but imposed proportional thinning, with Poisson and prespecified Gamma–Poisson count-error models. The null therefore removed temporal change in latent composition while preserving the decline itself.

For each eligible island-season, we combined the independent November adult census with January chick counts assigned to breeding season by the frozen PALYYZZ identifier. Expected chicks under proportional production were
\[
E_{i,t}=C_tN_{i,t}/N_t,
\]
and a Pearson-type residual was standardized within island-season to define the relative late-season colony state \(S_{i,t}\). Adjacent adult-census growth was
\[
G_{i,u}=\log(1+N_{i,u+1})-\log(1+N_{i,u}),
\]
then centred within each island-transition to define relative redistribution \(R_{i,u}\). Lag-\(k\) models related \(S_{i,t}\) to \(R_{i,t+k-1}\), controlling standardized prior colony size and island × colony-code fixed effects.

Lag 1 shares the predictor-year adult count between state construction and the \(t\rightarrow t+1\) transition. We therefore treated lag 2—state at \(t\) predicting redistribution during \(t+1\rightarrow t+2\)—as the primary bias-resistant endpoint. Inference used 100,000 within-island-season permutations of \(S_{i,t}\), preserving outcomes, missingness and controls. We also froze lags 1–5 and a delayed recruitment contrast,
\[
C_{\mathrm{recruit}}=(\beta_4+\beta_5)/2-(\beta_2+\beta_3)/2,
\]
with the prediction \(C_{\mathrm{recruit}}>0\).

The lag analysis underwent one documented provenance repair: calendar-date season assignment conflicted with an earlier outcome-blind PALYYZZ season contract. Only the key was repaired; lags, model, metrics and decision rules were unchanged. Because coefficients had already been exposed, the repaired result is treated as **fixed-specification validation**, not fully outcome-blind preregistration.

#### State persistence and independent validation

We tested colony-state memory at lags 1–3 with colony fixed effects and within-season permutations. A non-causal bridge diagnostic then included both \(S_{i,t}\) and \(S_{i,t+1}\) when predicting redistribution during \(t+1\rightarrow t+2\); because \(S_{i,t+1}\) is post-\(t\), this is not causal mediation.

For independent biological validation we used Palmer LTER REPRO nest histories. The frozen primary endpoint was mean chicks reaching crèche per monitored nest, requiring at least five nests per colony-season, standardized within island-season and tested against next-year relative redistribution with the same prior-size and colony-identity controls. Historical zero and recent blank encodings of absent crèche dates were harmonized by a source-semantic repair frozen before fitting: only positive numeric crèche dates counted as successful events. A binary any-crèche metric was sensitivity-only and could not rescue a failed primary endpoint. A same-panel comparison of REPRO and colony-wide state was post-result diagnostic only.

Published Torgersen mapping was used as phenomenon-level spatial triangulation of concentration and habitat persistence [@cimino2025], not as a merged response dataset.

### Part II: Antarctic-wide transferability test

#### Analysis frame and predictors

We used a pinned MAPPPD/APBP abundance snapshot. Predeclared temporal-coverage rules produced 107 bridged *Pygoscelis* site × species units and 2,100 nest-count records for 1980–2025; after joining frozen terrestrial predictors, 104 units were predictor-complete (41 Adélie, 34 chinstrap and 29 gentoo).

At the primary 2 km radius, breeding-space amount was \(A=z[\log(1+\mathrm{ice\text{-}free\ area})]\) and habitat-option heterogeneity was \(H=z(\mathrm{Tier\ 2\ Habitat\ Complex\ richness})\). The focal predictor was \(A\times H\). Terrain relief and alternative spatial supports were prespecified secondary analyses and could not replace the frozen primary test.

#### Demographic model and inference

Direct counts were the observation reference. Image counts received one shared calibrated offset, and observation precision used frozen accuracy groups. Before outcome magnitudes were opened, candidate estimators had to recover prespecified null, simple-buffering and interaction scenarios under the real temporal and observation schedules. The retained model used one species-wide latent annual forcing per species, spatial-block loading adjustments, residual site loading variation and propagated endpoint observation variance.

Site coupling was parameterized as
\[
\lambda_i=1+\alpha_{b(i)}+\gamma_AA_i+\gamma_HH_i+\gamma_{AH}A_iH_i+b_i,
\]
with traits centred within the frozen spatial block. The primary paper-level statistic was the median \(\gamma_{AH}\) across the three species. In 9,999 permutations, complete \((A,H,A\times H)\) tuples were reassigned among sites within species × spatial block and the complete model was re-estimated; the one-sided alternative was a more negative median. Species-specific tests used the same directional rule with Holm adjustment.

Prespecified secondary analyses included A-only breeding-space buffering, exact-date and ±14-day observation-calibration refits, 1 km and 5 km spatial supports, and 2 km Shannon diversity. Because the interaction changed sign across radii, a joint 9,999-permutation diagnostic tested whether the observed 2 km negative/5 km positive switch plus its contrast was unusually large; scale-dependence language required \(p\leq0.05\). A retrospective operating-characteristic analysis using the unchanged estimator and observation layout quantified what common interaction magnitudes the frozen test could usually detect; it was not an equivalence test. Full estimator-recovery gates, stopped analyses and inferential-status details are provided in the Supporting Information.
"""

DISCUSSION = r"""## Discussion

### Local history and the limits of static transfer

The central result is a cross-scale asymmetry in ecological information. At Palmer, decline included spatial concentration and short-lived history: a dynamically updated late-season colony state predicted subsequent relative redistribution beyond prior abundance and persistent colony identity. Across Antarctica, static breeding-space amount and habitat complexity did not provide a confirmed, scale-invariant rule for coupling to shared demographic forcing. This is an **evidentiary asymmetry rather than an effect-size comparison**. The responses and grains differ; the defensible contrast is that local state passed its frozen information test whereas the macroecological rule did not pass its own transferability test.

This does not imply that state matters while place does not. Palmer studies independently show effects of terrain, snow and geomorphology on subcolony persistence [@cimino2019; @cimino2025]. Persistent physical structure defines the set of usable breeding locations, while recent occupancy and biological state can alter how that landscape is realized. Static landscape summaries can therefore be biologically relevant yet omit the local histories that organize short-term redistribution.

### Relation to performance-based habitat selection

The Palmer association extends rather than discovers performance-associated habitat selection. Observational and experimental kittiwake studies established that previous local reproductive success can alter subsequent breeding decisions [@danchin1998; @boulinier2008], and Méheust et al. reported a one-year-lagged breeding-success–growth association in Adélie penguins [@meheust2024]. Our lag-1 coefficient consequently has little standalone novelty.

The added information is temporal and metric-specific. The association persisted at the denominator-separated lag 2 and at lag 3, but did not strengthen at lags 4–5; the predeclared recruitment-echo contrast was negative. Moreover, mean chicks reaching crèche per monitored nest did not reproduce the primary association. The informative Palmer variable is therefore a **specific late-season colony-wide state**, not a generic productivity measure. It may integrate chick survival, late-season spatial aggregation, density, social conditions, incompletely measured habitat quality and observation processes.

Public-information use remains compatible with this pattern, but so do retention, prospecting and latent environmental persistence. Weak measured state autocorrelation and the positive bridge diagnostic constrain a perfectly persistent measured-state explanation, but the bridge conditions on a post-\(t\) variable and cannot identify causation. Colony counts likewise cannot reveal which individuals carry the history or which cue they perceive. Public information is thus a motivated hypothesis with strong precedent, not the demonstrated mechanism.

### Why local information need not transfer

Penguin breeding islands are externally subsidized systems: terrestrial space is essential for reproduction, while most trophic acquisition occurs at sea. Area and habitat heterogeneity can therefore influence nesting opportunities without acting as simple proxies for energetic carrying capacity. More importantly, static descriptors do not encode which subcolonies were occupied the previous year, how breeders redistributed, or what biological state developed after reproduction. Local explanatory structure can be real without being recoverable from a coarse static map.

The Antarctic-wide interaction illustrates this limit rather than proving absence of landscape effects. All three 2 km point estimates were negative, but the frozen cross-species test was non-confirmatory. The operating-characteristic analysis shows that moderate common effects near the observed magnitude were poorly detectable, whereas very large effects around 0.50–0.55 would usually have been detected. The result therefore constrains a strong general rule more than a moderate one.

Spatial support further limits interpretation. The raw interaction differed among 1, 2 and 5 km and reversed sign between 2 and 5 km, but the joint multi-radius null did not meet the frozen criterion for biological scale dependence. Habitat heterogeneity is plainly not scale-free, yet these data do not establish a particular biological radius.

### A hierarchy of ecological information

The analyses suggest three levels of information: **physical structure**, which constrains where breeding can occur; **dynamic colony state**, which records recent demographic history; and **individual behaviour**, which must carry that history through retention, prospecting, immigration or settlement. Information can be valid at one level without transferring cleanly to another.

The present study resolves the first two levels only partially. Palmer identifies history-dependent redistribution but not its carrier. A 25-year Ross Island mark–recapture analysis shows that Adélie pre-breeders move among colonies more frequently than established breeders [@dugger2026], making prospecting and first settlement a natural future mechanism test, but no Ross movement result is part of the present evidentiary chain.

Important boundaries remain. The Palmer lag-2 analysis is fixed-specification validation after a provenance repair; the bridge is non-causal; colony codes are repeated census units rather than demonstrated one-to-one physical polygons; and the independent REPRO result prevents interpreting the state as generic reproductive success. At the Antarctic scale, landscape variables describe potential surroundings rather than annually occupied footprints, latent forcing is not an identified climate driver, and the primary interaction remains non-confirmatory.

The broader implication is that macroecology should distinguish **local explanatory structure**, **dynamic historical information** and **transferable structure**. A landscape variable can matter locally without becoming a robust cross-population predictor, and a demographic state can be informative locally without surviving aggregation into static descriptors.
"""


def replace_section(text: str, start: str, end: str, replacement: str) -> str:
    pattern = re.compile(
        rf"{re.escape(start)}.*?(?={re.escape(end)})",
        flags=re.S,
    )
    new, n = pattern.subn(replacement.rstrip() + "\\n\\n", text, count=1)
    if n != 1:
        raise RuntimeError(f"failed to replace section {start!r} -> {end!r}")
    return new


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    text = args.source.read_text(encoding="utf-8")
    text = text.replace(
        "**Integrated manuscript draft v0.4 — literature-gap revision**",
        "**Integrated manuscript draft v0.5 — GEB submission revision**\\n\\n**Running title:** Penguin colony history across scales",
        1,
    )
    text = replace_section(text, "## Abstract", "## Introduction", STRUCTURED_ABSTRACT)
    text = replace_section(text, "## Introduction", "## Materials and Methods", INTRODUCTION)
    text = replace_section(text, "## Materials and Methods", "## Results", METHODS)
    text = replace_section(text, "## Discussion", "## Conclusion", DISCUSSION)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
