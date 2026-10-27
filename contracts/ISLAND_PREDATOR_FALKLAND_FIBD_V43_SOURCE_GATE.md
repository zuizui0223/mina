# V43 SOURCE GATE — Independent Falkland Islands original mammal visit/status database

**2026-10-27 | Scope: public original database acquisition and reproducible data-quality/effort classification ONLY.** UK V40/V41 predator *published-label* SDMs already built and evaluated; UK V42 GBIF island witness gate failed. This V43 is an **out-of-geography independent source** for a future second-archipelago island predator niche study, not a rescue of UK historical predator × seabird H2. The Falkland Islands' predation/rat-isolation relationship was already investigated in Tabak et al. (2015, Journal for Nature Conservation: 158-island rat analysis). **Island area and isolation alone are PRIOR ART**, not a novel finding.

## Original open first-party datasets: Falkland Islands Government FIBDv8 20140601

Public CKAN catalogue, Falkland Islands Data Portal https://dataportal.saeri.org/ :
- \`fibdv8-20140601-invasives\` — per-island *invasive mammals* observations/status (1765–2013, reliable field campaigns principally 1997–2013).
- \`fibdv8-20140601-locations\` — island identity, hectares, elevation and WGS84 original point location.
- \`fibdv8-20140601-visits\` — survey visit date / observer / method (must distinguish in-field and **desktop-assessment** "visits"; mere visit ≠ targeted mammal non-detection).
- \`fibdv8-20140601-eradication\` — dated alien species removal operations (may be absent from catalogue; record source HOLD).
- \`fibdv8-20140601-birds\` — original island bird observations and nesting labels; eligibility is source-only, not seabird biology fitted until independent plan.

Scientific owner Falkland Islands Government; catalogue licence CC-BY-SA-4.0 (verify every dataset). Original sources remain at publisher; download openly marked public XLS (<4 MB each) and record binary SHA256. Do NOT commit original XLS datasets, personal observer identities, sensitive colony coordinates, original protected locations, or individual source rows. No external contacts or credentials. Use public unauthenticated HTTPS only (the catalogue gives an http: origin URL which may be *upgraded* to https for the same explicitly verified host). Deny redirects to third-party domains or authentication pages.

## Essential distinction in rat absence semantics

Official FIG metadata explicitly warns that **Rattus norvegicus is the only invasive mammal with a listed status for EVERY island, including UNSURVEYED ones**; where unsurveyed, records reflect knowledge/desktop assessment of likely absence/presence. Other introduced mammals lack complete negative observations. Therefore a published "absence" on a surveyed island is NOT automatically a true negative unless original *field* visit identifies a targeted systematic rat search with protocol/time/effort and known absence outcome. The geographical RAT baseline dataset may be treated as source-category association only unless genuinely surveyed negatives can be identified with audited field methods. No species zero imputation.

## Intake and source-only pre-outcome structural stages

1. CKAN \`/api/3/action/package_show\` for each exact slug (no custom dataset discovery chosen by ecological effect). Validate that catalogue is public (\`private=false\`, resource \`restricted.level=public\` where present, \`saeri_access_limitations=open\` when specified), \`license_id\` CC-BY-SA-4.0, one recognized publicly marked XLS resource, original size ceiling.
2. Download each publicly authorised XLS over verified HTTPS same host, verify ZIP vs BIFF readable \`xlrd\`; save exact archive SHA256 and XLS sheet name, row and column counts, first ~5 header candidates only (no row values, names or identity); examine if there is a candidate common ORIGINAL \`Island ID\` with consistent type, never name fuzzy matching.
3. For invasives: discover exact column layout containing Norway rat \`Rattus norvegicus\`, \`Rattus rattus\` (not to confuse taxon), mouse and other mammals, explicit present/absent/probable/unknown legend, date/visit link. Until legend confirmed, do not recode source cells to biological binary truth.
4. For visits: identify exact join key(s), field/desktop visit type, date, observer effort fields and island visit counts without making "no rat record=rat absent". Inspect whether any **repeated targeted rat detection & genuine negative check** exists, or just database entry activity.
5. For locations: verify geographical WGS84 valid and hectares source geometry (original island CENTROID points only, not polygons). Eradication histories should stay separate from current occupancy; a historically eradicated island is not automatically predator-free after reintroductions. Birds remains schema-only.
6. Produce five-dataset public permission/register/sha/schema source receipt plus support classification. If multiple workbook files inaccessible, be explicit \`SOURCE_ACCESS_HOLD\`. A verified source workbook is not proof we have verified negative field histories.
7. Only AFTER field-negative effort and island key lineage gates are passed, freeze a **new independent** rat occupancy probability model and spatially blocked original-island validation. If only per-island inferred statuses exist, keep \`SOURCE_RECORD_STATUS_MODEL_ONLY\` and do not call it true occupancy SDM.

### Original source provenance and prior art
- Official catalogue: https://dataportal.saeri.org/dataset/fibdv8-20140601-invasives
- Independent peer-reviewed rat modelling, **already done**: *Modeling the distribution of Norway rats (Rattus norvegicus) on offshore islands in the Falkland Islands* (Tabak et al. 2015), 158 islands of which 56 assessed rat-present, 102 no evidence, and rat detection probability from five repeat surveys on ten islands. Area / distance to rat source known mechanisms. Do not claim rediscovery of that correlation is innovative.
- Appropriate future novel comparison if quality permits: does **validated rat occupancy** versus **source-assigned risk** partition island colonization opportunities and local seabird breeding refuges in an archipelago with maritime exposure, and does transfer from UK to Falklands fail due to island-size/swimming-human dispersal mix? True seabird outcome and independent temporal exposure require their own support.
- UK V40 maps and V36 JNCC H2 STOP untouched. South Antarctic original #197/#199 and frozen Ecology #189 untouched.

**Source STOP conditions:** no original public XLS file, no reliable original crosswalk ID, no source field legend, or no effort-indexed field non-detection => no ecological occupancy probability claim. A qualitative source status atlas is permitted if original source records are verified and licence terms honored.
