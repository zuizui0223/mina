"""Same-calendar-day original Chinstrap GPS x OSI SAF 25-km daily SIC, SI vs PI.

First fix shared dates BEFORE opening ice. Satellite 24h averaged SIC is not
ice at a GPS timestamp or physical navigability; tags/cells not independent.
Only the source-selected 2013/14 South Orkney island pair is examined here.
"""
from __future__ import annotations
import argparse,csv,datetime as dt,hashlib,json,math
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import xarray as xr
from scipy.spatial import cKDTree
import south_orkney_chinstrap_island_krill_v1 as tracks
import signy_gps_krill_access_v1 as geo
import osi_daily_source_catalog_probe_v1 as archive

DOI="10.15770/EUM_SAF_OSI_0023"
GPS_DOI="10.5285/8f8ccba5-01af-4b00-8a3b-c3c85b24bf92"
SITES=("SI","PI")
RADII=(20.,35.)
MIN_HOURS=(1,3,6)
PREFIX="osisaf/met.no/reprocessed/ice/conc_450a1_files"
SERVER="https://thredds.met.no/thredds/"
MONTHS=((2013,12),(2014,1))

def positions(source):
    source_tracks,source_qc=tracks.read_all_chinstrap(source)
    origins=tracks.island_source_centers(source_tracks)
    tagdates={}
    qualified=0
    for track in source_tracks:
        site,year=track["island"],track["season"]
        fixes=track["points"]
        origin=origins[site,year]
        la=np.array([p[1] for p in fixes])
        lo=np.array([p[2] for p in fixes])
        km=geo.geodesic(la,lo,origin["center_lat"],origin["center_lon"])
        bad=geo.singleton_spike_mask(fixes)
        keep=(km>=10)&(km<=150)&(~bad)
        hourly=geo.selected_hourly([fixes[i] for i in np.flatnonzero(keep)])
        qualified+=int(len(hourly)>=10)
        if site not in SITES or year!=2013 or len(hourly)<10:continue
        for p in hourly:
            day=p[0].strftime("%Y%m%d")
            if (int(day[:4]),int(day[4:6])) not in MONTHS:continue
            tagdates.setdefault((site,track["deployment"],day),[]).append((p[1],p[2]))
    if len(source_tracks)!=308 or qualified!=253:
        raise ValueError("BAS original GPS 308/253 source roster drift")
    bysite=defaultdict(set)
    for site,tag,day in tagdates:
        bysite[site].add(day)
    dates=sorted(bysite["SI"]&bysite["PI"])
    if not dates or len(dates)>62:
        raise ValueError("No valid same-source-GPS-calendar-date support")
    freeze={
      "status":"FROZEN_SHARED_ORIGINAL_GPS_DATES_BEFORE_ICE",
      "source_GPS_DOI":GPS_DOI,
      "original_GPS_member_digest":source_qc["source_original_313_csv_sha256"],
      "original_GPS_n":len(source_tracks),"qualified_original_GPS_n":qualified,
      "source_sites":SITES,"source_year":2013,
      "same_day_source_dates":dates,
      "support":[{"day":d,**{s:sum(k[0]==s and k[2]==d for k in tagdates) for s in SITES}}
                for d in dates],
      "source_time_zone":"native DateTime date, no inferred offset",
      "satellite_ice_examined_for_day_selection":False}
    return tagdates,dates,freeze

def collect(dates,folder):
    cats=[]
    listing=[]
    for yr,mo in sorted({(int(d[:4]),int(d[4:6])) for d in dates}):
        url=SERVER+"catalog/"+PREFIX+f"/{yr}/{mo:02d}/catalog.xml"
        content=archive.fetch(url,4_000_000)
        refs,entries=archive.catalog(content,url)
        listing+=entries
        cats.append({"url":url,"sha256":hashlib.sha256(content).hexdigest(),
                     "source_entries":len(entries)})
    exact=[]
    for day in dates:
        target=f"ice_conc_sh_ease2-250_cdr-v3p1_{day}1200.nc"
        found=[r["url_path"] for r in listing if Path(r["url_path"]).name==target]
        if len(found)!=1 or not found[0].startswith(PREFIX+"/"):
            raise ValueError("Daily product name not uniquely present in actual catalogue "+day)
        exact.append((day,SERVER+"fileServer/"+found[0]))
    folder.mkdir(parents=True,exist_ok=True)
    def fetch(info):
        day,url=info
        content=archive.fetch(url,archive.MAX_NETCDF_BYTES)
        if not content.startswith((b"CDF",b"\x89HDF")):
            raise ValueError("Original OSI source is not NetCDF")
        name=day+".nc"
        (folder/name).write_bytes(content)
        return {"date":day,"url":url,"file":name,"bytes":len(content),
                "sha256":hashlib.sha256(content).hexdigest()}
    with ThreadPoolExecutor(max_workers=4) as pool:
        records=list(pool.map(fetch,exact))
    return {"status":"ORIGINAL_DAILY_SIC_SOURCES_DOWNLOADED","DOI":DOI,
            "catalogue_sha_receipts":cats,"source_original_daily_netcdfs":records}

