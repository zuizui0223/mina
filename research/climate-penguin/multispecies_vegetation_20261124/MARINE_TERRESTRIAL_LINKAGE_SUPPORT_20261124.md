# Marine–terrestrial integration: actual spatial and seasonal support audit

Executed locally 2026-11-24. This audit checks whether the frozen marine proxy evidence and existing terrestrial breeding-source analyses can be joined; no new ecological regression, nutrient flux, vegetation change, mediation, or future biological forecast. Prior main and manuscript branches unchanged. Only public-source-derived tables used. No restricted/unreleased AADC data or derived results republished.

## Source lock

- Isotope 860 site-seasons / 88 sites: original-source artifact [14328755565](https://github.com/zuizui0223/mina/actions/runs/44083346932/artifacts/14328755565), ZIP SHA256 dfbbe281e50e7d802c43f69255c02878a4c49c14185804acb7e15048189af205.
- Direct polynya source [14539723210](https://github.com/zuizui0223/mina/actions/runs/44545732891/artifacts/14539723210), ZIP SHA256 702ab3eeff9ed953c19a9e696492ba9bf5cddce204d40a9c7d9b1234d98f9f96. Join by exact site_id, season, and source_region, unique one-to-one, 860 rows; 439 complete polynya exposures / 85 sites. The 439-row matched exposure values agree exactly with the original complete-winter table. Native geography 88 unique IDs at 100 km. Both ZIP CRC and source hashes verified.
- Previously audited endpoint roster (30 species-site rows / 21 sites) and strict three-species panel (3 sites), previous commit eec88f05b05dcdca0fb583be4d6c2142f65e3fdf. Local roster.csv SHA256 2ad33e3b954303246106a51b27f0d6f70b7729862a6a7e8d9080dafb88f20b77; cosurvey.csv ebdc7200cceaa24ae6366ee8152e98d870ede0c78d6a604a30dead0e0dbe8692. ARDL shared, union 23 locations. WGS84 geodesic distance between actual archived source centres; no spatial substitution.

## Peninsula / South Shetland: no linked observation support

| Distance criterion | Sites near isotope centre | Sites near joint isotope-polynya centre |
|---:|---:|---:|
| Exact site ID | 0/23 | 0/23 |
| <=2 km | 0/23 | 0/23 |
| <=10 km | 1/23 | 0/23 |
| <=25 km | 4/23 | 0/23 |
| <=50 km | 10/23 | 0/23 |
| <=100 km | 19/23 | 0/23 |

Nearest joint-panel centre distance is 123.7021568 km (PETE to ARMS). Strict three-species sites: ARDL isotope nearest TSIS 55.255 km, joint HOPE 164.805 km; LION isotope TSIS 12.546 km, joint FRNC 147.470 km; PCHA isotope YALO 20.118 km, joint ARMS 135.698 km. Nearby optical-only records TSIS and YALO have no matched polynya record in the frozen panel. These are source-panel distances, not evidence that nearby waters lack polynyas. No model fitted or values imputed.

## Windmill: geographic but not footprint-level or temporal linkage

| Code | Isotope records | Joint polynya records |
|---|---:|---:|
| BERK |9|4|
| HOLL |11|5|
| ODBE |11|5|
| SHLY |10|5|
| WHTY |10|5|
| Total |51|24|

Four distinct GLORYS wet cells; pairwise code-centre distances 4.891790–23.721153 km. Five codes are not five independent ocean systems; four correspond to grouped localities, not individual island footprints. Only four complete shared winters (2006, 2007, 2008, 2010); BERK 2009 missing, never zero-filled.

| Common winter start | Mean polynya area fraction % | Across-code range pp |
|---:|---:|---:|
|2006|21.519103|1.169074|
|2007|21.592035|0.911497|
|2008|14.582590|0.627049|
|2010|18.032053|1.533597|

Mean within-winter spatial range 1.060304 pp; range of annual means 7.009445 pp, a descriptive comparison on four winters, not a variance decomposition or test of climate effect. The 100-km source supports overlap strongly. Temporal coding matters: 2005/06 breeding survey is austral season starting 2005, not start year 2006. All five marine codes have zero records in 2005, and in 2012 (2012/13) five isotope but zero matched polynya records. No exact two-endpoint marine linkage.

## Synthesis / next gate

Separate three evidence levels: (1) broad physical axes and exploratory winter polynya/summer salinity association with optical guano nitrogen isotope proxy; (2) observed breeding-nest redistribution, composition change and hypothetical local source availability; (3) local terrestrial occupancy, soil and vegetation relationships. They are scientifically complementary, not a demonstrated causal chain. Neither optical isotope composition nor nest number is a measurement of nutrient flux; static botanical mapping is not a vegetation time series.

The next concrete gate is physical exposure reconstruction at the actual peninsula colony centres and census-season dates, with independently matched nutrient and repeated plant observations. Do not substitute another colony's marine conditions, infer actual dietary proportions from proxy, multiply exploratory coefficients into CMIP6 biological predictions, or change frozen model hypotheses. No merge or manuscript change.

Local reproducibility bundle marine_terrestrial_integration_20261124.zip SHA256 efa5a99dad8a5eddc1944aaad885df19d0952d17ed997c997e68ccf98d1fa649 (executed audit.py SHA256 7eb4656e25262450e6f06d6b649827f283bcdf107eb92f046439dcaa834b5893; four CSVs, summary JSON, README). No publisher original data republished. Source artifacts remain linked.
