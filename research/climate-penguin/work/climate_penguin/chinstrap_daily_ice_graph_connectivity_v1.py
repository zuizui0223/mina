"""Original BAS Chinstrap GPS x daily OSI SAF low-SIC graph-connectivity diagnostic.

Source: BAS GPS V2 and EUMETSAT OSI-450-a1 v3.1 (25 km daily SIC).
Question: under explicit *hypothetical* ice-exclusion thresholds, are the
ocean-grid pixels near observed GPS fixes in the same low-SIC connected
component as the nearest source-island coastal marine cell?

This is an intentionally coarse-grid, illustrative model of geometric graph
connectivity, NOT documented penguin passability, foraging, krill availability
or realized ice-avoidance. 15/30/50% thresholds are merely sensitivities.
Origin is the pre-fixed original first-GPS-fix island-year median, and the
ocean mask is OSI SAF product-valid marine pixels, not a shoreline survey.
No missing satellite data or unobserved GPS days are treated as zero ice.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
import xarray as xr
from scipy.ndimage import generate_binary_structure, label

import chinstrap_daily_ice_same_day_GPS_2013_v1 as satellite
import chinstrap_daily_SIC_three_island_year_pairs_v1 as original
import signy_gps_krill_access_v1 as geodesic
import south_orkney_chinstrap_island_krill_v1 as colony

PAIRS=((2011,"LI"),(2013,"PI"),(2015,"MI"))
THRESHOLDS=(15.0,30.0,50.0)
FLAGS=(False,True)
NEIGHBOURS=(4,8)
COAST_SEED_RADIUS=(35.,60.)
GPS_PIXEL_RADIUS=(20.,35.)
COAST_SIC_STATUS="HYPOTHETICAL_NATIVE_SATELLITE_PIXEL_CONNECTIVITY_NOT_PENGUIN_PASSABILITY"
NATIVE_SHAPE=(432,432)
CONTEXT_RADIUS=(10.,150.)
GPS_DOI="10.5285/8f8ccba5-01af-4b00-8a3b-c3c85b24bf92"
SIC_DOI="10.15770/EUM_SAF_OSI_0023"

def graph_labels(flat_sic,valid_indices,threshold,neighbours,shape):
    """Label 4/8 adjacent low-SIC source-valid pixels, in original EASE2."""
    if neighbours not in NEIGHBOURS or threshold not in THRESHOLDS:
        raise ValueError("Unregistered sensitivity rule")
    values=np.asarray(flat_sic,dtype=float).ravel()
    ocean=np.asarray(valid_indices,dtype=int)
    if values.size!=shape[0]*shape[1]:
        raise ValueError("Original source satellite grid native shape mismatch")
    if ocean.size!=np.unique(ocean).size:
        raise ValueError("Source ocean pixels not unique")
    if (ocean.size and (ocean.min()<0 or ocean.max()>=values.size)):
        raise ValueError("Source ocean native index outside raster")
    eligible=np.zeros(values.size,dtype=bool)
    eligible[ocean]=np.isfinite(values[ocean])&(values[ocean]>=0)&(values[ocean]<threshold)
    connected,n_comp=label(eligible.reshape(shape),
                           structure=generate_binary_structure(2,1 if neighbours==4 else 2))
    return connected.ravel(),eligible,int(n_comp)

def select_coast_seed(labels,eligible,source_distance_km,limit):
    """Nearest *threshold-passing* source marine cell; NONE if no coastal seed.

    This is a scenario assumption; no evidence of physical ocean access.
    """
    dist=np.asarray(source_distance_km,dtype=float).ravel()
    if labels.size!=dist.size or eligible.size!=dist.size:
        raise ValueError("Satellite mask/geo-distance shape mismatch")
    possible=np.flatnonzero(eligible & np.isfinite(dist) & (dist<=limit))
    if not possible.size:
        return None,0
    nearest=int(possible[np.argmin(dist[possible])])
    if labels[nearest]==0:
        raise ValueError("Source eligible ocean seed is outside open graph")
    return nearest,int(possible.size)

def diagnostic(visited,ice,labels,eligible,distances,coast_seed,context=(10.,150.)):
    """One vote per original visited satellite pixel, not per GPS tag/fix."""
    ids=sorted(int(k) for k in visited)
    if any(v<0 or v>=ice.size for v in ids):
        raise ValueError("Source GPS visited pixel ID outside native satellite")
    n=len(ids)
    high=sum(float(ice[i])>=0 and not eligible[i] for i in ids)
    low=sum(bool(eligible[i]) for i in ids)
    unknown=sum(not math.isfinite(float(ice[i])) for i in ids)
    if high+low<n and unknown==0:
        raise ValueError("Original visited pixels do not exhaust source low/high categories")
    active=int(labels[coast_seed]) if coast_seed is not None else 0
    seed_connected=sum(bool(eligible[i]) and int(labels[i])==active for i in ids) if active else 0
    disconnected=low-seed_connected
    valid_within=np.asarray(np.isfinite(distances)&(distances>=context[0])&
                            (distances<=context[1]),dtype=bool)
    background_open=valid_within & eligible
    background_reachable=background_open & (labels==active) if active else np.zeros_like(background_open)
    return {
        "n_original_distinct_GPS_ocean_pixels":n,
        "n_original_GPS_cells_meeting_or_exceeding_SIC_threshold":high,
        "n_original_GPS_cells_below_SIC_threshold":low,
        "n_original_GPS_cells_below_threshold_connected_to_seed":(
            seed_connected if coast_seed is not None else None),
        "n_original_GPS_low_ice_cells_disconnected_from_seed":(
            disconnected if coast_seed is not None else None),
        "n_source_GPS_pixels_with_unknown_daily_SIC":unknown,
        "fraction_visited_in_binary_low_SIC_connected_component":(
            seed_connected/n if n and coast_seed is not None else None),
        "n_background_original_low_SIC_ocean_pixels_10_150km":int(background_open.sum()),
        "n_background_original_low_SIC_connected_pixels_10_150km":(
            int(background_reachable.sum()) if coast_seed is not None else None),
        "background_low_SIC_connectivity_fraction":(
            float(background_reachable.sum()/background_open.sum())
            if background_open.any() and coast_seed is not None else None),
        "low_ice_seed_defined":coast_seed is not None,
    }

def run(gps_file,ice_dir,receipt):
    tracks,shared,gps_frozen=original.original_source_days(gps_file)
    all_tracks,_=colony.read_all_chinstrap(gps_file)
    centres=colony.island_source_centers(all_tracks)
    dates=sorted(set().union(*(set(shared[key]) for key in PAIRS)))
    sources={r["date"]:r for r in receipt["source_original_daily_netcdfs"]}
    if set(dates)!=set(sources) or len(dates)!=45:
        raise ValueError("GPS source days not identical to 45 downloaded original daily ice files")
    q=[]
    daily=[]
    grid_sha=None
    expected_pairs={}
    for year,other in PAIRS:
        expected_pairs[(year,other)]=len(shared[(year,other)])
        for day in shared[(year,other)]:
            source=sources[day]
            source_file=ice_dir/source["file"]
            native=satellite.open_day(source_file,source)
            with xr.open_dataset(source_file) as ds:
                lat=np.asarray(ds["lat"].values,dtype=float).ravel()
                lon=np.asarray(ds["lon"].values,dtype=float).ravel()
            if lat.size!=NATIVE_SHAPE[0]*NATIVE_SHAPE[1] or lon.size!=lat.size:
                raise ValueError("OSI original geolocation source grid changed")
            sha=hashlib.sha256(lat.tobytes()+lon.tobytes()).hexdigest()
            if grid_sha is not None and sha!=grid_sha:
                raise ValueError("Original satellite EASE2 coordinate geometry changed across daily source files")
            grid_sha=sha
            for strict in FLAGS:
                f="strict" if strict else "all"
                native_ids=native[f+"_ids"]
                for threshold in THRESHOLDS:
                    for neighbourhood in NEIGHBOURS:
                        labels,eligible,n_comps=graph_labels(
                            native["values"],native_ids,threshold,neighbourhood,NATIVE_SHAPE)
                        for site in ("SI",other):
                            anchor=centres[site,year]
                            distances=np.asarray(geodesic.geodesic(
                                lat,lon,anchor["center_lat"],anchor["center_lon"]),dtype=float)
                            visit_source=[(tag,fixes) for (s,y,tag,d),fixes in tracks.items()
                                          if (s,y,d)==(site,year,day)]
                            if not visit_source:
                                raise ValueError("No true original BAS GPS support on shared native day")
                            visited_by_radius={}
                            for radius in GPS_PIXEL_RADIUS:
                                cells={}
                                tags_with_pixel=set()
                                for tag,fixes in visit_source:
                                    native_points=satellite.sample(native,fixes,radius,strict)
                                    if native_points:tags_with_pixel.add(tag)
                                    for idx,sic in native_points.items():
                                        idx=int(idx)
                                        if idx in cells and not math.isclose(cells[idx],sic,abs_tol=1e-9):
                                            raise ValueError("One original satellite cell mapped to inconsistent daily ice")
                                        cells[idx]=float(sic)
                                visited_by_radius[radius]=(cells,tags_with_pixel)
                            for coast in COAST_SEED_RADIUS:
                                seed,n_coast_eligible=select_coast_seed(labels,eligible,distances,coast)
                                for radius in GPS_PIXEL_RADIUS:
                                    visited,tags_with_pixel=visited_by_radius[radius]
                                    score=diagnostic(visited,native["values"],labels,eligible,distances,seed)
                                    row={
                                        "season_start":year,"other_island":other,"island":site,
                                        "source_GPS_shared_calendar_day":day,
                                        "SIC_cutoff_percent_binary_open_below":threshold,
                                        "original_SIC_source_status_strict":strict,
                                        "original_native_pixel_connectivity_neighbours":neighbourhood,
                                        "hypothetical_nearest_low_ice_coastal_seed_limit_km":coast,
                                        "GPS_nearest_satellite_ocean_cell_limit_km":radius,
                                        "n_original_GPS_tags_with_any_fix":len(visit_source),
                                        "n_original_GPS_tags_with_valid_SIC":len(tags_with_pixel),
                                        "n_original_low_ice_coastal_seeds_within_limit":n_coast_eligible,
                                        "original_low_ice_coast_seed_pixel":seed,
                                        "n_low_SIC_ocean_graph_components_hemisphere":n_comps,
                                        **score,
                                        "not_actual_penguin_route_or_ice_passability":True,
                                        "not_independent_prey_or_reproduction":True
                                    }
                                    daily.append(row)
            # Native geolocation + all source flag and threshold combinations
            # kept; the dataset includes original GPS deployment-days indirectly
            # through the n_tag support in each paired island row.
    if len(daily)!=45*2*len(THRESHOLDS)*len(FLAGS)*len(NEIGHBOURS)*len(COAST_SEED_RADIUS)*len(GPS_PIXEL_RADIUS):
        raise ValueError("Source day/paired island full binary-conductivity sensitivity grid incomplete")
    indexed={(r["season_start"],r["other_island"],r["source_GPS_shared_calendar_day"],
              r["SIC_cutoff_percent_binary_open_below"],r["original_SIC_source_status_strict"],
              r["original_native_pixel_connectivity_neighbours"],
              r["hypothetical_nearest_low_ice_coastal_seed_limit_km"],
              r["GPS_nearest_satellite_ocean_cell_limit_km"],r["island"]):r
             for r in daily}
    if len(indexed)!=len(daily):
        raise ValueError("Source daily connectivity table contains duplicate scientific grain")
    paired=[]
    for year,other in PAIRS:
        for date in shared[(year,other)]:
            for threshold in THRESHOLDS:
                for strict in FLAGS:
                    for near in NEIGHBOURS:
                        for coast in COAST_SEED_RADIUS:
                            for radius in GPS_PIXEL_RADIUS:
                                key=(year,other,date,threshold,strict,near,coast,radius)
                                a=indexed[*key,"SI"]
                                b=indexed[*key,other]
                                av=a["fraction_visited_in_binary_low_SIC_connected_component"]
                                bv=b["fraction_visited_in_binary_low_SIC_connected_component"]
                                paired.append({
                                    "season_start":year,"other_island":other,
                                    "source_GPS_shared_calendar_day":date,
                                    "SIC_cutoff_percent_binary_open_below":threshold,
                                    "original_SIC_source_status_strict":strict,
                                    "original_native_pixel_connectivity_neighbours":near,
                                    "hypothetical_coastal_seed_limit_km":coast,
                                    "GPS_nearest_satellite_ocean_cell_limit_km":radius,
                                    "n_Signy_GPS_native_SIC_pixels":a["n_original_distinct_GPS_ocean_pixels"],
                                    "n_other_GPS_native_SIC_pixels":b["n_original_distinct_GPS_ocean_pixels"],
                                    "Signy_coast_seed_exists":a["low_ice_seed_defined"],
                                    "other_coast_seed_exists":b["low_ice_seed_defined"],
                                    "Signy_visited_low_SIC_connected_fraction":av,
                                    "other_visited_low_SIC_connected_fraction":bv,
                                    "Signy_minus_other_binary_low_SIC_connectivity_fraction":(
                                        av-bv if av is not None and bv is not None else None),
                                    "source_sic_threshold_is_not_true_penguin_ice_barrier":True
                                })
    primary=[r for r in paired if
             r["SIC_cutoff_percent_binary_open_below"]==15 and
             not r["original_SIC_source_status_strict"] and
             r["original_native_pixel_connectivity_neighbours"]==8 and
             r["hypothetical_coastal_seed_limit_km"]==35 and
             r["GPS_nearest_satellite_ocean_cell_limit_km"]==20]
    if len(primary)!=45:
        raise ValueError("Primary sea-ice hypothetical-connectivity source day coverage incomplete")
    months=[]
    for year,other in PAIRS:
        for month in ("12","01"):
            arr=[r for r in primary if r["season_start"]==year and
                 r["other_island"]==other and
                 r["source_GPS_shared_calendar_day"][4:6]==month]
            n_valid=[r for r in arr if
                     r["Signy_visited_low_SIC_connected_fraction"] is not None and
                     r["other_visited_low_SIC_connected_fraction"] is not None]
            months.append({
                "season_start":year,"other_island":other,
                "month":"December" if month=="12" else "January",
                "n_source_GPS_shared_days":len(arr),
                "n_days_both_islands_with_detected_coast_seed_and_GPS_SIC":len(n_valid),
                "mean_Signy_minus_other_hypothetical_low_ice_connected_GPS_fraction":(
                    float(np.mean([r["Signy_minus_other_binary_low_SIC_connectivity_fraction"]
                        for r in n_valid])) if n_valid else None),
                "n_days_Signy_source_coast_seed_unavailable":sum(not r["Signy_coast_seed_exists"] for r in arr),
                "n_days_other_source_coast_seed_unavailable":sum(not r["other_coast_seed_exists"] for r in arr),
                "n_unpaired_due_to_missing_SIC_or_no_graph_seed":len(arr)-len(n_valid),
                "source_missing_is_not_ice_free_or_no_movement":True
            })
    return daily,paired,months,{
        "status":COAST_SIC_STATUS,
        "source_GPS_DOI":GPS_DOI,"source_OSI_SIC_DOI":SIC_DOI,
        "source_GPS_pre_ice_day_roster":gps_frozen,
        "n_source_original_daily_NetCDF":len(sources),
        "n_source_island_day_sensitivity_rows":len(daily),
        "n_source_paired_days":len(paired),
        "native_source_ice_geolocation_sha256":grid_sha,
        "primary_months":months,
        "predefined_hypothetical_thresholds_percent":THRESHOLDS,
        "predefined_graph_adjacency":NEIGHBOURS,
        "predefined_coastal_seed_km":COAST_SEED_RADIUS,
        "predefined_satellite_ocean_pixel_match_km":GPS_PIXEL_RADIUS,
        "not_independent_ocean_access_validation":True,
        "important_limitations":[
           "Sea ice 15/30/50% thresholds describe artificial graph edges, not biological impassability.",
           "Satellite valid-ocean mask does not resolve coastline, narrow water channels, bergs, current or pack-ice traversability.",
           "Source island location is fixed from earliest original GPS positions, not verified actual sea-entry point.",
           "No low-ice seed within 35/60km is a null source connection scenario, not absence of penguin mobility.",
           "A 25km daily ice pixel above 15% does not mean the penguin could not swim within or around that pixel.",
           "One step from one cell to another in 4/8-connectivity is not a physically realized GPS trajectory.",
           "Daily 24h satellite SIC is not instant ice nor penguin location at exact observed time; GPS not dive/capture.",
           "Connected source grid cells and multiple GPS tags are spatially correlated, not independent climate experiments.",
           "No independent krill acoustic response, salinity causal slope, demographic, N_eff or 2050/2100 breeding forecasts validated."
        ]
    }

def write_csv(path,records):
    if not records:raise ValueError("No source observation")
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]))
        w.writeheader()
        w.writerows(records)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--gps-source",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--phase",required=True,choices=("discover","download","analyze"))
    a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    tracks,days,receipt=original.original_source_days(a.gps_source)
    if a.phase=="discover":
        (a.out/"source_GPS_days_frozen_before_SIC.json").write_text(
            json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
        print("SOURCE_DATES_FROZEN="+json.dumps(
            {"shared":receipt["same_year_island_pair_support"],
             "unique_source_days":len(receipt["unique_calendar_dates"])},ensure_ascii=False))
    elif a.phase=="download":
        old=json.loads((a.out/"source_GPS_days_frozen_before_SIC.json").read_text())
        if old["unique_calendar_dates"]!=receipt["unique_calendar_dates"]:
            raise ValueError("Original GPS source day support changed before SIC was opened")
        folder=a.out/"original_daily_SIC_NetCDF"
        source=original.fetch_daily(days,folder)
        (a.out/"original_daily_ice_SHA_receipts.json").write_text(
            json.dumps(source,indent=2,ensure_ascii=False)+"\n")
        print(json.dumps({"status":"SOURCE_ORIGINAL_45_DAILY_SIC_RETRIEVED",
                          "n_daily_netCDF":len(source["source_original_daily_netcdfs"])}))
    else:
        source=json.loads((a.out/"original_daily_ice_SHA_receipts.json").read_text())
        rows,pairs,months,gate=run(a.gps_source,a.out/"original_daily_SIC_NetCDF",source)
        write_csv(a.out/"island_day_25km_lowSIC_binary_graph_source.csv",rows)
        write_csv(a.out/"same_date_Signy_other_binary_graph_comparison.csv",pairs)
        write_csv(a.out/"source_island_year_month_binary_graph_summary.csv",months)
        (a.out/"decision.json").write_text(json.dumps(gate,indent=2,ensure_ascii=False)+"\n")
        print("SOURCE_BINARY_GRAPH_RESULT="+json.dumps({
            "status":gate["status"],"source_days":gate["n_source_original_daily_NetCDF"],
            "scenario_months":months,
            "n_rows":len(rows),"n_pairs":len(pairs)},ensure_ascii=False))
if __name__=="__main__":
    main()