def unit_xyz(lat,lon):
    a=np.deg2rad(np.asarray(lat,dtype=float))
    b=np.deg2rad(np.asarray(lon,dtype=float))
    return np.column_stack((np.cos(a)*np.cos(b),np.cos(a)*np.sin(b),np.sin(a)))

def open_day(filename,receipt):
    data=Path(filename).read_bytes()
    if hashlib.sha256(data).hexdigest()!=receipt["sha256"]:
        raise ValueError("Source daily bytes do not match download receipt")
    day=receipt["date"]
    t=dt.datetime.strptime(day,"%Y%m%d")
    nextday=t+dt.timedelta(days=1)
    with xr.open_dataset(filename) as ds:
        a=ds.attrs
        if (a.get("product_id"),str(a.get("product_version")),a.get("doi"))!=(
            "osi-450-a1","3.1",DOI):
            raise ValueError("Original publisher daily product/DOI mismatch")
        if (a.get("time_coverage_start"),a.get("time_coverage_end"))!=(
            t.strftime("%Y-%m-%dT00:00:00Z"),nextday.strftime("%Y-%m-%dT00:00:00Z")):
            raise ValueError("Satellite day does not match original GPS calendar date")
        if ds["ice_conc"].attrs.get("units")!="%":
            raise ValueError("Satellite SIC source unit not percentage")
        if list(ds["status_flag"].attrs["flag_masks"])!=[1,2,4,8,16,32,64,128]:
            raise ValueError("Original source flag meaning changed")
        sic=np.asarray(ds["ice_conc"].values[0],dtype=float).ravel()
        flag=np.asarray(ds["status_flag"].values[0],dtype=float).ravel()
        lat=np.asarray(ds["lat"].values,dtype=float).ravel()
        lon=np.asarray(ds["lon"].values,dtype=float).ravel()
    if any(x.size!=432**2 for x in (sic,flag,lat,lon)):
        raise ValueError("Original EASE2 Antarctic native 432x432 grid drift")
    good=np.isfinite(flag)&(flag>=0)&(flag<=32767)
    bits=np.where(good,flag,3).astype(int)
    valid=good&((bits&3)==0)&np.isfinite(lat)&np.isfinite(lon)
    valid &=np.isfinite(sic)&(sic>=0)&(sic<=100.0001)
    strict=valid&((bits&(8|16|32|64|128))==0)
    if valid.sum()<1000:raise ValueError("No original source ocean satellite pixels")
    out={"values":sic}
    for label,mask in (("all",valid),("strict",strict)):
        idx=np.flatnonzero(mask)
        out[label+"_ids"]=idx
        out[label+"_tree"]=cKDTree(unit_xyz(lat[idx],lon[idx])) if idx.size else None
    return out

def sample(day,locations,radius,strict):
    suffix="strict" if strict else "all"
    tree=day[suffix+"_tree"]
    if tree is None:return {}
    distance,indices=tree.query(unit_xyz(
        [x[0] for x in locations],[x[1] for x in locations]))
    km=12742.0176*np.arcsin(np.clip(np.asarray(distance)/2,0,1))
    sourceids=day[suffix+"_ids"][np.asarray(indices)]
    observations={}
    for i,pixel in enumerate(sourceids):
        if km[i]>radius:continue
        value=float(day["values"][pixel])
        observations.setdefault(int(pixel),value)
        if not math.isclose(observations[int(pixel)],value,abs_tol=1e-10):
            raise ValueError("Source pixel value internally inconsistent")
    return observations

