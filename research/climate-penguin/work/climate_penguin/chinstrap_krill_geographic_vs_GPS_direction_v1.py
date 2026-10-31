"""Separate geographic krill opportunity from GPS-directional use in Chinstrap islands.

Source-only exploratory retrospective geometry. 2011/2013/2015 matched
Chinstrap other-island/Signy original GPS locations; BAS Freer et al (2025)
hurdle-GAM krill fields already learned from IMR original acoustics and sea
ice/salinity, and are NOT independently observed prey. No GPS fix is a
verified feeding/dive/capture event. No ocean coastline, sea ice accessibility,
travel cost or colony nesting suitability outside the model-valid mask is
independently supplied.

Two pre-specified descriptive reference constructions:
  (A) area weighted ALL model-valid raster cells at 10–150 km from source GPS
      first-fix island-year center; reference is GEOGRAPHIC opportunity only
      and is NOT actual navigable/ice-free foraging space.
  (B) distance-matched background expected modelled krill in each 10-km
      model-centre ring represented by the tag's observed UNIQUE model cells,
      then equal source deployments per island-year. Controls the traversed
      distance distribution but NOT directional access or device selection.
No null probability or p-value is claimed from the within-GAM comparison.
"""
from __future__ import annotations
import argparse,csv,json,math,statistics
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
import signy_gps_krill_access_v1 as source
import south_orkney_chinstrap_island_krill_v1 as island

MIN_KM=10
MAX_KM=150
BIN_KM=10
N_VALID_HOURS=10
PAIRS=island.PAIRS
PERIODS=("preseason","same_summer")
EXPECTED_RATIO={(2011,"LI"):2.4401791626507325,
                (2013,"PI"):6.3144099881199685,
                (2015,"MI"):2.747735214032483}

def grid_reference(arr,transform,lat0,lon0):
    """Geographic model-valid cell means with cos(latitude) weighting."""
    rr,cc=np.indices(arr.shape)
    lat=transform.f+(rr+0.5)*transform.e
    lon=transform.c+(cc+0.5)*transform.a
    distance=np.asarray(source.geodesic(lat,lon,lat0,lon0),dtype=float)
    bins=np.floor(distance/BIN_KM).astype(int)
    weights=np.cos(np.deg2rad(lat))
    valid=np.isfinite(arr)
    geographic=valid&(distance>=MIN_KM)&(distance<=MAX_KM)
    if int(np.sum(geographic))<20:
        raise ValueError("publisher GAM source raster has insufficient candidate geography")
    values={
        "geographic_baseline":float(np.average(arr[geographic],weights=weights[geographic])),
        "n_model_valid_geographic_cells":int(np.sum(geographic)),
        "source_model_valid_fraction":float(np.sum(geographic)/np.sum(
            (distance>=MIN_KM)&(distance<=MAX_KM))),
    }
    rings={}
    # All bins from 0-10 to 160-170 to support source GPS-fix distance
    # gates 10-150 km and native 0.08333° centre-edge differences.
    for b in range(17):
        mask=valid&(bins==b)
        if np.any(mask):
            rings[b]=float(np.average(arr[mask],weights=weights[mask]))
    if len(rings)<9:
        raise ValueError("original spatial raster support too narrow")
    return values,rings,bins

def source_selected_unique_cells(track,center,arr,transform):
    """Exactly the existing GPS cohort, isolated 12m/s spikes, 1 source fix/h."""
    points=track["points"]
    lat=np.array([p[1] for p in points])
    lon=np.array([p[2] for p in points])
    km=source.geodesic(lat,lon,center["center_lat"],center["center_lon"])
    spikes=source.singleton_spike_mask(points)
    ok=(km>=MIN_KM)&(km<=MAX_KM)&(~spikes)
    hourly=source.selected_hourly([points[i] for i in np.flatnonzero(ok)])
    if len(hourly)<N_VALID_HOURS:
        return (len(hourly),None)
    a=np.array([x[1] for x in hourly])
    b=np.array([x[2] for x in hourly])
    values,rr,cc=source.sampled_cells(arr,transform,a,b)
    mask=np.isfinite(values)
    if not np.any(mask):
        return (len(hourly),None)
    cells=sorted(set(zip(rr[mask].tolist(),cc[mask].tolist())))
    return (len(hourly),cells)

