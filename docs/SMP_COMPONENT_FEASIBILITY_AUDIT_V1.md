# SMP component-resolved macroecology feasibility audit v1

**Status:** outcome-blind feasibility audit; no SMP abundance effects have been analysed.

## Question

Can the BTO/JNCC Seabird Monitoring Programme (SMP) supply repeated, internally resolved breeding counts that are suitable for testing whether declining colonial breeders contract onto fewer effective breeding components beyond proportional thinning?

## Public-source findings

### 1. The database has a spatial hierarchy

SMP Online distinguishes:

- **Master site**
- **Site** within a master site
- optional **Plot** within a site
- **Whole Colony Count** when no plot is used

The public data browser visibly returns site names nested in master sites, e.g. forms such as `Horn Head 5 (Horn Head)` and `Loop Head 24 (Loop Head Peninsular)`.

The current colony-count form contains separate Master site, Site name/Site code and Plot site name fields.

### 2. Plot identity is intended to persist

The SMP Online application guide states that existing plots appear under a site's Plots tab and instructs counters to keep plot names consistent so that future counters can survey the same plots.

For colony-count entry, the counter selects an existing plot from a drop-down, or explicitly selects site-level whole-colony count.

This is strong evidence that plot identity is stored as a database object rather than free text in the modern system.

### 3. Site boundaries are explicitly continuity-controlled

The application guide says boundary changes should be accepted only when they represent the area that has always been counted. Extending monitoring to a new area requires creation of a new site.

The 1995 handbook likewise says colony/census boundaries should remain the same as previous counts or be directly relatable, and recommends clearly documented plot boundaries.

This is unusually favourable for a longitudinal component-composition analysis.

### 4. Missingness and zero abundance are distinguishable

BTO explicitly asks counters to submit zero / nil returns and states that a zero is essential because it distinguishes local absence from a site not being surveyed.

Therefore an absent site-year record must not be converted to zero; explicit zero/nil returns can be treated as observed zeros.

### 5. Method and count-unit metadata are retained

Public records expose Species, Date, County, Site, Plot, Method, Unit, Count and comments/qualifiers.

The current form additionally records accuracy and environmental conditions. Recommended count units differ by species (e.g. AON, AOS, IND, AOT, AOB), so cross-year and cross-site analyses must harmonize only records with compatible units.

### 6. Public portal exposes some plot-monitoring records, but legacy aggregation is ambiguous

A public Kittiwake query at Flamborough Head and Bempton Cliffs produced rows with `Plot=4` from 2009–2019 and whole-colony rows in other years.

However, the 2009 `Plot=4` count (1585 AON) matches the published total across seven Kittiwake study plots, so the public `Plot` value should **not** be assumed to be an individual physical plot without a data dictionary/crosswalk.

This means the safest primary spatial grain is currently **Master site → child Site**, not individual Plot.

### 7. The public portal is not enough for a full macro audit

The browser can show and request downloads for filtered data, but large or bespoke extracts are directed to the BTO Data Request system / SMP organiser.

The Data Access and Use Policy allows research use, requires acknowledgement of providers/recorders, and notes that bespoke extractions may incur charges. Sensitive records may be spatially blurred or restricted.

## Current feasibility conclusion

**Conditional GO.**

SMP is structurally suitable in principle because it preserves nested spatial units, distinguishes explicit zero from missing, and treats boundary continuity as a design requirement.

The unresolved issue is whether a research extract can provide stable child-site identifiers and site-history metadata consistently enough across decades to reconstruct Master-site × species panels without silent merges, splits or redefinitions.

## Primary spatial grain

### Primary
**Master site × species population**, with **child Site IDs** as breeding components.

Why:
- child sites are visible in the public database;
- site boundaries are continuity-controlled;
- child-site structure exists across many master sites;
- this grain is likely more consistently retained than historical plot records.

### Secondary, only if supplied with continuity metadata
**Site × species population**, with named **Plots** as components.

This is potentially valuable for within-colony replication but is not required for the macro analysis.

## Data fields required for a decisive feasibility audit

For all colony-count records, ideally 1986–latest verified year:

- master_site_id
- master_site_name
- site_id
- site_name
- plot_id
- plot_name
- year / date
- species code and species name
- count
- count unit
- survey method
- accuracy / estimate flag
- explicit nil-return indicator
- validation / verification status
- comments, especially merged-site or reconstructed-total flags
- source survey / census
- site boundary/version identifier if available
- site creation/retirement date if available
- merge/split/rename/crosswalk history for site and plot identifiers

No geographic coordinates for sensitive species are required for the initial audit.

## Hard exclusions

Exclude from the primary panel:

- records labelled as merged-site totals when constituent child sites are also used;
- child sites whose identity cannot be held constant or crosswalked through the analysis interval;
- years with unobserved child sites mistaken for zeros;
- mixtures of incompatible count units;
- obvious method changes that make counts non-comparable unless BTO metadata explicitly validate comparability;
- synthetic or extrapolated whole-master-site totals used together with their constituent components.

## Key external sources

- SMP public data browser: https://app.bto.org/seabirds/public/data.jsp
- SMP Online application guide: https://app.bto.org/static/seabirds/app_guide.pdf
- Current colony-count form: https://www.bto.org/sites/default/files/smp_colony_counts_2023.pdf
- Seabird Monitoring Handbook: https://www.bto.org/sites/default/files/seabird-monitoring-handbook.pdf
- SMP data access/use policy: https://www.bto.org/sites/default/files/seabird_monitoring_programme_data_access_and_use_policy.pdf
- SMP participation/data guidance: https://www.bto.org/get-involved/volunteer/projects/seabird-monitoring-programme/taking-part

## Decision

Do **not** postpone or replace the frozen penguin Ecology Report yet.

The next decision point is receipt of a metadata-complete SMP extract or confirmation from the SMP team that the required child-site continuity fields/crosswalk can be supplied.
