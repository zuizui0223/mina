"""Reproduce original BAS Chinstrap GPS × OSI SAF daily SIC for all island-year pairs.

Extends the published original 2013 Signy-Powell 14-day GPS/day SIC test to
2011 Signy-Laurie and 2015 Signy-Monroe, including 2013 as a source-defined
positive-control cohort. Date intersections are fixed from ORIGINAL native
GPS before reading satellite SIC. No dates selected based on ice or krill.

Satellite SIC is original OSI-450-a1 v3.1 25km EASE2 24h means; not the ice
at individual GPS timestamp, ocean access, foraging/dive behaviour or prey.
"""
from __future__ import annotations
import argparse,csv,datetime as dt,hashlib,json,math
from collections import defaultdict,Counter
from pathlib import Path
import numpy as np
import chinstrap_daily_ice_same_day_GPS_2013_v1 as src
import signy_gps_krill_access_v1 as geo
import south_orkney_chinstrap_island_krill_v1 as penguins

PAIRS=((2011,"LI"),(2013,"PI"),(2015,"MI"))
SOURCES=(2011,2013,2015)
MONTHS={(2011,12),(2012,1),(2013,12),(2014,1),(2015,12),(2016,1)}
RADII=(20.,35.)
MIN_HOURS=(1,3,6)
PHASES=("all_GPS_days","Dec_GPS_only","Jan_GPS_only")
DOI="10.15770/EUM_SAF_OSI_0023"
EXPECTED_2013=tuple((dt.date(2013,12,29)+dt.timedelta(days=i)).strftime("%Y%m%d") for i in range(14))
MAX_DAYS=130

def original_source_days(gpszip):
    records,audit=penguins.read_all_chinstrap(gpszip)
    centers=penguins.island_source_centers(records)
    if len(records)!=308 or len(centers)!=7:
        raise ValueError("Original BAS source Chinstrap GPS cohorts changed")
    goodcount=0
    daylocations=defaultdict(list)
    for tag in records:
        site,year=tag["island"],tag["season"]
        center=centers[site,year]
        pts=tag["points"]
        la=np.asarray([p[1] for p in pts])
        lo=np.asarray([p[2] for p in pts])
        distance=geo.geodesic(la,lo,center["center_lat"],center["center_lon"])
        spikes=geo.singleton_spike_mask(pts)
        keep=(distance>=10)&(distance<=150)&(~spikes)
        hourly=geo.selected_hourly([pts[i] for i in np.flatnonzero(keep)])
        if len(hourly)<10:continue
        goodcount+=1
        if year not in SOURCES or site not in ("SI","LI","PI","MI"):continue
        for t,lat,lon,*_ in hourly:
            if (t.year,t.month) not in MONTHS:continue
            day=t.strftime("%Y%m%d")
            daylocations[site,year,tag["deployment"],day].append((lat,lon))
    if goodcount!=253:
        raise ValueError("Original source 253 GPS-qualified movements changed")
    pairdates={}
    frozen=[]
    for year,other in PAIRS:
        daysA={d for (site,y,tag,d) in daylocations if site=="SI" and y==year}
        daysB={d for (site,y,tag,d) in daylocations if site==other and y==year}
        common=sorted(daysA&daysB)
        if year==2013 and tuple(common)!=EXPECTED_2013:
            raise ValueError("2013 independent original 14-day GPS date source changed")
        pairdates[year,other]=common
        frozen.append({"season_start":year,"other_island":other,
                       "n_original_Signy_days":len(daysA),
                       "n_original_other_days":len(daysB),
                       "n_original_shared_days":len(common),
                       "shared_calendar_dates":common,
                       "original_Signy_tags_on_shared_dates":len({tag for site,y,tag,d in daylocations
                            if site=="SI" and y==year and d in common}),
                       "original_other_tags_on_shared_dates":len({tag for site,y,tag,d in daylocations
                            if site==other and y==year and d in common})})
    union=sorted(set().union(*(set(v) for v in pairdates.values())))
    if not union or len(union)>MAX_DAYS:raise ValueError("Source-locked actual GPS date horizon changed")
    out={"status":"FROZEN_3_MATCHED_CHINSTRAP_ISLAND_PAIRS_GPS_SOURCE_DATES_BEFORE_ICE",
         "first_party_GPS_DOI":src.GPS_DOI,
         "native_GPS_source_hash":audit["source_original_313_csv_sha256"],
         "original_GPS_source_tracks":len(records),
         "original_source_qualified_tracks":goodcount,
         "same_year_island_pair_support":frozen,
         "unique_calendar_dates":union,
         "source_ice_examined_to_select_dates":False,
         "unmatched_GPS_dates_not_assumed_zero_ice":True}
    return daylocations,pairdates,out