def evaluate(source_positions,shared,receipt,folder):
    entries={r["date"]:r for r in receipt["source_original_daily_netcdfs"]}
    if set(entries)!=set(shared):raise ValueError("Missing actual source GPS shared day in downloaded NetCDF")
    rows=[]
    for date in shared:
        ds=open_day(folder/entries[date]["file"],entries[date])
        for (site,tag,day),locations in source_positions.items():
            if day!=date:continue
            for radius in RADII:
                for strict in (False,True):
                    # exact source GPS day >0-hour filters remain explicit below
                    pixels=sample(ds,locations,radius,strict)
                    rows.append({
                      "calendar_date":date,"island":site,"original_GPS_tag":tag,
                      "source_hourly_GPS_fixes":len(locations),
                      "max_source_pixel_distance_km":radius,
                      "strict_ice_quality":strict,
                      "n_original_valid_satellite_cells":len(pixels),
                      "original_pixel_values_json":json.dumps(pixels,sort_keys=True),
                      "per_tag_pixel_mean_SIC_percent":(
                        float(np.mean(list(pixels.values()))) if pixels else None),
                      "source_daily_is_24_hour_average_not_instant_ice":True
                    })
    grouping=defaultdict(list)
    for row in rows:
        grouping[row["calendar_date"],row["island"],row["max_source_pixel_distance_km"],
                 row["strict_ice_quality"]].append(row)
    site_days=[]
    for (day,site,radius,strict),records in sorted(grouping.items()):
        for min_hour in MIN_HOURS:
            accepted=[r for r in records if r["source_hourly_GPS_fixes"]>=min_hour and
                      r["n_original_valid_satellite_cells"]>0]
            pixels={}
            for r in accepted:
                for pix,v in json.loads(r["original_pixel_values_json"]).items():
                    pix=int(pix);v=float(v)
                    if pix in pixels and not math.isclose(pixels[pix],v,abs_tol=1e-10):
                        raise ValueError("Two GPS tags conflict on one original satellite pixel")
                    pixels[pix]=v
            site_days.append({
                "calendar_date":day,"island":site,
                "max_satellite_ocean_cell_distance_km":radius,
                "strict_source_flags":strict,"minimum_tag_hourly_GPS_fixes":min_hour,
                "n_source_GPS_tags":len(records),
                "n_source_GPS_tags_with_valid_satellite":len(accepted),
                "n_original_unique_satellite_ocean_pixels":len(pixels),
                "n_original_ocean_pixels_SIC_ge15":sum(v>=15 for v in pixels.values()),
                "mean_of_source_tag_pixel_means_SIC_percent":float(np.mean(
                    [r["per_tag_pixel_mean_SIC_percent"] for r in accepted])) if accepted else None,
                "unique_source_ocean_pixel_mean_SIC_percent":float(np.mean(
                    list(pixels.values()))) if pixels else None,
                "same_original_satellite_pixel_counted_only_once":True
            })
    lookup={(z["calendar_date"],z["island"],z["max_satellite_ocean_cell_distance_km"],
            z["strict_source_flags"],z["minimum_tag_hourly_GPS_fixes"]):z for z in site_days}
    paired=[]
    for date in shared:
        for radius in RADII:
            for strict in (False,True):
                for min_hour in MIN_HOURS:
                    si=lookup[date,"SI",radius,strict,min_hour]
                    pi=lookup[date,"PI",radius,strict,min_hour]
                    a=si["mean_of_source_tag_pixel_means_SIC_percent"]
                    b=pi["mean_of_source_tag_pixel_means_SIC_percent"]
                    c=si["unique_source_ocean_pixel_mean_SIC_percent"]
                    d=pi["unique_source_ocean_pixel_mean_SIC_percent"]
                    paired.append({
                        "source_same_GPS_calendar_date":date,"radius_km":radius,
                        "strict_source_flags":strict,"min_tag_hours":min_hour,
                        "n_Signy_tags_with_satellite":si["n_source_GPS_tags_with_valid_satellite"],
                        "n_Powell_tags_with_satellite":pi["n_source_GPS_tags_with_valid_satellite"],
                        "n_Signy_distinct_ocean_pixels":si["n_original_unique_satellite_ocean_pixels"],
                        "n_Powell_distinct_ocean_pixels":pi["n_original_unique_satellite_ocean_pixels"],
                        "Signy_tag_equal_SIC_percent":a,"Powell_tag_equal_SIC_percent":b,
                        "Signy_unique_pixel_SIC_percent":c,"Powell_unique_pixel_SIC_percent":d,
                        "Signy_minus_Powell_tag_mean_pp":a-b if a is not None and b is not None else None,
                        "Signy_minus_Powell_unique_pixel_pp":c-d if c is not None and d is not None else None,
                        "both_islands_observed_valid_SIC":a is not None and b is not None,
                        "same_day_source_SIC_not_daily_migration_obstacle":True
                    })
    if len(paired)!=len(shared)*len(RADII)*2*len(MIN_HOURS):
        raise ValueError("Fixed same-day source date/sensitivity grid incomplete")
    primary=[r for r in paired if r["radius_km"]==20 and
             not r["strict_source_flags"] and r["min_tag_hours"]==1 and
             r["both_islands_observed_valid_SIC"]]
    if not primary:raise ValueError("No source same-day matched valid satellite SIC comparison")
    dec=[r for r in primary if r["source_same_GPS_calendar_date"].startswith("201312")]
    jan=[r for r in primary if r["source_same_GPS_calendar_date"].startswith("201401")]
    summary={
       "status":"SOURCE_SAME_CALENDAR_DAY_GPS_OSI_SAF_DAILY_ICE_DESCRIPTIVE",
       "original_GPS_DOI":GPS_DOI,"original_SIC_DOI":DOI,
       "n_original_shared_GPS_days_before_SIC":len(shared),
       "n_original_southern_daily_NetCDF":len(entries),
       "n_SI_PI_comparable_daily_SIC_dates":len(primary),
       "n_comparable_December_2013_dates":len(dec),
       "n_comparable_January_2014_dates":len(jan),
       "primary_same_day_comparisons":primary,
       "source_sensitivity_count_per_shared_day":len(RADII)*2*len(MIN_HOURS),
       "mean_daily_Signy_minus_Powell_tag_SIC_pp_Dec":float(np.mean(
           [r["Signy_minus_Powell_tag_mean_pp"] for r in dec])) if dec else None,
       "mean_daily_Signy_minus_Powell_tag_SIC_pp_Jan":float(np.mean(
           [r["Signy_minus_Powell_tag_mean_pp"] for r in jan])) if jan else None,
       "mean_daily_Signy_minus_Powell_native_pixel_pp_Dec":float(np.mean(
           [r["Signy_minus_Powell_unique_pixel_pp"] for r in dec])) if dec else None,
       "mean_daily_Signy_minus_Powell_native_pixel_pp_Jan":float(np.mean(
           [r["Signy_minus_Powell_unique_pixel_pp"] for r in jan])) if jan else None,
       "original_SIC_is_24h_satellite_mean_not_direct_ice_navigability":True,
       "no_krill_dive_capture_or_future_nesting_effect_estimated":True,
       "limitations":[
        "GPS native calendar date timezone is not externally checked; do not infer subdaily ocean ice.",
        "OSI satellite 25-km 24-hour average SIC not measured ice barrier or access at animal position and time.",
        "Satellite coastline/gap/flag bias and marine nearest-pixel radius matter, so missing SIC stays NA.",
        "Several birds can share the same source ocean pixel; 25-km cells are spatially autocorrelated.",
        "SIC contrast at one breeding season was selected post hoc from earlier monthly difference, not independent replication.",
        "Freer prey model was trained on ice/salinity/acoustic data, so do not claim ice-to-prey causal validation.",
        "No climate-driven 2050/2100 penguin nesting pair, effective breeding space or vegetation forecast."
       ]
    }
    return rows,site_days,paired,summary

