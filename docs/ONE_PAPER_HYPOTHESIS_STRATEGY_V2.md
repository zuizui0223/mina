# One-paper hypothesis strategy v2 — spatial recovery hysteresis

**Date:** 2026-10-05  
**Status:** prospective strategy; SMP outcomes unopened.

## The single biological hypothesis

> **Population recovery does not retrace spatial collapse in colonial breeders.**

A breeding site that has been abandoned is predicted to require a higher surrounding population state to be recolonized than the state at which that same site was lost.

For the same physical SiteID:

\[
H=A_{\mathrm{recolonize}}-A_{\mathrm{abandon}}.
\]

Primary prediction:

\[
H>0.
\]

## Why this is stronger than the current concentration story

The existing penguin results establish:

1. decline can concentrate breeders beyond proportional thinning;
2. increasing regional networks do not necessarily restore effective breeding-site number.

Those results imply weak spatial reversibility, but they do not directly compare disappearance and later recolonization of the **same place**.

The SMP test does.

By pairing abandonment and recolonization within the same physical SiteID, the test asks whether history changes the population threshold for occupancy while controlling fixed place identity.

## Competing hypotheses

### Reversible site-quality / basin model

For a physically stable site with fixed intrinsic quality, occupancy should be approximately a reversible function of surrounding population state.

Prediction:

\[
H\approx0.
\]

### History-dependent spatial recovery

If occupation itself creates persistence through site fidelity, social information, colony state or another positive feedback, losing occupancy changes the effective state of the site.

Prediction:

\[
H>0.
\]

The estimand is **history dependence**, not a particular social mechanism.

## Four blind gates before the ecological result

### Gate A1 — structural support

Freeze species × MasterSite panels and child SiteID rosters from identifiers, sampling support, methods and missingness only.

### Gate A2 — physical SiteID identity

Require provider/site-history confirmation that retained SiteIDs are stable, mutually exclusive physical breeding Sites without unresolved merges, splits, replacements or boundary changes.

If physical identity cannot be established, stop.

### Gate A3 — zero semantics

Require provider/official confirmation that:

- a direct Count=0 row is a surveyed nil return;
- an absent SiteID × year row is not zero;
- imputed/estimated zeroes are excluded from the primary analysis.

If this cannot be established, stop.

### Gate B — completed vacancy spells

Using only positive / explicit-zero / missing states, freeze completed calendar-consecutive spells:

\[
1\rightarrow0\rightarrow\cdots\rightarrow0\rightarrow1.
\]

Require the prespecified multi-SiteID, multi-MasterSite and multi-species support before count magnitudes are opened.

## Stage C — paired threshold test

For focal SiteID \(j\), define surrounding population size without the focal Site:

\[
N_{-j,t}=\sum_{k\ne j}n_{k,t}.
\]

For the abandonment transition,

\[
A_e=
\frac{
\log(1+N_{-j,t})+
\log(1+N_{-j,t+1})
}{2}.
\]

For later recolonization,

\[
A_c=
\frac{
\log(1+N_{-j,u})+
\log(1+N_{-j,u+1})
}{2}.
\]

Then:

\[
H=A_c-A_e.
\]

Average hierarchically:

spell \(\rightarrow\) SiteID \(\rightarrow\) MasterSite \(\rightarrow\) species,

with species equally weighted.

## Two mandatory inferential checks

### 1. Species sign-flip

Test whether species-level mean \(H\) values are directionally positive.

### 2. Structured trajectory-phase null

Keep the frozen spell roster and transition years fixed.

Within each species × MasterSite contiguous complete-year block, circularly shift the **entire multivariate annual count matrix** by one common lag. This preserves:

- the exact abundance trajectory;
- serial structure up to circular phase;
- cross-site covariance within the panel;
- spell identities and vacancy durations.

It breaks only the alignment between the frozen abandonment/recolonization transitions and the abundance trajectory.

A positive paper-level result requires:

\[
T>0,
\]

\[
p_{\mathrm{sign}}\le0.05,
\]

and

\[
p_{\mathrm{phase}}\le0.05.
\]

## Evidence sequence in one paper if SMP passes

### Part 1 — discovery in Antarctic penguins

Palmer + Signy:
non-proportional concentration during decline.

MAPPPD:
regional effective breeding-site number can remain reduced while abundance increases.

Interpretation:
population recovery need not immediately reconstruct prior spatial organization.

### Part 2 — prospective test in SMP seabirds

The independent test asks whether the same breeding Sites are recolonized only after the surrounding population exceeds its state at prior abandonment.

### One-paper conclusion if all frozen criteria pass

> **Spatial collapse and spatial recovery occur at different population thresholds in colonial breeders.**

or, more plainly:

> **Population recovery does not retrace spatial collapse.**

This would turn the Antarctic penguin anomaly into a prospectively replicated island-ecology process.

### One-paper conclusion if any confirmatory criterion fails

Do not force the synthesis.

Submit the current penguin paper as the bounded Antarctic result and treat SMP as a falsification or non-identification of the proposed generalization.

## What is not the novelty

Do not claim novelty for:

- Allee effects;
- conspecific attraction;
- buffer effects;
- colonization versus recolonization as distinct processes;
- dynamic-landscape theory;
- hysteresis as a theoretical concept.

All are established.

## Candidate novelty

The candidate contribution is narrower:

> **a prospective multi-species, same-site paired test of whether abandonment and later recolonization occur at different surrounding population thresholds, linked to an independently discovered Antarctic spatial-recovery anomaly.**

## Island-ecology framing

Classical patch and island models treat colonization and extinction as transition rates conditioned on place and regional state.

The focal hypothesis is that occupancy history changes the transition threshold itself.

The same physical breeding island can therefore have different demographic thresholds depending on whether it is currently occupied or has already been lost.

## Mechanism boundary

Even a supported result would establish **history-dependent spatial recovery**, not a unique behavioral mechanism.

Same-site pairing controls fixed site quality. The structured phase null calibrates generic temporal alignment. Time-varying habitat deterioration, predators, disturbance and management can still generate part of the asymmetry.

## Stop rule

No new penguin analysis is required.

After SMP magnitudes are opened, do not add:

- alternative SiteID crosswalks;
- low-count vacancy thresholds;
- new lags;
- new abundance transforms;
- environmental covariates;
- species subsets;
- social-trait screens;
- new null models

to rescue the paper-level hypothesis.
