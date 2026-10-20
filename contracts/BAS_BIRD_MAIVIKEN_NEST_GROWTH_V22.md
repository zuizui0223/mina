# V22 — Test shared annual Gentoo nest-count forcing across an offshore island boundary

**Frozen 2026-10-20 BEFORE any numerical colony nesting count from Bird Island or Maiviken original source files is opened.** This is an independent physical-island/main-island comparison (both South Georgia regional nesting systems), NOT a general Antarctic area law or an ad-hoc rescue of V20.

Publisher original source and exact SHA256:
- BAS historical Bird Island gentoo v1 CSV, https://doi.org/10.5285/c8d5a7a4-e19b-497f-b7ae-56f9a2b15a56, SHA256 b1abc3c3adacee3f277d481217aabe4206c7b592a81f1f0eb1a0ec20a64450d3, 252 original colony rows, with Season absent but Date nests counted + Colony + Number of nests.
- BAS Maiviken colony on main South Georgia island, https://doi.org/10.5285/1fd5bc8a-96b5-4f53-aa15-33e5330e7705, SHA256 8eef8ba06b0f1e666041be38415cfcc70d16cdb07e72ca6db805d8b70631dc85, 12 original annual rows, Season, Date of nest count, Number of incubating nests.

V21 publisher header/schema audit finished before choosing this analysis. Both are **stage-aligned original incubating/occupied nest counts**, but not identical breeding-pair enumeration or colony size; biological estimates will be within-source *log(1+n)* changes only. Bird Island original historical v1 is NOT the updated 2026 v2 even if the publisher states earlier rows unchanged.

## Competing predictions and identification
- Shared regional marine forcing predicts *temporally aligned* interannual nests change between neighboring Bird Island colonies and Maiviken main-island nesting grounds.
- Island-level terrestrial colony-organization/access buffering predicts distinct change patterns across this physical island boundary, possibly despite near-shared regional marine forcing.
- Observation effort, redefinition of colony boundaries, breeding-stage/date shifts, unequal sampling areas, species age structure and local predators remain alternative explanations. This is *one island-main-island contrast*, not replicated quasi-experimental proof of a process.

## Cohort eligibility fixed now
1. Read exact two official public CSVs and require V21-pinned SHA256 match. Reject untrusted redirects, HTML, and any year/source mutation.
2. Bird records: require original Species explicitly naming gentoo (case-insensitive contains 'gentoo' or exact 'Pygoscelis papua'), nonblank literal Colony, exact recorded Date nests counted parseable as UK day-first DD/MM/YYYY, ISO YYYY-MM-DD, long English dates DD Mon YYYY, or YYYY/MM/DD; assign breeding season by austral July–June calendar, not by arbitrary count row. Exclude entire duplicate (Colony, year) groups without cherry-picking highest or earliest count. Do not count multiple colonies as independent physical islands.
3. Maiviken: original Season must be a consecutive YYYY/YY, YYYY/YYYY, YYYY-YY or YYYY-YYYY code, or bare YYYY, with start year 2009–2019; Date of nest count must agree with the season as July–June. Exclude entire duplicate season groups. Unknown missing year/date is never 0.
4. Freeze candidate common years to 2009–2019 (both sources expected to have coverage) and require median Bird colony nest-count phenological day within **30 days** of Maiviken nest-count day for each considered common year. No post-outcome adjustment of this radius.
5. Eligibility determined using source IDs, dates, duplicate/season logic alone, BEFORE parsing/counting Number of nests or Number of incubating nests. A Bird year requires >=3 distinct nonduplicate original colony IDs and one strict Maiviken source annual record. Minimum >=8 same-year meta eligible seasons and >=6 strictly consecutive annual growth windows, each with >=3 Bird colonies matched across two years. Otherwise hard STOP before any animal count magnitudes are read.
6. Once this passes, parse nonnegative finite numeric nest count values from only pre-eligible cohort; literal 0 remains a recorded zero, missing/textual NA remains unknown (never zero). Require >=8 numeric-valid common years and >=6 numeric-valid adjacent windows with >=3 Bird colonies measured in both years, or hold without fitting. Exclude invalid complete site×year input rather than filling values.
7. Single primary descriptive endpoint: Pearson r between Maiviken annual log1p nest changes and equally-colony-weighted mean Bird Island matched-colony annual log1p nest changes, over fixed eligible adjacent-year windows; report n windows, n Bird colonies, Bird colony ID roster, leave-one-year-out r min/max, positive/negative sign concordance (and denominator excluding genuine zeros). No p-value, no adjusted threshold, no prospectively causal language.
8. One frozen check for within-Bird Island site heterogeneity: median of all within-island pairwise colony growth r values supported by >=6 original years of joint annual change. These are nested, highly dependent colonies and cannot be treated as independent replicate islands or tests. Do not select favorable colony pairs after viewing effects.
9. A sensitivity to survey-stage timing (≤30 day only) is already imposed. Do not tune the date window, exclude individual outliers, change taxon/area, or substitute external literature digitizations once effects are visible. Even a positive within-region r does not prove shared krill/wind, competition, local demographic rescue or boundary-specific causation.
10. Original V20 NOAA nearby r=0.635 is an outside-programme **descriptive comparator**, not a calibrated null because physical years, sites and census methods differ. The correct next mechanistic step would independently model temperature/wind/sea-ice/access *before* nest counts with more island-mainland matched pairs.

Outputs: SHA-pinned result JSON plus source-stage QA, no raw data mirrored to Git. Frozen Ecology PR189 remains unchanged. No false extrapolation to 'mainland Antarctica' from South Georgia main island.

## Source-date parser diagnostic amendment before opening count magnitudes

The original V22 strict run downloaded both SHA-verified sources but matched zero metadata years because no site date or main-island original time label parsed. Treat this as a **date format/schema issue**, not scientific evidence of insufficient ecological samples. Log ONLY bounded literal publisher date/season labels and parse counts before any nesting count values. Do not alter frozen cohort years, 30-day timing, colony count or any ecological interpretation threshold. The mismatch must be diagnosed before source eligibility can be interpreted.

### Original date-format correction — not model tuning

The metadata-only test revealed original BAS field dates use literal DD-Mon-YY strings, e.g. 20-Oct-19 (Bird Island) and 11-Nov-08 (Maiviken), including Bird Island 1981 records. Before opening any original nesting count magnitudes, enable exactly the Python date format %d-%b-%y in the otherwise unchanged source calendar parser; the 1981–2019 range is not ambiguous with Python's fixed 1969–2068 parsing pivot. Retain 2009–2019 fixed seasons, 30-day stage match, colony and regional criteria. The earlier zero support was a parser bug, NOT a biological finding.
