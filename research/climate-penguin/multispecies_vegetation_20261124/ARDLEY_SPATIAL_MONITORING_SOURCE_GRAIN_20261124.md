# Ardley published footprint comparison: census timing and source-grain audit

2026-11-24. Source: Mustafa et al. (2020), UBA TEXTE 112/2020, section 5.1.3, Table 10 and Figures 52–53, https://www.umweltbundesamt.de/sites/default/files/medien/479/publikationen/texte_112-2020_monitoring_von_pinguinkolonien_in_der_antarktis_mit_hilfe_der_fernerkundung.pdf ; Braun, Grämer & Peter (2025), DOI 10.60810/openumwelt-7664, §§4,5.2.1.1,5.2.1.3 and Fig.6, https://www.umweltbundesamt.de/system/files/medien/11850/publikationen/63_2025_texte.pdf. Table values manually transcribed from indexed text; screenshot requests failed, so table layout remains to be visually verified. No new GIS or plant time series acquired.

## Count timing

{
  "records": [
    {
      "year": 2016,
      "month": 11,
      "ADPE": 395,
      "CHPE": 15,
      "GEPE": 7259,
      "total": 7669
    },
    {
      "year": 2016,
      "month": 12,
      "ADPE": 448,
      "CHPE": 20,
      "GEPE": 7227,
      "total": 7695
    },
    {
      "year": 2017,
      "month": 11,
      "ADPE": 350,
      "CHPE": 15,
      "GEPE": 6242,
      "total": 6607
    },
    {
      "year": 2017,
      "month": 12,
      "ADPE": 363,
      "CHPE": 19,
      "GEPE": 6708,
      "total": 7090
    }
  ],
  "changes": [
    {
      "year": 2016,
      "GEPE_change_pct": -0.4408320705331259,
      "total_change_pct": 0.33902725257530797
    },
    {
      "year": 2017,
      "GEPE_change_pct": 7.465555911566812,
      "total_change_pct": 7.310428333585595
    }
  ],
  "latest": [
    {
      "baseline_month": 11,
      "GEPE_change_pct": 27.234860621595637
    },
    {
      "baseline_month": 12,
      "GEPE_change_pct": 18.395945140131186
    }
  ]
}

Cross-check against original audited pair table strict_original_pair_1993_2020_matched_siteyears.csv blob 7e86b2eb5f5a4e012f128101ebec02d51cbfe41c (PR214 branch). All 63 ARDL pair rows expand consistently to 21 three-species site-years. The archive's 2016 count (448,20,7227) exactly matches December in UBA 2020 Table 10, whereas 2017 (350,15,6242) matches November. Thus even this strict same-citation/site/calendar-year/method panel does not enforce the same seasonal sampling phase. The published map in Figure 53 of UBA 2020 is dated 13–14 December 2017. The 2017 November vs December totals differ by 483 nests (7.31043% of November). The 2023/24 report gives 7,942 gentoo pairs (peak in series), so the descriptive increase versus 2017 ground-count alternatives is 18.395945–27.234861%, not a confidence interval or an area change. Report 2025 methods: late censuses may use apparently occupied nests (AON), and year labels refer to second half of austral season, unlike archived calendar-year count labels. Do not merge label years without actual dates.

## Spatial observation and gate

2020 report explicitly describes GPS perimeter mapping and two census visits per breeding season, with December maps in 2016/17 and 2017/18. 2025 report describes an older ground-based survey vs current Uruguayan aerial photography in 2023/24 (map CRS WGS84 UTM21S). Fig.6 compares 2017/18 vs 2023/24 breeding groups and separately labelled zonation boundaries. Published qualitative findings: central Zone 4 no longer occupied, southern Zone 7 new/larger gentoo groups and local moss deterioration associated with faecal cover. These are published observations, not results of our own polygon delineation. Different year-specific zone boundaries and possible occlusion of overlapping colored footprints in a rendered figure prevent treating visible color pixel areas as occupied area/transition classes until the original geometry and map encoding are verified. No original georeferenced breeding-group polygons or repeated botanical plots identified. No area, plant response or nutrient effect computed. Source figure acquisition [run 45389357453](https://github.com/zuizui0223/mina/actions/runs/45389357453) was queued at this checkpoint; no success or raw acquisition claimed.

Roland et al. (2024), DOI 10.1038/s41561-024-01564-5, reports spectral browning in eastern Ardley in 2016–2021; this differs in location and time from southern breeding-group changes and must not be treated as the same mechanism. The 2026 field-validation critique (DOI 10.1038/s41561-026-02076-0) further motivates field-supported vegetation endpoints. No new causal or climate forecast claim.

## Next exact data requirement

2017/18 and 2023/24 original georeferenced breeding-group layers (and survey dates, CRS, definition of active/AON or guano footprint, and mapped extent), plus a comparable botanical observation table or validated repeated imagery. Freeze common study boundary and distinguish continuous/new/lost/unobserved polygons. Compare botanical change on a fixed common observation support; do not infer plant decline from an increase in visible guano or map-classified browning alone. No restricted input published. Main/frozen papers unchanged.
