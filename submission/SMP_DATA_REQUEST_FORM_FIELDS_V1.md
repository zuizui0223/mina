# BTO SMP data-request form fields v1

**Official route checked:** 2026-10-05  
**Form:** BTO Data Request Form for BTO survey data  
**SMP contact:** smp@bto.org  
**Status:** ready-to-paste draft; personal contact, supervisor and funding fields remain author-controlled.

## Form choices

- Request type: **Student Project** or **Academic (non-commercial)** — author to choose according to submission status.
- Specific geographic data search: **No**
- Already know what data are required: **Yes**
- Preferred format: **Text/Excel**

## Title of project / question

**Spatial recovery thresholds after local breeding-site abandonment in colonial seabirds**

Under 200 characters.

## Source of funding

[AUTHOR TO COMPLETE; 100-character limit]

## Supervisor name

[AUTHOR TO COMPLETE; required by form]

## Details of research

**Paste-ready field; keep under the form's 1500-character limit.**

I am testing whether population recovery retraces spatial collapse in colonial seabirds. For the same repeatedly monitored breeding SiteID, I will compare the surrounding MasterSite population state when that SiteID changes from occupied to an explicit zero count with the state when it is later recolonized. The primary prediction is that recolonization requires a higher surrounding population state than abandonment. The design is prospectively staged. First, SiteID/MasterSite identity, sampling support, count units and methods are resolved without count magnitudes. Second, counts are reduced only to positive, provider-confirmed explicit zero, or missing, and completed calendar-consecutive abandonment-to-recolonization spells are frozen. Only if a predeclared multi-species support gate passes are count magnitudes opened for one paired analysis. The focal SiteID is excluded from the surrounding abundance predictor. A structured circular-phase null preserves local multivariate abundance trajectories and shared temporal covariance. Outputs will be a peer-reviewed ecological study and reproducible analysis code. Antarctic penguin results generated the hypothesis but are not pooled with the SMP test.

## Details of proposed collaboration

**Paste-ready field; under 1500 characters.**

This work forms part of an academic research project. [AUTHOR TO COMPLETE: supervisor/collaborator names and affiliations, or state that no collaboration beyond the supervisory team is currently proposed.] I would welcome clarification from the SMP team on historical SiteID/MasterSite continuity and the semantics of nil/zero records because these metadata determine eligibility before any ecological outcome is examined.

## Details of data required

**Paste-ready field; keep under the form's 1500-character limit.**

Please provide a record-level SMP Colony Count / Whole Colony Count extract for 1986-2024 for non-sensitive species across Britain and Ireland, preferably CSV/TSV/Excel. Requested fields, where available: Species; Country/County; SiteID; Site; MasterSite and stable MasterSite identifier; Plot/spatial-level indicator; StartGrid/EndGrid; site category/type/habitat; survey date/year; Method; Unit; Count; Accuracy; Estimate/estimate type; Comments; verification/review status; explicit nil-return/zero indicator; merged/aggregate-site indicator; and metadata on SiteID/MasterSite renames, merges, splits, retirement/replacement or boundary changes. It is essential to distinguish explicit surveyed zero/nil returns from unvisited or missing SiteID-year records, and mutually exclusive child SiteIDs from parent/aggregate records. If zero semantics or identifier continuity differ among historical data eras, please indicate the compatible years/record families. A SiteID/MasterSite crosswalk or change-log would be especially helpful.

## Any other information

**Paste-ready field; under 500 characters.**

A public structural audit previously exposed count magnitudes for Black-legged Kittiwake at Flamborough and Filey Coast SPA; that species x MasterSite combination is excluded prospectively. All structural, zero-state, replication and inferential rules were frozen before receiving the requested bulk extract. If stable SiteID histories or sufficient completed vacancy-recolonization cycles are unavailable, the test will stop rather than relax thresholds.

## Provider confirmation requested separately

After the initial request/response, freeze written confirmation of:

1. whether a direct Count=0 row is a surveyed nil return;
2. whether an absent SiteID x year row means not surveyed/missing rather than zero;
3. whether estimated/imputed zeroes can be excluded;
4. the years/record families for which these semantics apply;
5. stable physical MasterSite identifiers;
6. SiteID rename/merge/split/boundary/retirement history;
7. parent/aggregate versus mutually exclusive child-site relationships.

Use:
- `submission/SMP_PROVIDER_ZERO_CONFIRMATION_TEMPLATE_V1.json`
- `submission/SMP_PROVIDER_SITE_IDENTITY_TEMPLATE_V1.csv`

## Official-source notes

The SMP public data page directs users seeking large amounts of data to the BTO Data Request form and gives `smp@bto.org` for caveats/advice.

Current BTO SMP guidance explicitly states that zero counts are important because they distinguish species absence from a site not being surveyed, and describes site extinction as a recorded nil return. The prospective analysis still requires provider confirmation that these semantics apply to the requested historical bulk record family.
