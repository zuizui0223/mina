# SMP trend-symmetry decision table v1

**Date:** 2026-10-05  
**Status:** prospective interpretation contract before receipt of the SMP bulk extract.  
**Branch:** \`research/smp-trend-symmetry-v1\`

## Purpose

This document freezes how the SMP result will update the Antarctic penguin hypothesis.

It does not authorize any new endpoint. The numerical definitions are in:

- \`contracts/SMP_TREND_SYMMETRY_SUPPORT_V1.json\`
- \`contracts/SMP_TREND_BALANCE_GATE_V1.json\`
- \`contracts/SMP_TREND_SYMMETRY_EFFECT_V1.json\`

## Gate outcomes

### Stage A fails

If the structural support gate fails:

> **SMP cannot identify the symmetry question with the requested hierarchy.**

Action:

- stop the SMP trend-symmetry route;
- do not lower component/year/species/MasterSite thresholds;
- do not substitute Plot or another hierarchy after seeing support unless a genuinely new protocol is frozen without concentration outcomes;
- Paper 1 interpretation remains unchanged.

### Stage A passes, Stage B fails

If there are not enough Stage-C-eligible increasing and declining panels, species, MasterSites, or within-species trend variation:

> **The SMP extract is structurally rich but does not identify increase–decline symmetry.**

Action:

- do not open \(E\), \(\gamma\), or \(\Delta\gamma\);
- do not weaken the positive/negative trend balance requirements;
- do not reclassify near-zero trends using a post-hoc cutoff;
- the symmetry question remains unresolved.

## Stage C quantities

For each panel:

\[
\Delta\gamma_i
=
\gamma_i^{obs}
-
\operatorname{median}(\gamma_i^{null}).
\]

Negative values mean excess temporal concentration beyond the exact observed abundance trajectory under fixed component composition.

The macro result has three prespecified summaries:

1. species-balanced overall mean \(\alpha_S\);
2. within-species abundance-trend coupling \(\beta_{\mathrm{within}}\);
3. species-balanced trend-class means \(\mu_-\) and \(\mu_+\).

No single one of these is allowed to replace the others after results are known.

## Confirmatory interpretation table

### A. Directionally persistent concentration

Required:

\[
CI_{95}^{upper}(\mu_-)<0
\]

and

\[
CI_{95}^{upper}(\mu_+)<0.
\]

Interpretation:

> **Excess breeding-space concentration occurs in both declining and increasing seabird systems.**

Allowed program-level update:

> Breeding-space concentration is not specific to population decline and can persist under population growth.

If \(\alpha_S\) is also supported negative, this strengthens the overall cross-species statement.

If \(\beta_{\mathrm{within}}>0\) is also supported, say:

> concentration occurs under both trend directions but is stronger toward more negative abundance trajectories.

Do **not** call this hysteresis. The allowed term is **directionally persistent** or **ratchet-compatible** concentration.

### B. Reversible abundance tracking

Required:

\[
CI_{95}^{upper}(\mu_-)<0
\]

and

\[
CI_{95}^{lower}(\mu_+)>0.
\]

Interpretation:

> **Breeding-space organization contracts during population decline and re-expands during population growth.**

Program-level consequence:

- strengthens an abundance-coupled interpretation;
- MAPPPD increasing-panel concentration is not a transferable macroecological rule;
- Paper 1 remains a decline-associated concentration result.

A supported positive \(\beta_{\mathrm{within}}\) is expected under this outcome but is reported separately.

### C. Decline supported, increase unresolved

Required:

\[
CI_{95}^{upper}(\mu_-)<0
\]

while \(\mu_+\) is neither supported negative nor supported positive.

Interpretation:

> **SMP independently supports concentration during decline but does not resolve what happens during growth.**

Do not write “decline-specific concentration.”

Program-level consequence:

- strengthens Paper 1's decline result;
- leaves the MAPPPD increasing-network boundary unresolved rather than refuted.

### D. Increasing concentration supported, decline unresolved

Required:

\[
CI_{95}^{upper}(\mu_+)<0
\]

while the declining class is unresolved.

Interpretation:

> **The independent data support concentration during growth but do not reproduce the decline contrast.**

This is not a clean confirmation of either existing story.

Action:

- report as unresolved macroecological asymmetry;
- do not invent a new growth-specific mechanism on the same data.

### E. Overall concentration supported but class symmetry unresolved

Required:

\[
CI_{95}^{upper}(\alpha_S)<0
\]

while neither A nor B is satisfied.

Interpretation:

> **Across species, breeding-space organization tends to concentrate through time, but the available trend-class contrast does not identify whether that tendency is symmetric across population growth and decline.**

Do not infer trend independence from a non-significant \(\beta_{\mathrm{within}}\).

### F. Decline coupling supported

Required:

\[
CI_{95}^{lower}(\beta_{\mathrm{within}})>0.
\]

This is an orthogonal modifier, not a replacement for the class result.

Interpretation:

> More negative abundance trends are associated with more negative excess concentration within species.

Possible combinations:

- A + F: directionally persistent concentration, stronger in declining trajectories.
- B + F: reversible abundance tracking with continuous decline coupling.
- C + F: decline-associated concentration supported; growth remains unresolved.
- F alone: continuous coupling exists but class-level biological symmetry remains unresolved.

### G. No confirmatory pattern

If \(\alpha_S\), \(\beta_{\mathrm{within}}\), \(\mu_-\), and \(\mu_+\) do not meet any directional support criterion:

> **SMP does not provide confirmatory evidence for a general concentration–trend relationship under the frozen design.**

Do not search subgroups, traits, lags, trend thresholds, or alternate component definitions as rescue analyses.

## Relationship to MAPPPD

The three increasing MAPPPD panels are hypothesis-generating evidence only.

They predict outcome A more naturally than outcome B, but they are not counted in any SMP p-value, confidence interval, bootstrap, or replication count.

### If SMP supports A

The MAPPPD observation receives independent support.

The program can move from:

> concentration accompanies decline

to:

> concentration can be a directional spatial process that is not reversed by population growth.

### If SMP supports B

The MAPPPD increasing panels remain real observations but are not a transferable macroecological pattern.

### If SMP supports C or G

The regional penguin boundary remains unresolved at general taxonomic scale.

## Relationship to “ratchet” and hysteresis

Cross-system increase/decrease symmetry is not a hysteresis test.

Even outcome A cannot demonstrate that the same population follows a different path during decline and recovery.

A future hysteresis test would require within-system history or experimentally/observationally comparable trajectories that revisit the same abundance states.

Therefore:

- **directionally persistent** = allowed;
- **ratchet-compatible** = allowed with explicit qualification;
- **hysteresis demonstrated** = prohibited.

## Stop rule

After Stage C is opened:

- no new trend cutoff;
- no removal of near-zero trend panels;
- no species subset chosen by result;
- no trait screen;
- no lag search;
- no nonlinear trend taxonomy;
- no alternate \(E\) metric;
- no replacement of species-balanced inference by panel-count-weighted inference.

Any new mechanism or moderator requires a separate independent study.
