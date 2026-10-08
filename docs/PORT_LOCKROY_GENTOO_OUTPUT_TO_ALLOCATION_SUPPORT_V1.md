# Port Lockroy Gentoo ratio-free mechanism route: support FAIL

**Status:** terminal support failure under the frozen Port Lockroy contract. No mechanism effect was opened.

## What is structurally available

The provider dataset contains ten stable named sub-colonies across 1996/97–2019/20:

- Anemometer Tower
- Base
- Boatshed
- Control 1–4
- Mast
- Nissen
- Screen

The schema contains:

- `TOTAL_NO_PAIRS` — breeding-pair count;
- `NO_CHICKS` — sub-colony chick count;
- `NO_FLEDGLINGS` — later fledgling/pre-fledging count field.

BAS metadata distinguishes two chick-count stages: an earlier chick count after hatching and a later crèche count before fledging.

## Frozen primary endpoint is not supported

The contract explicitly required the **late / crèche chick count** at each fixed sub-colony.

It also explicitly stated:

> if the file does not supply the late/crèche endpoint for the fixed roster, record SUPPORT FAIL rather than switching to the earlier hatch/chick endpoint.

Observed structure:

- all ten sub-colonies have pair + earlier `NO_CHICKS` support in 17 seasons;
- `NO_FLEDGLINGS` is populated in only 24 rows in the entire file;
- those rows occur almost entirely at Boatshed (23) plus one Mast row;
- **zero seasons** contain a late/fledgling value for all ten fixed sub-colonies.

Therefore there cannot be the required >=12 eligible transitions.

## Decision

> **SUPPORT FAIL — frozen late/crèche endpoint unavailable at sub-colony resolution.**

No `Q_it`, allocation beta, or permutation result is calculated.

The earlier `NO_CHICKS` field is not substituted post-support.

## Why this matters

The Bird Island mechanism signal remains statistically interesting but semantically/mechanically qualified.

Port Lockroy was intended as an independent denominator-safer confirmation using a specifically frozen late chick endpoint.

Because that endpoint is unavailable at the required spatial resolution, this route contributes **no confirming or falsifying biological effect**.

It is a data-support failure, not evidence against the hypothesis.

## Manuscript consequence

Do not claim the Bird mechanism has been independently replicated.

The main paper remains supported by:

- Ross disturbance/rebound allocation;
- Bird prospective aggregate/spatial sign test;
- global Emperor prospective decline test.

The question of what prospectively predicts the contrast mode remains open.
