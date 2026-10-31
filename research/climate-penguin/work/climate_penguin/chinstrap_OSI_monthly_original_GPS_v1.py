"""Match original Chinstrap GPS source months to independent satellite SIC.

Source OSI SAF OSI-450-a1 v3.1 monthly satellite ice concentration (%).
GPS fixes are observed movement, not confirmed diving/feeding; OSI monthly
25 km EASE2 estimates are NOT ice at exact GPS time nor navigability.
Freer krill GAM has already used ice/salinity/acoustic; do not double-count.
"""
from __future__ import annotations
import argparse,csv,datetime as dt,hashlib,json,math
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
import xarray as xr
from scipy.spatial import cKDTree
import south_orkney_chinstrap_island_krill_v1 as island
import signy_gps_krill_access_v1 as gpslib
import seaice_monthly_source_v4 as osi

DOI="10.15770/EUM_SAF_OSI_0023"
PROD="osi-450-a1"
VERSION="3.1"
RADII=(20.,35.)
THRESHOLDS=(15.,30.)
EXPECTED_GPS=(308,253,7)

def gps_source(file):
    tracks,qa=island.read_all_chinstrap(file)
    centers=island.island_source_centers(tracks)
    selected=[]
    months=set()
    for r in tracks:
        z=centers[r["island"],r["season"]]
        points=r["points"]
        lat=np.array([p[1] for p in points])
        lon=np.array([p[2] for p in points])
        distance=gpslib.geodesic(lat,lon,z["center_lat"],z["center_lon"])
        bad=gpslib.singleton_spike_mask(points)
        ok=(distance>=10)&(distance<=150)&(~bad)
        hourly=gpslib.selected_hourly([points[i] for i in np.flatnonzero(ok)])
        qualified=len(hourly)>=10
        if qualified:months.update((p[0].year,p[0].month) for p in hourly)
        selected.append({"site":r["island"],"season":r["season"],
                         "tag":r["deployment"],"hourly":hourly if qualified else [],
                         "qualified":qualified})
    if (len(tracks),sum(x["qualified"] for x in selected),len(centers))!=EXPECTED_GPS:
        raise ValueError("Original source GPS roster 308/253/7 changed")
    if not 1<=len(months)<=24 or any(y<2011 or y>2020 for y,m in months):
        raise ValueError("Unexpected original penguin source months")
    return selected,sorted(months),qa