def run(gps_source,model_source):
    gps,qc=island.read_all_chinstrap(gps_source)
    centers=island.island_source_centers(gps)
    models=source.source_models(model_source)
    references={}
    grid_bands={}
    for (site,season),center in centers.items():
        for period in PERIODS:
            model_year=season+(period=="same_summer")
            arr,tr=models[model_year]
            info,rings,bins=grid_reference(
                arr,tr,center["center_lat"],center["center_lon"])
            references[site,season,period]=info
            grid_bands[site,season,period]=(rings,bins)
    records=[]
    for tag in gps:
        site,season=tag["island"],tag["season"]
        center=centers[site,season]
        row={
            "island":site,"season_start":season,"deployment":tag["deployment"],
            "original_source_member_sha256":tag["source_sha256"],
            "n_original_GPS_positions":tag["raw_positions"],
            "source_GPS_not_foraging_or_diving":True,
            "GIS_reference_not_navigable_ocean_area":True,
        }
        for period in PERIODS:
            year=season+(period=="same_summer")
            arr,tr=models[year]
            nhrs,cells=source_selected_unique_cells(tag,center,arr,tr)
            row[period+"_model_year"]=year
            row[period+"_qualified_source_hourly"]=nhrs>=N_VALID_HOURS
            row[period+"_original_hourly_positions_in_geographic_window"]=nhrs
            row[period+"_visited_unique_model_cells"]=len(cells) if cells else 0
            row[period+"_observed_track_mean_GAM_g_m2"]=None
            row[period+"_distance_matched_reference_GAM_g_m2"]=None
            row[period+"_track_vs_distance_reference_ratio"]=None
            if not cells:continue
            rings,bins=grid_bands[site,season,period]
            try:
                expected=[rings[bins[r,c]] for r,c in cells]
            except KeyError as e:
                raise ValueError("visited source cell lacks same-distance model background") from e
            observed=[float(arr[r,c]) for r,c in cells]
            obs=float(statistics.mean(observed))
            avail=float(statistics.mean(expected))
            row[period+"_observed_track_mean_GAM_g_m2"]=obs
            row[period+"_distance_matched_reference_GAM_g_m2"]=avail
            row[period+"_track_vs_distance_reference_ratio"]=obs/avail if avail>0 else None
        records.append(row)
    if len(records)!=308:
        raise ValueError("original 308 source nonempty GPS deployments changed")

    # Independently regenerate original core analysis to verify
    # exact geography/temporal alignment, not just our new calculation.
    originals=island.tag_exposures(gps,centers,models)
    group=island.aggregate(originals)
    contrast=island.comparisons(group)
    island.verify(gps,centers,group,contrast)
    old={(r["island"],r["season_start"],r["deployment"]):r for r in originals
         if r["minimum_island_center_distance_km"]==MIN_KM
         and r["isolated_speed_spikes_removed"]}
    if len(old)!=len(records):raise ValueError("prior source 308 trace counts drift")
    for r in records:
        prior=old[r["island"],r["season_start"],r["deployment"]]
        for period in PERIODS:
            valid=r[period+"_observed_track_mean_GAM_g_m2"]
            prior_val=prior[period+"_native_model_krill_g_m2"]
            if valid is None:
                if prior["qualifies_source_hourly_support"] and prior_val is not None:
                    raise ValueError("published GPS qualified source track unexpectedly lost")
            elif not math.isclose(valid,float(prior_val),abs_tol=1e-10,rel_tol=1e-10):
                raise ValueError("original 308-track GPS native model index not reproduced")

    annual=[]
    for (site,season),center in sorted(centers.items()):
        tags=[r for r in records if r["island"]==site and r["season_start"]==season]
        for period in PERIODS:
            value=references[site,season,period]
            filtered=[r for r in tags if r[period+"_observed_track_mean_GAM_g_m2"] is not None]
            if not filtered:raise ValueError("no original tag-level modelkrill field")
            obs=statistics.mean(r[period+"_observed_track_mean_GAM_g_m2"] for r in filtered)
            radial=statistics.mean(r[period+"_distance_matched_reference_GAM_g_m2"] for r in filtered)
            geo=value["geographic_baseline"]
            annual.append({
                "island":site,"season_start":season,"model_year":season+(period=="same_summer"),
                "period":period,"n_original_deployments":len(tags),
                "n_qualified_source_GPS_deployments":len(filtered),
                "n_valid_model_cells_geographic_10_150km":value["n_model_valid_geographic_cells"],
                "geographic_model_valid_fraction":value["source_model_valid_fraction"],
                "source_tag_equal_mean_visited_GAM_g_m2":obs,
                "source_tag_equal_mean_distance_matched_GAM_g_m2":radial,
                "all_model_valid_cells_geographic_background_GAM_g_m2":geo,
                "GPS_visited_div_geographic_background":obs/geo if geo>0 else None,
                "GPS_visited_div_distance_matched_background":obs/radial if radial>0 else None,
                "directional_exposure_from_published_GAM_not_independent_prey":True
            })

    idx={(r["island"],r["season_start"],r["period"]):r for r in annual}
    comparisons=[]
    for season,other in PAIRS:
        for period in PERIODS:
            a=idx["SI",season,period]
            b=idx[other,season,period]
            if a["n_qualified_source_GPS_deployments"]<1 or b["n_qualified_source_GPS_deployments"]<1:
                raise ValueError("incomplete source island pair")
            raw=b["source_tag_equal_mean_visited_GAM_g_m2"]/a["source_tag_equal_mean_visited_GAM_g_m2"]
            background=b["all_model_valid_cells_geographic_background_GAM_g_m2"]/a["all_model_valid_cells_geographic_background_GAM_g_m2"]
            radial=b["source_tag_equal_mean_distance_matched_GAM_g_m2"]/a["source_tag_equal_mean_distance_matched_GAM_g_m2"]
            geometric_adjusted=(b["GPS_visited_div_geographic_background"]/
                                a["GPS_visited_div_geographic_background"])
            distance_adjusted=(b["GPS_visited_div_distance_matched_background"]/
                               a["GPS_visited_div_distance_matched_background"])
            if not math.isclose(raw/background,geometric_adjusted,abs_tol=1e-9):
                raise ValueError("island contrast multiplicative decomposition identity failed")
            if not math.isclose(raw/radial,distance_adjusted,abs_tol=1e-9):
                raise ValueError("distance-conditional multiplicative decomposition identity failed")
            if period=="preseason" and not math.isclose(raw,EXPECTED_RATIO[season,other],abs_tol=1e-7):
                raise ValueError("original GPS island ratio numerical receipt not reproduced")
            comparisons.append({
                "season_start":season,"same_species":"Chinstrap","other_island":other,"reference_island":"SI",
                "model_period":period,"source_yearly_model":season+(period=="same_summer"),
                "n_tag_other":b["n_qualified_source_GPS_deployments"],
                "n_tag_Signy":a["n_qualified_source_GPS_deployments"],
                "other_div_Signy_GPS_visited_model_ratio":raw,
                "other_div_Signy_all_model_cells_geographic_background_ratio":background,
                "other_div_Signy_distance_matched_GAM_reference_ratio":radial,
                "other_div_Signy_GPS_use_after_geographic_background_ratio":geometric_adjusted,
                "other_div_Signy_GPS_use_after_radial_background_ratio":distance_adjusted,
                "same_published_model_used_for_all_terms":True,
                "geographic_background_not_true_navigable_foraging_space":True,
                "statistical_n_independent_region_year_pairs":1
            })
    return records,annual,comparisons,qc