def fetch_daily(pairdates,folder):
    dates=sorted(set().union(*(set(v) for v in pairdates.values())))
    if not dates:raise ValueError("Zero daily source opportunity")
    return src.collect(dates,folder)

def valid_cell_means(taglocations,pairdates,receipts,directory):
    sourcefiles={r["date"]:r for r in receipts["source_original_daily_netcdfs"]}
    all_dates=sorted(set().union(*(set(v) for v in pairdates.values())))
    if set(sourcefiles)!=set(all_dates):
        raise ValueError("Published daily source file support not the pre-frozen native GPS dates")
    satellite={d:src.open_day(directory/sourcefiles[d]["file"],sourcefiles[d]) for d in all_dates}
    source_tag=[]
    for year,other in PAIRS:
        for date in pairdates[year,other]:
            grid=satellite[date]
            for site in ("SI",other):
                for (loc,season,tag,day),points in taglocations.items():
                    if (loc,season,day)!=(site,year,date):continue
                    for limit in RADII:
                        for strict in (False,True):
                            cells=src.sample(grid,points,limit,strict)
                            source_tag.append({
                               "season_start":year,"other_island":other,
                               "calendar_date":date,"island":site,"original_GPS_deployment":tag,
                               "n_original_hourly_GPS_fixes":len(points),
                               "nearest_satellite_ocean_cell_km":limit,
                               "strict_original_satellite_status_flags":strict,
                               "n_original_matched_ocean_pixels":len(cells),
                               "source_pixel_values_json":json.dumps(cells,sort_keys=True),
                               "native_cell_equal_mean_SIC_percent":float(np.mean(list(cells.values()))) if cells else None,
                               "one_day_24h_ice_not_ice_at_actual_GPS_time":True})
    # Every source GPS observation remains; no source tag is dropped at this stage.
    island_day=[]
    cell_sets=defaultdict(set)
    for year,other in PAIRS:
        for date in pairdates[year,other]:
            for site in ("SI",other):
                for radius in RADII:
                    for strict in (False,True):
                        choices=[r for r in source_tag if (r["season_start"],r["calendar_date"],r["island"],
                               r["nearest_satellite_ocean_cell_km"],r["strict_original_satellite_status_flags"])
                               ==(year,date,site,radius,strict)]
                        for minimum in MIN_HOURS:
                            present=[r for r in choices if r["n_original_hourly_GPS_fixes"]>=minimum
                              and r["n_original_matched_ocean_pixels"]>0]
                            cells={}
                            for r in present:
                                for idx,val in json.loads(r["source_pixel_values_json"]).items():
                                    idx=int(idx);val=float(val)
                                    if idx in cells and not math.isclose(cells[idx],val,abs_tol=1e-11):
                                        raise ValueError("one original satellite ocean pixel has inconsistent SIC")
                                    cells[idx]=val
                            row={"season_start":year,"other_island":other,"calendar_date":date,
                                 "island":site,"radius_km":radius,"strict_quality":strict,
                                 "minimum_GPS_hourly_fixes":minimum,
                                 "source_GPS_tags_with_any_fix":len(choices),
                                 "source_GPS_tags_with_valid_source_SIC":len(present),
                                 "n_original_unique_satellite_ocean_pixels":len(cells),
                                 "n_original_unique_satellite_pixels_SIC_ge15":sum(v>=15 for v in cells.values()),
                                 "source_equal_tag_mean_SIC_percent":float(np.mean(
                                     [r["native_cell_equal_mean_SIC_percent"] for r in present])) if present else None,
                                 "original_unique_ocean_pixel_mean_SIC_percent":float(np.mean(list(cells.values()))) if cells else None,
                                 "source_tag_hours_not_independent_ocean_pixels":True}
                            island_day.append(row)
                            if radius==20 and not strict and minimum==1:
                                cell_sets[year,other,site,"all_GPS_days"].update(cells)
                                phase=("Dec_GPS_only" if date[4:6]=="12" else "Jan_GPS_only")
                                cell_sets[year,other,site,phase].update(cells)
    idx={(r["season_start"],r["other_island"],r["calendar_date"],r["island"],
          r["radius_km"],r["strict_quality"],r["minimum_GPS_hourly_fixes"]):r
         for r in island_day}
    matched=[]
    for year,other in PAIRS:
        for day in pairdates[year,other]:
            for radius in RADII:
                for strict in (False,True):
                    for min_hour in MIN_HOURS:
                        a=idx[year,other,day,"SI",radius,strict,min_hour]
                        b=idx[year,other,day,other,radius,strict,min_hour]
                        at=a["source_equal_tag_mean_SIC_percent"]
                        bt=b["source_equal_tag_mean_SIC_percent"]
                        ap=a["original_unique_ocean_pixel_mean_SIC_percent"]
                        bp=b["original_unique_ocean_pixel_mean_SIC_percent"]
                        matched.append({"season_start":year,"other_island":other,
                            "source_same_calendar_date":day,
                            "radius_km":radius,"strict_quality":strict,
                            "minimum_tag_hours":min_hour,
                            "n_Signy_tags":a["source_GPS_tags_with_valid_source_SIC"],
                            "n_other_tags":b["source_GPS_tags_with_valid_source_SIC"],
                            "n_Signy_native_satellite_pixels":a["n_original_unique_satellite_ocean_pixels"],
                            "n_other_native_satellite_pixels":b["n_original_unique_satellite_ocean_pixels"],
                            "Signy_minus_other_tag_mean_SIC_pp":at-bt if at is not None and bt is not None else None,
                            "Signy_minus_other_unique_pixel_mean_SIC_pp":ap-bp if ap is not None and bp is not None else None,
                            "original_both_islands_SIC_observed":at is not None and bt is not None,
                            "observed_satellite_ice_not_direct_penguin_movement_barrier":True})
    # True same-source-pixel seasonal history: keep each island's set of GPS
    # footprints constant over all common days, and exclude nonmarine/missing
    # satellite cells on any required date (do not call them ice=0).
    fixed_rows=[]
    native_grid_hash={}
    try:
        import xarray as xr
        for date in all_dates:
            with xr.open_dataset(directory/sourcefiles[date]["file"]) as ds:
                coords=np.asarray(ds["lat"].values,dtype=np.float64).tobytes()+np.asarray(
                    ds["lon"].values,dtype=np.float64).tobytes()
                native_grid_hash[date]=hashlib.sha256(coords).hexdigest()
        if len(set(native_grid_hash.values()))!=1:
            raise ValueError("original OSI 25km satellite native grids differ across GPS days")
    except ImportError:
        raise ValueError("xarray source validation is required")
    for year,other in PAIRS:
        shared=pairdates[year,other]
        if not shared:continue
        common_valid=set.intersection(*(set(satellite[d]["all_ids"].tolist()) for d in shared))
        for site in ("SI",other):
            for phase in PHASES:
                chosen=sorted(cell_sets[year,other,site,phase]&common_valid)
                for date in shared:
                    pixels=[float(satellite[date]["values"][p]) for p in chosen]
                    if any(not math.isfinite(v) or not 0<=v<=100.0001 for v in pixels):
                        raise ValueError("Invalid source satellite SIC on fixed original ocean cell")
                    fixed_rows.append({"season_start":year,"other_island":other,
                          "source_same_calendar_date":date,"island":site,
                          "source_GPS_footprint_rule":phase,
                          "n_unique_original_satellite_pixels_fixed_all_shared_days":len(chosen),
                          "fixed_original_pixel_mean_SIC_percent":float(np.mean(pixels)) if pixels else None,
                          "fixed_pixel_ice15_cells":sum(v>=15 for v in pixels),
                          "source_GPS_footprint_fixed_without_using_daily_SIC_value":True,
                          "independent_native_ocean_pixel_sample_size_not_equal_GPS_tags":True})
    fixedidx={(r["season_start"],r["other_island"],r["source_same_calendar_date"],
               r["island"],r["source_GPS_footprint_rule"]):r for r in fixed_rows}
    fixedcontrast=[]
    for year,other in PAIRS:
        for day in pairdates[year,other]:
            for phase in PHASES:
                a=fixedidx[year,other,day,"SI",phase]
                b=fixedidx[year,other,day,other,phase]
                av=a["fixed_original_pixel_mean_SIC_percent"]
                bv=b["fixed_original_pixel_mean_SIC_percent"]
                fixedcontrast.append({"season_start":year,"other_island":other,
                    "calendar_date":day,"footprint":phase,
                    "n_Signy_same_original_pixels":a["n_unique_original_satellite_pixels_fixed_all_shared_days"],
                    "n_other_same_original_pixels":b["n_unique_original_satellite_pixels_fixed_all_shared_days"],
                    "Signy_minus_other_fixed_pixel_SIC_pp":av-bv if av is not None and bv is not None else None,
                    "source_observed_real_SIC_not_route_connectivity":True})
    def summ(arr,key):
        v=[r[key] for r in arr if r[key] is not None]
        return float(np.mean(v)) if v else None
    totals=[]
    for year,other in PAIRS:
        shared=pairdates[year,other]
        for phase in PHASES:
            for label in ("Dec","Jan"):
                subset=[r for r in fixedcontrast if r["season_start"]==year and
                        r["other_island"]==other and r["footprint"]==phase and
                        r["calendar_date"][4:6]==("12" if label=="Dec" else "01")]
                valid=[r for r in subset if r["Signy_minus_other_fixed_pixel_SIC_pp"] is not None]
                totals.append({"season_start":year,"other_island":other,
                       "fixed_GPS_footprint":phase,"month":label,
                       "n_original_shared_source_GPS_days":len(subset),
                       "n_valid_fixed_pixel_daily_contrasts":len(valid),
                       "mean_Signy_minus_other_fixed_25km_cell_SIC_pp":summ(valid,
                           "Signy_minus_other_fixed_pixel_SIC_pp"),
                       "descriptive_posthoc_not_independent_climate_replication":True})
    positive=next((r for r in totals if r["season_start"]==2013 and
                   r["other_island"]=="PI" and r["fixed_GPS_footprint"]=="all_GPS_days"
                   and r["month"]=="Dec"),None)
    if positive is None or not math.isclose(positive["mean_Signy_minus_other_fixed_25km_cell_SIC_pp"],
            10.97786900584795,abs_tol=1e-7):
        raise ValueError("2013 previous original fixed-pixel positive control not reproduced")
    return source_tag,island_day,matched,fixed_rows,fixedcontrast,totals,{
        "status":"THREE_SAME_SPECIES_ISLAND_YEAR_ORIGINAL_GPS_DAILY_SIC_GENERALITY_AUDIT",
        "source_DOI_GPS":src.GPS_DOI,"source_DOI_SIC":src.DOI,
        "source_three_pairs":list(PAIRS),
        "GPS_source_dates_frozen_without_SIC":True,
        "source_shared_calendar_days":{f"{y}_{o}":pairdates[y,o] for y,o in PAIRS},
        "n_original_source_netCDF_days":len(all_dates),
        "n_original_tag_day_geo_quality_rows":len(source_tag),
        "n_island_day_sensitivity_rows":len(island_day),
        "n_matched_site_day_sensitivity_rows":len(matched),
        "n_fixed_original_ocean_pixel_day_rows":len(fixed_rows),
        "n_fixed_island_contrast_rows":len(fixedcontrast),
        "n_fixed_footprint_month_summary_rows":len(totals),
        "selected_2013_published_result_matched_as_positive_control":True,
        "new_years_2011_2015_have_prespecified_source_day_support_only":True,
        "warnings":[
            "Year 2013 was a post hoc chosen positive case, not a randomly replicated island contrast.",
            "The additional year 2011 and 2015 island counterparts also differ; no island fixed effect identified.",
            "Only actual GPS-matched calendar dates enter the daily satellite comparison; missing days are not zero ice.",
            "Fixed pixel footprints retrospectively use all source GPS days, so GIS area and ice sample support are not causal navigable habitat.",
            "Original OSI-450-a1 25km satellite SIC daily 24h mean, not the ice present at precise animal movement or true route passability.",
            "Multiple tags and adjacent satellite cells share spatial and temporal covariance; no independent climatic sample size inflation.",
            "Published Freer krill GAM already trained ice, salinity and IMR acoustics; satellite SIC source does not validate climate→prey causality.",
            "No penguin breeding output, N_eff, plant succession or future 2050/2100 demographic forecast tested."
        ]}