def download(months,folder):
    raw=osi.get(osi.ROOT,4_000_000)
    root=osi.catalog(raw,osi.ROOT)
    files=list(root["datasets"])
    catalog=[{"url":osi.ROOT,"sha256":hashlib.sha256(raw).hexdigest()}]
    years=sorted({y for y,m in months})
    refs=osi.needed_refs(root["refs"],years)
    if len(refs)!=len(years):raise ValueError("OSI monthly catalog year discovery incomplete")
    for url in refs:
        raw=osi.get(url,4_000_000)
        contents=osi.catalog(raw,url)
        files.extend(contents["datasets"])
        catalog.append({"url":url,"sha256":hashlib.sha256(raw).hexdigest()})
    jobs=[(y,m,"https://thredds.met.no/thredds/fileServer/"+
           osi.choose_file(files,y,m)) for y,m in months]
    def get(job):
        y,m,url=job
        raw=osi.get(url,osi.MAX_BYTES)
        if not raw.startswith((b"CDF",b"\x89HDF")):
            raise ValueError("Original OSI file is not NetCDF")
        name="original_OSI_%04d%02d.nc"%(y,m)
        (folder/name).write_bytes(raw)
        return {"year":y,"month":m,"source_url":url,"file":name,
                "bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
    with ThreadPoolExecutor(max_workers=3) as pool:receipt=list(pool.map(get,jobs))
    return {"source_DOI":DOI,"product":PROD,"version":VERSION,
            "catalogues":catalog,"original_source_month_files":receipt}

def xyz(lat,lon):
    phi=np.deg2rad(np.asarray(lat,dtype=float))
    th=np.deg2rad(np.asarray(lon,dtype=float))
    return np.column_stack([np.cos(phi)*np.cos(th),np.cos(phi)*np.sin(th),np.sin(phi)])

def source_month(path,receipt):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=receipt["sha256"]:
        raise ValueError("Original OSI NetCDF source SHA mismatch")
    y,m=receipt["year"],receipt["month"]
    with xr.open_dataset(path) as ds:
        a=ds.attrs
        if (a.get("product_id"),str(a.get("product_version")),a.get("doi"))!=(PROD,VERSION,DOI):
            raise ValueError("Original publisher product/version/DOI drift")
        endyear,endmonth=(y+1,1) if m==12 else (y,m+1)
        if (a.get("time_coverage_start"),a.get("time_coverage_end"))!=(
            f"{y:04d}-{m:02d}-01T00:00:00Z",
            f"{endyear:04d}-{endmonth:02d}-01T00:00:00Z"):
            raise ValueError("Original source calendar time boundaries mismatch")
        if ds["ice_conc"].attrs.get("units")!="%":
            raise ValueError("OSI source sea ice not percent")
        if list(ds["status_flag"].attrs["flag_masks"])!=[1,2,4,8,16,32,64,128]:
            raise ValueError("OSI official quality flags changed")
        sic=ds["ice_conc"].values[0].astype(float).ravel()
        flag=ds["status_flag"].values[0].astype(float).ravel()
        lat=ds["lat"].values.astype(float).ravel()
        lon=ds["lon"].values.astype(float).ravel()
    if any(x.size!=432**2 for x in (sic,flag,lat,lon)):
        raise ValueError("OSI 432x432 Southern grid changed")
    good=np.isfinite(flag)&(flag>=0)&(flag<=32767)
    bits=np.where(good,flag,3).astype(np.int32)
    marine=good&((bits&3)==0)&np.isfinite(lat)&np.isfinite(lon)
    valid=marine&np.isfinite(sic)&(sic>=0)&(sic<=100.0001)
    strict=valid&((bits&(8|16|32|64|128))==0)
    if valid.sum()<1000:raise ValueError("Original monthly marine source support insufficient")
    out={"sic":sic,"flags":bits}
    for name,mask in (("all",valid),("strict",strict)):
        idx=np.flatnonzero(mask)
        out[name+"_idx"]=idx
        out[name+"_tree"]=cKDTree(xyz(lat[idx],lon[idx])) if idx.size else None
    return out

def match_month(month,lat,lon,limit,strict):
    key="strict" if strict else "all"
    tree=month[key+"_tree"]
    if tree is None:return [(None,None,None) for _ in lat]
    d,p=tree.query(xyz(lat,lon))
    distance=12742.0176*np.arcsin(np.clip(d/2,0,1))
    idx=month[key+"_idx"][p]
    return [(float(month["sic"][idx[i]]) if distance[i]<=limit else None,
             float(distance[i]),
             int(month["flags"][idx[i]]) if distance[i]<=limit else None)
            for i in range(len(lat))]

def analyze(gps_zip,root,receipt):
    tags,months,gpsqa=gps_source(gps_zip)
    files={(r["year"],r["month"]):r for r in receipt["original_source_month_files"]}
    if set(files)!=set(months):raise ValueError("Missing source GPS month satellite NetCDF")
    ocean={k:source_month(root/files[k]["file"],files[k]) for k in months}
    rows=[]
    for tag in tags:
        if not tag["qualified"]:continue
        bymonth=defaultdict(list)
        for p in tag["hourly"]:
            bymonth[p[0].year,p[0].month].append(p)
        for (y,m),positions in sorted(bymonth.items()):
            lat=np.array([x[1] for x in positions])
            lon=np.array([x[2] for x in positions])
            for limit in RADII:
                for strict in (False,True):
                    hits=match_month(ocean[y,m],lat,lon,limit,strict)
                    valid=[x for x in hits if x[0] is not None]
                    values=np.array([x[0] for x in valid],dtype=float)
                    rows.append({
                      "site":tag["site"],"breeding_season":tag["season"],
                      "original_source_tag":tag["tag"],
                      "source_year":y,"source_month":m,
                      "original_GPS_source_hours_in_month":len(positions),
                      "nearest_monthly_satellite_ocean_radius_km":limit,
                      "strict_publisher_quality_flags":strict,
                      "n_GPS_hours_with_valid_source_sic":len(valid),
                      "source_gps_satellite_coverage_fraction":len(valid)/len(positions),
                      "mean_observed_monthly_SIC_percent_at_GPS":float(values.mean()) if valid else None,
                      "fraction_matched_hours_with_monthly_SIC_ge15":float(np.mean(values>=15)) if valid else None,
                      "fraction_matched_hours_with_monthly_SIC_ge30":float(np.mean(values>=30)) if valid else None,
                      "n_source_landspill_bit8":sum((x[2]&8)!=0 for x in valid),
                      "n_source_interpolation_bits32_64":sum((x[2]&96)!=0 for x in valid),
                      "median_distance_to_satellite_ocean_cell_km":float(np.median([x[1] for x in valid])) if valid else None,
                      "satellite_month_average_not_observed_day_or_true_nav":True
                    })
    groups=defaultdict(list)
    for r in rows:
        key=(r["site"],r["breeding_season"],r["source_year"],r["source_month"],
             r["nearest_monthly_satellite_ocean_radius_km"],r["strict_publisher_quality_flags"])
        groups[key].append(r)
    summary=[]
    for key,records in sorted(groups.items()):
        match=[r for r in records if r["mean_observed_monthly_SIC_percent_at_GPS"] is not None]
        summary.append({
            "island":key[0],"breeding_season":key[1],
            "GPS_calendar_month":f"{key[2]:04d}-{key[3]:02d}",
            "nearest_satellite_limit_km":key[4],"strict_quality":key[5],
            "source_tags_in_this_month":len(records),
            "source_tags_satellite_matched":len(match),
            "source_hourly_GPS_n":sum(r["original_GPS_source_hours_in_month"] for r in records),
            "source_hourly_ocean_SIC_matched_n":sum(r["n_GPS_hours_with_valid_source_sic"] for r in records),
            "equal_tag_mean_monthly_SIC_percent":float(np.mean([r["mean_observed_monthly_SIC_percent_at_GPS"] for r in match])) if match else None,
            "equal_tag_fraction_GPS_hours_SIC_ge15":float(np.mean([r["fraction_matched_hours_with_monthly_SIC_ge15"] for r in match])) if match else None,
            "observation_not_independent_climate_replicate":True
        })
    pairs=[]
    by={(r["island"],r["breeding_season"],r["GPS_calendar_month"],
         r["nearest_satellite_limit_km"],r["strict_quality"]):r for r in summary}
    for year,other in island.PAIRS:
        for limit in RADII:
            for strict in (False,True):
                months_a={r["GPS_calendar_month"] for r in summary if r["island"]=="SI" and r["breeding_season"]==year
                          and r["nearest_satellite_limit_km"]==limit and r["strict_quality"]==strict}
                months_b={r["GPS_calendar_month"] for r in summary if r["island"]==other and r["breeding_season"]==year
                          and r["nearest_satellite_limit_km"]==limit and r["strict_quality"]==strict}
                for month in sorted(months_a&months_b):
                    a=by["SI",year,month,limit,strict]
                    b=by[other,year,month,limit,strict]
                    u=a["equal_tag_mean_monthly_SIC_percent"]
                    v=b["equal_tag_mean_monthly_SIC_percent"]
                    pairs.append({"season":year,"other_island":other,
                         "source_GPS_calendar_month":month,"nearest_source_radius_km":limit,
                         "strict_satellite_quality":strict,
                         "Signy_GPS_deployments_with_source":a["source_tags_satellite_matched"],
                         "other_GPS_deployments_with_source":b["source_tags_satellite_matched"],
                         "Signy_mean_original_OSI_SIC_percent":u,
                         "other_mean_original_OSI_SIC_percent":v,
                         "other_minus_Signy_monthly_SIC_percentage_points":v-u if u is not None and v is not None else None,
                         "not_daily_ice_passability":True})
    result={"status":"SOURCE_GPS_MONTHLY_OBSERVED_SATELLITE_SIC_COLOCATION_NOT_ICE_ACCESS",
            "source_SIC_DOI":DOI,"source_GPS_DOI":"10.5285/8f8ccba5-01af-4b00-8a3b-c3c85b24bf92",
            "source_SIC_months":months,"n_original_source_GPS_tracks":len(tags),
            "n_GPS_qualified_tracks":sum(t["qualified"] for t in tags),
            "n_original_satellite_NetCDF_month_files":len(files),
            "n_tag_month_geo_quality_rows":len(rows),"n_island_year_month_geo_quality_rows":len(summary),
            "n_same_species_same_year_month_pairs":len(pairs),
            "satellite_not_daily_GPS_timestamp_condition":True,
            "no_true_route_ice_barrier_or_prey_observation":True,
            "limitations":[
              "OSI monthly 25 km EASE2 mean is not ice at actual GPS date or fine-scale navigability.",
              "Coastal interpolation and microwave resolution affect which marine cells have valid SIC.",
              "The SIC CDR includes ERA5 ancillary forcing and is not fully independent of physical reanalyses.",
              "Multiple GPS tracks share original satellite ocean pixels; distinct ocean samples NOT equal source tracks.",
              "The original Freer krill GAM used sea ice and salinity and acoustic data, so combining these is not independent ice-to-prey effect validation.",
              "BAS GPS fixes are movement, not confirmed at-sea foraging/capture.",
              "Island and year confounding, dynamic exposure and logger coverage unresolved.",
              "No quantitative breeding count, N_eff or vegetation forecast for 2050/2100 validated."
            ]}
    return rows,summary,pairs,result

def save(path,rows):
    if not rows:raise ValueError("no original source data to write")
    with Path(path).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--gps",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--phase",required=True,choices=("discover","fetch","evaluate"))
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    _,months,_=gps_source(a.gps)
    if a.phase=="discover":
        x={"status":"GPS_SOURCE_MONTHS_ONLY","months":[{"year":y,"month":m} for y,m in months],
           "n_valid_original_GPS_tracks":253}
        (a.out/"gps_calendar_months.json").write_text(json.dumps(x,indent=2)+"\n")
        print(json.dumps(x))
    elif a.phase=="fetch":
        folder=a.out/"original_OSI_monthly"
        folder.mkdir(exist_ok=True)
        receipt=download(months,folder)
        (a.out/"satellite_original_receipts.json").write_text(json.dumps(receipt,indent=2)+"\n")
        print(json.dumps({"downloaded_months":len(receipt["original_source_month_files"]),"months":months,"DOI":DOI}))
    else:
        receipt=json.loads((a.out/"satellite_original_receipts.json").read_text())
        rows,site,pairs,decision=analyze(a.gps,a.out/"original_OSI_monthly",receipt)
        save(a.out/"original_GPS_tag_month_SIC.csv",rows)
        save(a.out/"original_island_year_month_SIC.csv",site)
        if pairs:save(a.out/"original_same_year_island_month_SIC.csv",pairs)
        (a.out/"decision.json").write_text(json.dumps(decision,indent=2)+"\n")
        subset=[r for r in site if r["nearest_satellite_limit_km"]==20 and not r["strict_quality"]]
        print(json.dumps({"status":decision["status"],"months":months,
           "island_month_SIC":[{k:r[k] for k in (
             "island","breeding_season","GPS_calendar_month","source_tags_satellite_matched",
             "equal_tag_mean_monthly_SIC_percent","equal_tag_fraction_GPS_hours_SIC_ge15")}
             for r in subset],
           "same_year_pairs":[r for r in pairs if r["nearest_source_radius_km"]==20
               and not r["strict_satellite_quality"]]},ensure_ascii=False))
if __name__=="__main__":main()