def write(path,rows):
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--gps-zip",required=True,type=Path)
    a.add_argument("--model-zip",required=True,type=Path)
    a.add_argument("--out",required=True,type=Path)
    a.add_argument("--check",action="store_true")
    o=a.parse_args()
    tags,background,contrasts,qc=run(o.gps_zip,o.model_zip)
    if o.check and not (len(tags)==308 and len(background)==14 and len(contrasts)==6):
        raise ValueError("307 tag or 14 island model periods or 6 source-matched contrasts missing")
    o.out.mkdir(parents=True,exist_ok=True)
    write(o.out/"original_tag_visited_vs_radial_background.csv",tags)
    write(o.out/"seven_island_years_two_model_periods.csv",background)
    write(o.out/"three_matched_island_pairs_two_periods.csv",contrasts)
    result={
        "status":"SOURCE_BACKED_PUBLISHED_KRILL_MODEL_GEOGRAPHY_VS_GPS_TRAJECTORY_DIAGNOSTIC",
        "original_GPS_source_DOI":"10.5285/8f8ccba5-01af-4b00-8a3b-c3c85b24bf92",
        "modelled_krill_source_DOI":"10.5285/4fd0a1bf-da1a-4021-82eb-2fc513910e32",
        "n_original_GPS_deployments":len(tags),
        "n_island_years":7,"n_model_periods":2,"n_matched_year_island_pairs":3,
        "methods":{
            "main_source_GPS":"10-150 km source island-first-fix median center; 1 original fix per hour; singleton >12m/s GPS spike removal; >=10 hourly fixes; equal model-valid unique GAM cells per tag, then equal tags per island-year",
            "geographic_background":"All model-valid native GAM cells with centres 10-150 km from island first-GPS-fix median; cos latitude area weighting; not independent ocean/ice/foraging reachable mask",
            "distance_matched_background":"For each unique GPS-visited GAM cell, take area-weighted mean GAM from model-valid native cells in its 10km radial bin, then equal visited model cells and tags",
            "season_definitions":"Jan-Feb model year T before Dec T-January T+1 tagged breeding; T+1 same-summer as alternative retrospective, NOT a prospective forecast"
        },
        "matched_preseason":[x for x in contrasts if x["model_period"]=="preseason"],
        "published_GAM_is_pretrained_on_source_ice_salinity_acoustic":True,
        "cautions":[
            "Geographic reference contains only GAM-valid cells; no independent land/ocean mask and no validated ice access/travel cost.",
            "Radial 10km-bin background assumes azimuthal accessibility of all model-valid cells at the same radial distance. This is NOT established for flightless birds.",
            "GPS movement not necessarily foraging, diving or consumption and some source devices observe different time span.",
            "The Freer model was trained with sea ice/salinity and the same IMR acoustic fields, so independent environmental causal inference would be circular.",
            "Three other islands each occur only once in paired comparison; island-year replication is not independent. Signy 2011 has four original qualifying GPS deployments.",
            "Matching by year, keeping all 308 source units and original 2013 combined-acoustic missingness does not provide out-of-time krill model validation.",
            "No 2050/2100 penguin breeding abundance, patch N_eff, greening, or colonization numerical projection is scientifically calibrated by these indices."
        ]
    }
    (o.out/"decision.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"n_source_deployments":len(tags),
        "n_matched_pairs":len(contrasts),
        "preseason":result["matched_preseason"],"original_source_QA":qc,
        "receipt_checked":bool(o.check)},ensure_ascii=False))

if __name__=="__main__":
    main()