def write_csv(file,rows):
    if not rows:raise ValueError("No source data")
    with Path(file).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--gps",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    parser.add_argument("--phase",required=True,choices=("discover","fetch","analyze"))
    a=parser.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    tags,dates,frozen=positions(a.gps)
    if a.phase=="discover":
        (a.out/"source_GPS_shared_days_locked.json").write_text(
            json.dumps(frozen,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        print(json.dumps({"status":frozen["status"],"days":dates,
                          "source_support":frozen["support"]},ensure_ascii=False))
    elif a.phase=="fetch":
        old=json.loads((a.out/"source_GPS_shared_days_locked.json").read_text())
        if old["same_day_source_dates"]!=dates:
            raise ValueError("Original source GPS day set changed after ice-freeze")
        result=collect(dates,a.out/"daily_original_NetCDF")
        (a.out/"source_daily_NetCDF_SHA_receipts.json").write_text(
            json.dumps(result,indent=2)+"\n",encoding="utf-8")
        print(json.dumps({"status":result["status"],"n_source_days":len(dates),
                          "source_dates":dates}))
    else:
        records=json.loads((a.out/"source_daily_NetCDF_SHA_receipts.json").read_text())
        tags_out,sites,pairs,decision=evaluate(tags,dates,records,a.out/"daily_original_NetCDF")
        write_csv(a.out/"daily_GPS_tag_original_SIC.csv",tags_out)
        write_csv(a.out/"daily_island_original_SIC.csv",sites)
        write_csv(a.out/"matched_same_day_Signy_Powell_original_SIC.csv",pairs)
        (a.out/"decision.json").write_text(
            json.dumps(decision,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        print(json.dumps(decision,ensure_ascii=False))
if __name__=="__main__":main()
