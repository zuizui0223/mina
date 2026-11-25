# Syowa monitoring original-data availability and crosswalk, 2026-11-25

Current objective: independent additional breeding-nest series for the existing historical-size/climate comparison. No re-fit and no changed eligibility.

## Sources
- NIPR AMB1001 official ten sites: https://www.nipr.ac.jp/antarctic/science-plan10/kihon-biology01.html
- Long-term population and nest data catalogue: https://scidbase.nipr.ac.jp/modules/metadata/index.php?content_id=167 (annual records since 1960, contact atak@nipr.ac.jp). Legacy linked site returned 404 in current check: https://polaris.nipr.ac.jp/~penguin/oogataHP/workAs/peng_s0.htm . This establishes that route is currently inaccessible, not that all original data are unavailable.
- 2025 data catalogue: https://ads.nipr.ac.jp/data/meta/A20260323-004 (data download request; CC BY-SA 4.0, separate PDF download; single season, not historical time series).
- CEMP lists Syowa as a Japanese breeding-population monitoring site, https://www.ccamlr.org/en/science/cemp-sites ; access/use policy requires attention to owner rights and request route. No unrestricted full Syowa longitudinal download located. No access request submitted and no contact made.
- Watanuki & Naito 1992, Counting Adelie Penguins at Colonies: Seasonal and Annual Changes, https://nipr.repo.nii.ac.jp/record/8770/files/KJ00000140058.pdf . Original article text distinguishes Nov 10–20 adult maximum from Dec 1–10 plateau; relation to nests depends on timing. Screenshot retrieval failed (cache miss); no figure/table values digitized. Do not equate adult counts with nests by default or use published conversion for unknown dates.
- The long-term trend in this region has already been reported in Takahashi 2021 symposium, https://nipr.repo.nii.ac.jp/record/16776/files/PS12-OB.pdf ; no novelty claim for first regional ice association.

## Executed local audit
Verified MAPPPD v5 source ZIP artifact 14934334550 and marine source ZIP 13829236358 against SHA256 pins and CRC; original CSV rows 5487 and 16464 respectively. Ran syowa_source_gate.py using ten named official coordinates as explicit candidate crosswalks. Local script SHA256 db57e4fe9b2c7a68c5b03b2917ea59e75470bcefb574505b0c22d5c5d4ac6098; local result JSON SHA256 f943c94bb2aef2306fc188d7975555b6cff299ab68b6b282fcb1677543f886f2. Candidate name/coordinates not verified equal colony footprint or survey method. Official ten sites maximum pairwise distance 53.212545 km. Do not claim ten independent regions or marine exposures.

| Official site | MAPPPD ID | Coordinate gap km | Adults | Chicks | Nests | Marine years |
|---|---|---:|---:|---:|---:|---:|
| Mame | MAME | 0.037867 | 31 | 1 | 0 | 0 |
| Ongulkalven | ONGU | 0.011148 | 38 | 3 | 0 | 0 |
| Benten | BENT | 0.349383 | 17 | 0 | 0 | 0 |
| Rumpa | RUMP | 0.168673 | 28 | 2 | 0 | 0 |
| Sigaren | SIGA | 0.114030 | 4 | 0 | 0 | 0 |
| Mizukuguri | MIZU | 0.078675 | 23 | 0 | 0 | 0 |
| Hukuro | HUKU | 0.037249 | 23 | 5 | 4 | 28 |
| Ytrehovdeholmen | YTRE | 0.920004 | 18 | 0 | 0 | 0 |
| Torinosu | TORI | 1.153825 | 19 | 1 | 0 | 0 |
| Nokkelholmane | NOKK | 0.228212 | 15 | 0 | 1 | 28 |

Total 233 records (216 adults, 12 chicks, 5 nests). All ten adult series end by 2004. Within frozen historical 1993–2010 and evaluation 2011–2020 windows, adults 106 and 0 records; nests 2 and 3 records (evaluation HUKU alone). Kato 2006 accounts for 159 adults; month absent for 157. Only 29 adult rows in all ten sites have explicit Nov 10–20 dates, all pre-1993. No meaningful adult proxy rescue, no eligible historical-size series. Previous larger rectangle contained 244 observations and four marine-matched locations; exact official roster has only two (HUKU and NOKK), not four. Eight require original marine extraction if usable colony-level data acquired. No nearest-grid substitution; same geometry and calendar requirements as prior model, source wet-cell reuse explicit.

## Decision
SOURCE_REQUEST_REQUIRED_NO_NEW_OUTCOME_PANEL. Stop further retries of same legacy link and do not fit ecological outcome models. Prepared unsent provider inquiry in JARE_DATA_INQUIRY_DRAFT_JA.md. User/authorized researcher can request full original series; access conditions and author/source attribution must be followed. Once received, check occupied/incubating nest definition, dates, coverage, parent/subcolony changes, replicate counts, missing versus observed zeros and MAPPPD event provenance before freezing an independent comparison. Main and frozen manuscripts unchanged.