def write(path,rows):
    if not rows:return
    with Path(path).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--gps",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--phase",required=True,choices=("discover","fetch","analyze"))
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    locations,dates,receipt=original_source_days(a.gps)
    if a.phase=="discover":
        (a.out/"source_frozen_GPS_three_pair_dates.json").write_text(
            json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
        print("GPS_FROZEN_THREE_PAIRS="+json.dumps(receipt,ensure_ascii=False))
    elif a.phase=="fetch":
        old=json.loads((a.out/"source_frozen_GPS_three_pair_dates.json").read_text())
        if old["unique_calendar_dates"]!=receipt["unique_calendar_dates"]:
            raise ValueError("Source GPS dates drifted after freezing")
        source=fetch_daily(dates,a.out/"daily_original_NetCDF")
        (a.out/"source_daily_ice_download_receipts.json").write_text(
            json.dumps(source,indent=2,ensure_ascii=False)+"\n")
        print(json.dumps({"downloaded_daily_source_files":len(source["source_original_daily_netcdfs"]),
                          "dates":old["unique_calendar_dates"]}))
    else:
        orig=json.loads((a.out/"source_daily_ice_download_receipts.json").read_text())
        tag,site,pairs,px,cp,tot,result=valid_cell_means(locations,dates,orig,a.out/"daily_original_NetCDF")
        write(a.out/"source_3pair_tag_daily_SIC.csv",tag)
        write(a.out/"source_3pair_site_daily_SIC.csv",site)
        write(a.out/"source_3pair_matched_daily_SIC.csv",pairs)
        write(a.out/"source_3pair_fixed_pixels_SIC.csv",px)
        write(a.out/"source_3pair_fixed_pixel_daily_contrast.csv",cp)
        write(a.out/"source_3pair_fixed_pixel_month_summary.csv",tot)
        (a.out/"decision.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
        print("THREE_PAIR_SOURCE_RESULT="+json.dumps({
            "status":result["status"],"calendar_days":result["source_shared_calendar_days"],
            "n_netCDF":result["n_original_source_netCDF_days"],
            "fixed_pixel_month_results":tot
        },ensure_ascii=False))
if __name__=="__main__":main()
