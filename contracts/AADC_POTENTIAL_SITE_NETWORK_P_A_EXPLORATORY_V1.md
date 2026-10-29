# AADC site-option network exploratory biological association v1 (2026-10-25)

## Fixed question and novelty boundary

After the strict AADC×SCAR site crosswalk **failed** for both bird programmes (6 and 11 sites; zero jointly supported spatial blocks), a different independent spatial predictor was derived from the original 2025 AADC potential-geographic-site frame alone (7,785 unique mapped points). The 10-km candidate-site-neighbor count is not obtained from bird outcomes, but **the AADC P/A biology was already viewed in earlier V14**: the next analysis is unambiguously **exploratory**, not confirmatory or a second independent replication.

Question: **does local density of mapped potential reproductive geographic sites add geographically held-out information about observed breeding P/A after geographic location, survey, nominal site-area/island class and species are accounted for?**

The source 2025 map cannot be treated as a historically fixed count of physically accessible reproductive sites for 1980–2020. It may encode changing survey map density and reporting effort. The analysis provides only a conditional spatial association/forecast diagnostic, never a causal island-water barrier or species interaction effect.

## Source and sample

- Original five AADC XLS/XLSX workbooks and 2025 original geog_site_id, exact SHA pinned in prior V13.
- Original survey observations: explicit P=1 and A=0 with correct published occurrence certainty category and exact original certainty join; NR excluded entirely.
- Duplicate site × species × season observations excluded as groups, not selected by convenient P/A label; accepted austral breeding-season start 1980–2020.
- Separate biological source programmes: original Adélie penguin **ADP** and original seven flying bird codes **SGP/SK/AP/CP/SF/SP/WSP**. Programmes are NOT merged as same-day surveys; compare out-of-region generality only descriptively.
- Only geographic sites within frozen 250-km EPSG:3031 grid blocks with >=5 eligible source geographic site IDs are eligible to score, with >=3 blocks per programme and >=50 original survey rows. Otherwise STOP for that programme.
- Site species histories rather than observation rows are the unit for analysis weights (each history weights to one, splitting across repeat years), nested inside 250-km blocks.

## Models and guardrails

- Base **B0**: original geography (latitude, longitude phase), survey season, original author site-class island/continent, original reported site area, original station-distance/unknown indicator, survey vantage, original expert-validation flags, species indicators for flying programme, and whether the site ID existed in the earlier 2021 spatial reference. Fixed regularized logistic fit C=0.3. Training-fold-only feature centering, scaling and missing-value imputation.
- Option **B1**: B0 + log1p(other original *potential geographic-site centroids* within **10 km**), computed from all 7,785 candidate points without biological response.
- The geography-only 2 km and 50 km neighbor counts are **descriptive sensitivities**, not replacement for the 10 km primary B1 result after inspecting gains.
- For each programme, leave **entire 250-km geographic blocks** out; report equal-block site-history-weighted Brier and secondary log loss, plus block-by-block gain from B0 to B1.
- B1 ecological support requires positive average held-out Brier improvement AND improvements in >=2/3 of eligible geographic blocks. Even if so, the result is *exploratory* and limited to the publisher mapped candidate-site sampling frame. Negative models are not retuned, rescued by alternate radii, or called evidence that actual island patch density has no role.

Do not claim direct competition, Allee effects, recruitment, ocean versus ice isolation, same original island, causation, completeness of all possible nesting sites, or an independent external prospective validation.

Revisit confirmation only with independently mapped historical potential sites or prospective repeated field detection at calibrated visit/land units. Preserve old frozen Paper2, Ecology and failed V14 outcomes unchanged.
