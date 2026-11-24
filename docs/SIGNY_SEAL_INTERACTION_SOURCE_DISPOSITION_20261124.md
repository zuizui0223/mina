# Signy seal–penguin interaction: final source gate and next data request (2026-11-24)

## Decision

V1 remains FROZEN_SUPPORT_GATE_BLOCKED; D1 remains D1_BLOCKED; D2 is closed as SOURCE_ALGORITHM_TEMPORAL_LEAKAGE, not as a null biological result. No joint numeric outcome has been opened, no coefficients fitted. Do not broaden the ice-onset range, drop 2013, reinterpret the date origin, or choose another covariate on these data to rescue D2.

## Independent author-source audit

Actions run 45375247635; artifact 14910972577; downloaded ZIP SHA256 8e52802fe383b768bd12fa8b20d3a130b78f172e480a64925ac87417d2fbf189 matches Actions. BAS original CSV SHA256 b04bbb3bc593c67c070b18497acb6f96d52cbed6914952d814741c30206b5835. Version-specific source DOI 10.5281/zenodo.15544182. All five files verified against published MD5. Direct local comparison: all 43 BAS numerical rows are identical in order and all 10 fields to the author CSV (no explicit year column in the latter); author CSV SHA256 9905ffae6d10f769f7842142a64faeed9dd5aed107569ed83b1f93c5162408a5.

* getDay.R line 8 documents 1 as January 1; its reverse conversion uses a day-of-year matrix. The March 15 passage in the BAS metadata corresponds to the cited PAL LTER method reproduced as a historical comment in ice_variables_Signy.r line 223, not the actual Signy calendar implementation.
* iceGam.R lines 46–48 fit a GAM using the entire available series; line 62 defines the maximum day using observed and fitted maxima. Lines 65–66 assign onset 1 when all observations up to that maximum exceed the threshold. Thus 2013's onset 1 is algorithmically plausible, but is not proof that the first five consecutive days were actually observed above threshold. The input record has advance=1, retreat=388, duration=388, persistence=99. Lines 71–83 select advance candidates using full-series inflections or the maximum day. Lines 28–29 test three spaced observations at offsets 0,2,4, not five separate consecutive daily observations. These facts invalidate the D2 assumption that onset+4 is ascertainable in real time. D2 will not be fit using a different retrospective interpretation.
* ice_variables_Signy.r line 48 removes missing observations; icevars.R line 30 sets days absent from the retained input day list to zero. This is the authors' reconstruction convention, not independent proof that arbitrary missing observations in the attempted D1 downloads represent open water. Do not reopen D1 by filling missing values.
* D1 NOAA PSL transport pilot also returned HTTP 503. A new verified daily ice source, not further retries of the same source, is needed for a strict antecedent exposure.

## Timing-only feasibility for new daily seal data

Source: schema_review.json in the above verified artifact; dates only, no outcome magnitudes. Recomputed locally for the frozen 17 D1 common seasons. Use earliest recorded chick count among all valid source labels per species/year (conservative); all original dates in these years fall within:

| Species | Earliest and latest recorded chick dates (month/day) | Seasons with earliest count after Jan 1 | Seasons with earliest count on or after Jan 15 (14 preceding January days possible) |
|---|---|---:|---:|
| Adelie | Dec 6–Dec 29 | 0/17 | 0/17 |
| Chinstrap | Jan 7–Jan 27 | 17/17 | 15/17 |
| Gentoo | Dec 14–Jan 2 | 1/17 | 0/17 |

This is measurement-stage timing, not a quantified difference in arrival or feeding competition. Daily base counts (Jan–Mar since 1992, per BAS portal https://signy.data.bas.ac.uk/f?p=282%3A7%3A6999514514252%3A%3A%3A%3A%3A) might support a timing-aware chinstrap analysis; actual daily data coverage is unverified. January-only records cannot supply prior exposure for most Adelie/Gentoo endpoints. Request Nov–Mar where available. Local base counts are not equivalent to whole-island abundance or marine prey use. A cross-species competition claim additionally needs overlapping foraging windows, prey information, consistent response stage, and observation effort.

No further ecological model is authorized by this source diagnosis alone. Existing frozen papers unchanged. Next gate: obtain daily records and observation protocol, audit support before defining estimands; if only Jan–Mar is available, do not claim a common three-species prior-exposure comparison.

## Draft data request (not submitted)

To UK Polar Data Centre / Signy monitoring team, via https://data.bas.ac.uk/request.php?id=GB%2FNERC%2FBAS%2FPDC%2F02026

Subject: Request for timing-resolved seal monitoring records at Signy Island

Dear Signy monitoring team,

I am investigating how seasonal marine predator presence and penguin breeding-stage timing vary at Signy Island. I have accessed the public annual seal census (DOI 10.5285/8e910ac8-6f52-4548-bbcb-78474b559294), seasonal ice and penguin breeding data. Your Signy portal describes daily counts of fur, elephant and Weddell seals around the base from January to March since 1992. Are these daily data available for research, ideally for the 1992/93–2023/24 seasons and including November–December observations or first-arrival dates where available?

If possible, I would appreciate dated records, survey area identifiers or footprints, species counts, observation effort, explicit zero versus not-surveyed flags, and any changes in methodology or daily coverage. These details would allow us to distinguish predator presence before the chick-count dates from the later February census. I would also welcome guidance on access conditions, citation and potential collaboration. We would not interpret base counts as island-wide population totals.

Thank you for your time and guidance.

Best regards
