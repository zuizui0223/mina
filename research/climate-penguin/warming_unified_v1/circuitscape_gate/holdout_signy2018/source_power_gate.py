#!/usr/bin/env python3
"""Unused BAS Chinstrap Signy-2018 GPS season: source/date and physical SIC-power gate.

No held-out GPS utilization or Circuitscape rank score is examined in this script.
Date list is fixed from original qualifying GPS *before* opening the original
same-day OSI SAF daily satellite files. All GPS days are retained, including flat
summer SIC. NO-GO does not imply sea ice never affects Chinstrap movements.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from pathlib import Path
import csv,hashlib,json,math,sys
import numpy as np
import xarray as xr
from scipy.ndimage import label,generate_binary_structure

HERE=Path(__file__).resolve().parent
CLIMATE=HERE.parents[2]
sys.path.insert(0,str(CLIMATE/"work"/"climate_penguin"))
import south_orkney_chinstrap_island_krill_v1 as col
import signy_gps_krill_access_v1 as geo
import chinstrap_daily_ice_same_day_GPS_2013_v1 as sat

OUT=HERE/"outputs"
ORIGINAL_ZIP=Path("build/signy2018_circuit_original/original_chinstrap_gps.zip")
ORIGINAL_ICE=Path("build/signy2018_circuit_original/original_daily_sic")
OUT.mkdir(parents=True,exist_ok=True)

FIX_SEASON=2018
SITE="SI"
ALLOWED_MONTHS={(2018,11),(2018,12),(2019,1),(2019,2)}
MIN_TRACK_HOURLY=10
MIN_GPS_DAYS=8
GO_MIN_SOURCE_DAYS=10
GO_MIN_ICE_GRADIENT_DAYS=5
SOURCE_MAX_KM=35.
OUTER_RADIUS_KM=210.
GROUND_MIN_KM=175.
RANK_INNER_KM=10.
RANK_OUTER_KM=160.
P90_P10_GO_PP=1.
NATIVE_SHAPE=(432,432)

def writecsv(path,rows):
    if not rows:raise ValueError("Empty output table")
    with path.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
def sums(a):
    if not a.size:return None
    return {"mean_sic_pct":float(a.mean()),"sd_sic_pp":float(np.std(a)),
            "min_sic_pct":float(a.min()),"max_sic_pct":float(a.max()),
            "range_sic_pp":float(np.ptp(a)),
            "p10_sic_pct":float(np.quantile(a,.1)),
            "p90_sic_pct":float(np.quantile(a,.9)),
            "p90_minus_p10_pp":float(np.quantile(a,.9)-np.quantile(a,.1)),
            "fraction_sic_ge1":float(np.mean(a>=1.)),
            "fraction_sic_ge15":float(np.mean(a>=15.)),
            "fraction_sic_ge30":float(np.mean(a>=30.))}
def main():
    if not ORIGINAL_ZIP.exists():raise ValueError("Original publisher GPS ZIP unavailable")
    records,gpsaudit=col.read_all_chinstrap(ORIGINAL_ZIP)
    if len(records)!=308:raise ValueError("Original Chinstrap GPS payload changed")
    centers=col.island_source_centers(records)
    if set(centers)!={("SI",2011),("SI",2013),("SI",2015),("SI",2018),
                    ("LI",2011),("PI",2013),("MI",2015)}:
        raise ValueError("Source original GPS deployment year roster changed")
    center=centers[SITE,FIX_SEASON]
    source=[r for r in records if (r["island"],r["season"])==(SITE,FIX_SEASON)]
    if len(source)!=58 or center["n_original_deployments"]!=58:
        raise ValueError("Previously untested Signy 2018 deployment count changed")
    dates=defaultdict(lambda:{"tags":set(),"hourly_gps_fixes":0})
    n_qualified=0
    for track in source:
        p=track["points"]
        la=np.asarray([x[1] for x in p])
        lo=np.asarray([x[2] for x in p])
        km=geo.geodesic(la,lo,center["center_lat"],center["center_lon"])
        spikes=geo.singleton_spike_mask(p)
        keep=(km>=10)&(km<=150)&(~spikes)
        hourly=geo.selected_hourly([p[int(i)] for i in np.flatnonzero(keep)])
        if len(hourly)<MIN_TRACK_HOURLY:continue
        n_qualified+=1
        for t,lat,lon,*_ in hourly:
            if (t.year,t.month) not in ALLOWED_MONTHS:continue
            day=t.strftime("%Y%m%d")
            dates[day]["tags"].add(track["deployment"])
            dates[day]["hourly_gps_fixes"]+=1
    all_dates=sorted(dates)
    original_roster=[{"date":d,"n_original_hourly_fixes":dates[d]["hourly_gps_fixes"],
                       "n_qualified_deployments_with_fixes":len(dates[d]["tags"])}
                      for d in all_dates]
    # Write the original-only roster BEFORE fetching any ice.
    source_record={"status":"ORIGINAL_GPS_SOURCE_DATES_FIXED_BEFORE_ICE",
       "original_gps_sha256":gpsaudit["source_original_313_csv_sha256"],
       "original_publisher_gps_doi":"10.5285/8f8ccba5-01af-4b00-8a3b-c3c85b24bf92",
       "source_site":SITE,"source_season":FIX_SEASON,
       "source_deployments":len(source),"qualified_deployments":n_qualified,
       "year_months":["2018-11","2018-12","2019-01","2019-02"],
       "origin":center,
       "all_eligible_gps_calendar_dates":all_dates,
       "n_gps_calendar_dates":len(all_dates),
       "n_original_qualified_hourly_fixes_in_gps_calendar_dates":sum(v["hourly_gps_fixes"] for v in dates.values()),
       "does_not_score_gps_pixel_preferences":True}
    (OUT/"gps_original_source_date_roster.json").write_text(json.dumps(source_record,indent=2)+"\n")
    if not original_roster:
        (OUT/"source_power_summary.json").write_text(json.dumps({"status":"NO_SOURCE_GPS_DAYS",**source_record},indent=2)+"\n")
        raise SystemExit(2)
    writecsv(OUT/"gps_days_source_only.csv",original_roster)
    print("SIGNY2018_GPS_SOURCE="+json.dumps({k:source_record[k] for k in (
        "source_deployments","qualified_deployments","n_gps_calendar_dates",
        "n_original_qualified_hourly_fixes_in_gps_calendar_dates")}),flush=True)
    if len(all_dates)<MIN_GPS_DAYS:
        (OUT/"source_power_summary.json").write_text(json.dumps(
            {"status":"INSUFFICIENT_ORIGINAL_GPS_SUPPORT",**source_record},indent=2)+"\n")
        print("SIGNY2018_GO_NO_GO=INSUFFICIENT_ORIGINAL_GPS_SUPPORT",flush=True)
        return
    receipts=sat.collect(all_dates,ORIGINAL_ICE)
    names={r["date"]:r for r in receipts["source_original_daily_netcdfs"]}
    if set(names)!=set(all_dates):raise ValueError("Original OSI data missing GPS calendar date")
    (OUT/"source_original_2018_daily_SIC_receipts.json").write_text(json.dumps(receipts,indent=2)+"\n")
    stats=[];geofingerprint=None
    for day in all_dates:
        path=ORIGINAL_ICE/names[day]["file"]
        grid=sat.open_day(path,names[day])
        with xr.open_dataset(path) as ds:
            lat=np.asarray(ds.lat.values,dtype=float).reshape(NATIVE_SHAPE)
            lon=np.asarray(ds.lon.values,dtype=float).reshape(NATIVE_SHAPE)
        # Verify unchanged original grid identity without trusting a relocated GPS fix.
        geo_sha=hashlib.sha256(np.asarray(lat).tobytes()+np.asarray(lon).tobytes()).hexdigest()
        if geofingerprint is None:geofingerprint=geo_sha
        if geo_sha!=geofingerprint:raise ValueError("Original Antarctic source-grid geometry moved")
        dist=np.asarray(geo.geodesic(lat,lon,center["center_lat"],center["center_lon"]),dtype=float)
        valid=np.zeros(lat.size,dtype=bool)
        valid[grid["all_ids"]]=True
        valid=valid.reshape(NATIVE_SHAPE)
        sic=np.asarray(grid["values"]).reshape(NATIVE_SHAPE)
        closest=np.where(valid & np.isfinite(dist)&(dist<=SOURCE_MAX_KM),dist,np.inf)
        if np.isfinite(closest).any():
            seedidx=int(np.argmin(closest))
            sr,sc=divmod(seedidx,432)
            domain=valid&(dist<=OUTER_RADIUS_KM)
            groups,n=label(domain,structure=generate_binary_structure(2,2))
            mask=groups==groups[sr,sc] if groups[sr,sc]>0 else np.zeros_like(domain)
            coast_distance_km=float(dist[sr,sc])
        else:
            seedidx=None;mask=np.zeros_like(valid);coast_distance_km=None
        rank=(mask&(dist>=RANK_INNER_KM)&(dist<RANK_OUTER_KM))
        ground=(mask&(dist>=GROUND_MIN_KM)&(dist<=OUTER_RADIUS_KM))
        full=sums(sic[mask])
        within=sums(sic[rank])
        record={"date":day,
            "n_qualified_deployments_with_original_gps":len(dates[day]["tags"]),
            "n_original_hourly_gps_fixes":dates[day]["hourly_gps_fixes"],
            "source_nearest_ocean_native_pixel":seedidx,
            "source_snap_distance_km":coast_distance_km,
            "n_source_connected_ocean_cells":int(mask.sum()),
            "n_ranking_area_source_ocean_cells":int(rank.sum()),
            "n_offshore_ground_cells":int(ground.sum()),
            "n_total_source_ocean_cells":int(valid.sum()),
            "full_circuit_sic_range_pp":full["range_sic_pp"] if full else None,
            "full_circuit_sic_sd_pp":full["sd_sic_pp"] if full else None,
            "ranking_area_sic_mean_pct":within["mean_sic_pct"] if within else None,
            "ranking_area_sic_sd_pp":within["sd_sic_pp"] if within else None,
            "ranking_area_sic_range_pp":within["range_sic_pp"] if within else None,
            "ranking_area_sic_p90_p10_pp":within["p90_minus_p10_pp"] if within else None,
            "ranking_area_fraction_ge1":within["fraction_sic_ge1"] if within else None,
            "ranking_area_fraction_ge15":within["fraction_sic_ge15"] if within else None,
            "ranking_area_fraction_ge30":within["fraction_sic_ge30"] if within else None,
            "source_ocean_pixel_support":seedidx is not None,
            "ground_pixel_support":bool(ground.sum()>=8),
            "ice_spatial_gradient_at_least_1pp":bool(within is not None and within["p90_minus_p10_pp"]>=P90_P10_GO_PP),
            "gps_score_or_model_output_read_for_date_selection":False}
        stats.append(record)
        print("SIGNY2018_DAY_PHYSICAL_SUPPORT="+json.dumps({
          "date":day,"gps_hourly_fixes":record["n_original_hourly_gps_fixes"],
          "n_ocean":record["n_source_connected_ocean_cells"],
          "ice_p90_p10_pp":record["ranking_area_sic_p90_p10_pp"]}),flush=True)
    writecsv(OUT/"original_2018_19_same_day_physical_ice_support.csv",stats)
    ready=[r for r in stats if r["ground_pixel_support"] and r["source_ocean_pixel_support"]]
    identifiable=[r for r in ready if r["ice_spatial_gradient_at_least_1pp"]]
    status="GO_TO_FIXED_NATIVE_CIRCUIT_HOLDOUT" if len(ready)>=GO_MIN_SOURCE_DAYS and len(identifiable)>=GO_MIN_ICE_GRADIENT_DAYS else "NO_GO_WEAK_SOURCE_OR_SIC_SPATIAL_VARIATION"
    result={"status":status,"source_gps_archive_sha":gpsaudit["source_original_313_csv_sha256"],
      "n_gps_source_days":len(all_dates),"n_source_original_sic_files":len(names),
      "n_days_original_valid_ocean_source_and_ground":len(ready),
      "n_days_with_source_sic_spatial_gradient_ge1pp":len(identifiable),
      "n_days_fully_constant_circuit_sic":sum(r["full_circuit_sic_range_pp"] is not None and r["full_circuit_sic_range_pp"]<=1e-8 for r in stats),
      "n_days_constant_gps_rank_area_sic":sum(r["ranking_area_sic_range_pp"] is not None and r["ranking_area_sic_range_pp"]<=1e-8 for r in stats),
      "mean_rank_area_sic_p90_p10_pp":float(np.mean([r["ranking_area_sic_p90_p10_pp"] for r in ready])) if ready else None,
      "n_qualifying_new_calendar_days_with_gps":len(all_dates),
      "gate_minimum_eligible_source_days":GO_MIN_SOURCE_DAYS,
      "gate_minimum_sic_gradient_days":GO_MIN_ICE_GRADIENT_DAYS,
      "old_training_years":[2011,2013,2015],
      "new_holdout_season_start_year":2018,
      "interpretation":"Power/source gate only; no held-out ocean use ranks computed, and one new Signy season is not a new independent island."}
    (OUT/"source_power_summary.json").write_text(json.dumps(result,indent=2)+"\n")
    print("SIGNY2018_GO_NO_GO="+json.dumps(result),flush=True)

if __name__=="__main__":main()
