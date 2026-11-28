# Ledda fast-ice discrepancy: physical-space support versus temporal source leakage

**2026-10-08 / PR195 / non-causal exploratory audit.** Main manuscript PR189 untouched.

## Verified external-pixel results at two independent published historical site centroids

Original LaRue et al. (2024) colony attribute source, pinned author commit:
`LEDD,Ledda Bay,-74.228,-130.784`.

Independent Fretwell et al. (2021) Table 2 (doi:10.1002/rse2.176):
`Ledda Bay,-74.272,-131.243`. Direct author-source CI reproduction yields **14.692 km** between centroids; the two radius-5-km buffers do **not** intersect. This discrepancy is between publication locations and does NOT establish actual penguin movement.

Fraser and Massom (2020) v2.2 independent classified 1-km landfast ice maps (doi:10.26179/5d267d1ceb60c) were sampled in **nominal 15-day composite windows completed before the original high-resolution bird image date**:

| Source image | Physical composite start → end | LaRue-centroid 3km, class 4 | Fretwell-centroid 3km, class 4 |
|---|---|---:|---:|
| 2011-09-23 `bpresent=no`; annotation 'fast ice available' | 2011-08-29 → 2011-09-12 | **0/28** | **0/30** |
| 2014-10-13 `bpresent=no`; annotation 'fast ice available no birds' | 2014-09-28 → 2014-10-12 | **0/28** | **30/30** |

Source reproduction: original center [run 37765982575](https://github.com/zuizui0223/mina/actions/runs/37765982575); alternate [run 37766642777](https://github.com/zuizui0223/mina/actions/runs/37766642777). These are fixed-radii **retrospective physical map classes**, NOT 2014 actual habitat occupancy or confirmed vacant nesting platform. Class 0 includes pack/ocean and possible ambiguous fill; class 4 is mapped landfast-ice interior. The Fretwell 2021 paper already states that Ledda forms regularly but suffers early fast-ice break-up in many years.

### Causal-time correction: *nominally earlier* mosaic is not guaranteed to be strictly prospective

The Fraser et al. (2020) published algorithm constructs 15-day mosaics. When manual fast-ice boundary delineation is obscured by clouds, it can rely on **immediately preceding and/or following 15-day composite imagery** (Methods, https://doi.org/10.5194/essd-12-2987-2020). Accordingly:

- The 2011 Aug29–Sep12 and 2014 Sep28–Oct12 **nominal observation windows** end before their source bird image dates;
- It does **not** follow that every boundary or filled classification was assigned without information from later dates;
- No independent per-pixel source chronology was audited. Label these raster estimates **retrospective reconstructed physical exposure**, not real-time predictor, intervention, or environment-before-decision measurement.
- A fast-ice map could legitimately disagree with a single-day visible ice observation because the mapping rule requires persistent edges over ~15 days, and the source satellite imagery, spatial grain and time window differ.

The original class-4 all-interior Fretwell 2014 radius3km contrasts sharply with all-0 at LaRue, which raises a real **geographical-support sensitivity**; it neither selects the true 2014 penguin breeding footprint nor proves physical seasonal accessibility. The retrospective correction matters for any forecasting or causal claim.

### The next falsification (independent supplementary physical readouts, still exploratory)

The two-center seasonal comparison has been added as a GitHub Actions workflow, keeping the 2011/2014 *same calendar composites and radii* to inspect frequency, continuity and last-mosaic differences.

Separately, the original satellite image annotations already known *before opening the new physical annual mosaics* permit a fixed four-year context:
- 2009-10-27 `no`, annotator: no fast ice
- 2010-10-08 `yes`, small colony detected (not confirmed successful breeding)
- 2012-10-22 `no`, annotator: no fast ice
- 2013-11-30 `yes`, small polygons (late-stage comparator, **not October exchangeable**)

Frozen date selection: each complete **nominal** 15-day mosaic from May onward whose nominal end is before the source image date, at **both** prepublished centers and all radii 1/3/5km. Do not fit p-values or choose a center after observing ice values. A consistent 2014 class-4 positive at Fretwell and class-0 at LaRue is NOT a social-Allee observation until annually georeferenced actual nest footprints, meaningful source-negative repeated surveys, ice longevity through breeding and breeding success have been independently established.

**Ecological novelty gate:** No new causal mechanism yet. Claims of persistent suitable but unused habitat, avoidant social settlement, real first founding or neighbor rescue remain HOLD. The new positive contribution is a concrete measured contradiction of treating static 'same colony' coordinates as interchangeable local physical environments.

## Provenance

- LaRue author table: https://github.com/davidiles/EMPE_Global/blob/13f71112da43c1fd082273677757b41c550457ed/data/colony_attributes.csv
- Fretwell et al. 2021: https://doi.org/10.1002/rse2.176
- Fraser et al. 2020 physical mapping and retrospective method: https://doi.org/10.5194/essd-12-2987-2020
- Fraser/Massom AADC v2.2: https://doi.org/10.26179/5d267d1ceb60c
- Source audit receipt: `results/EMPEROR_LEDDA_LARUE_CENTROID_FROZEN_FASTICE_MAIN_SUMMARY_V1.json`
- Historical physical calibration contract: `contracts/EMPEROR_LEDDA_2009_2010_2012_2013_AUTHOR_STATE_ICE_CALIBRATION_V1.json`
