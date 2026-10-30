"""Same-species, matched-year multi-island chinstrap GPS × published krill GAM.

Original BAS 2025 Chinstrap GPS Version 2.0, DOI 10.5285/8f8ccba5-01af-4b00-8a3b-c3c85b24bf92.
Freer 2025 original 2011–2020 GAM rasters include ice/salinity and IMR
acoustic evidence: NOT independent observed prey or an ecological causal test.
GPS positions are NOT confirmed foraging/capture events; there is no
independently validated ocean-only/land mask or nest origin.
"""
from __future__ import annotations
import argparse,csv,datetime as dt,hashlib,io,json,math,statistics,zipfile
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
import signy_gps_krill_access_v1 as base

ROOT=Path(__file__).resolve().parents[4]
GPS_SHA="f56dc817aefefda41e509541d24a184f68644d12c0a1c28af8071717275101c9"
SITES={"SI":"Signy","LI":"Laurie","PI":"Powell","MI":"Monroe"}
PAIRS=((2011,"LI"),(2013,"PI"),(2015,"MI"))
SENSITIVITY=((5,True),(10,True),(20,True),(10,False))
MAX_KM=150
MIN_HOURS=10

def read_all_chinstrap(source):
    if not zipfile.is_zipfile(source):raise ValueError("original Chinstrap Version 2 ZIP missing")
    original=[]
    qc=Counter()
    digest=hashlib.sha256()
    with zipfile.ZipFile(source) as z:
        names=sorted((n for n in z.namelist() if Path(n).name.endswith(".csv")
                     and "_GPS" in Path(n).name), key=lambda n:Path(n).name)
        if len(names)!=313:raise ValueError("publisher GPS file count changed")
        seen={}
        for member in names:
            raw=z.read(member)
            name=Path(member).name
            sha=hashlib.sha256(raw).digest()
            digest.update(name.encode()+b"\0"+sha)
            deployment=name.split("_")[0]
            site=deployment[:2]
            if site not in SITES or not deployment.startswith(site+"C"):
                raise ValueError("unexpected publisher island/species GPS ID")
            if deployment in seen:
                if seen[deployment]!=sha:raise ValueError("duplicate source deployment not identical")
                qc["identical_duplicate_original_file"]+=1
                continue
            seen[deployment]=sha
            data=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
            if not data:
                qc["empty_original_file"]+=1
                continue
            if not {"DateTime","Latitude_degrees_north","Longitude_degrees_east"}<=set(data[0]):
                raise ValueError("GPS source header drift")
            points=[]
            for i,row in enumerate(data):
                stamp=dt.datetime.fromisoformat(row["DateTime"].replace("Z","+00:00"))
                lat=float(row["Latitude_degrees_north"])
                lon=float(row["Longitude_degrees_east"])
                if not(math.isfinite(lat) and math.isfinite(lon) and -90<lat<-45 and -180<lon<180):
                    raise ValueError("invalid original GPS lat/lon")
                points.append((stamp,lat,lon,i))
            years={t.year if t.month>=7 else t.year-1 for t,_,_,_ in points}
            if len(years)!=1:raise ValueError("GPS deployment spans multiple breeding seasons")
            year=next(iter(years))
            if year not in (2011,2013,2015,2018):
                raise ValueError("unexpected original GPS breeding season")
            points.sort(key=lambda x:(x[0],x[3]))
            ordered=[]
            times=set()
            for p in points:
                if p[0] in times:
                    qc["identical_timestamp_dropped"]+=1
                    continue
                times.add(p[0])
                ordered.append(p)
            original.append({"island":site,"season":year,"deployment":deployment,
                             "points":ordered,"raw_positions":len(points),
                             "source_sha256":sha.hex()})
            qc["unique_nonempty_deployments"]+=1
            qc["source_position_rows"]+=len(points)
    if digest.hexdigest()!=GPS_SHA:
        raise ValueError("original BAS Chinstrap GPS CSV payload drift")
    if len(original)!=308:
        raise ValueError("original nonempty Chinstrap deployments changed")
    return original,{"source_original_313_csv_sha256":digest.hexdigest(),"qc":dict(qc)}

def island_source_centers(source):
    groups=defaultdict(list)
    for r in source:
        # Data source only, not chosen using krill or chick outcomes.
        first=r["points"][0]
        groups[r["island"],r["season"]].append((first[1],first[2]))
    output={}
    for (island,year),locations in sorted(groups.items()):
        lat=np.array([a for a,b in locations])
        lon=np.array([b for a,b in locations])
        center=(float(np.median(lat)),float(np.median(lon)))
        dist=base.geodesic(lat,lon,center[0],center[1])
        output[island,year]={
            "island":island,"season_start":year,
            "center_lat":center[0],"center_lon":center[1],
            "n_original_deployments":len(locations),
            "first_position_distance_to_center_median_km":float(np.median(dist)),
            "first_position_distance_to_center_p90_km":float(np.quantile(dist,.9)),
            "center_is_observed_first_fix_median_not_nest":True}
    expected={("SI",2011):11,("SI",2013):21,("SI",2015):26,("SI",2018):58,
              ("LI",2011):60,("PI",2013):68,("MI",2015):64}
    if {(s,y):z["n_original_deployments"] for (s,y),z in output.items()}!=expected:
        raise ValueError("four islands, seven original island-years count drift")
    return output

def tag_exposures(tracks,centers,models):
    out=[]
    for r in tracks:
        center=centers[r["island"],r["season"]]
        points=r["points"]
        lat=np.array([p[1] for p in points])
        lon=np.array([p[2] for p in points])
        distance=base.geodesic(lat,lon,center["center_lat"],center["center_lon"])
        spike=base.singleton_spike_mask(points)
        for minimum,filtered in SENSITIVITY:
            mask=(distance>=minimum)&(distance<=MAX_KM)
            if filtered:mask &= ~spike
            hour=base.selected_hourly([points[i] for i in np.flatnonzero(mask)])
            row={
                "island":r["island"],"season_start":r["season"],
                "deployment":r["deployment"],
                "original_member_sha256":r["source_sha256"],
                "minimum_island_center_distance_km":minimum,
                "isolated_speed_spikes_removed":filtered,
                "source_positions":r["raw_positions"],
                "detected_singleton_speed_spikes":int(spike.sum()),
                "positions_in_radius":int(mask.sum()),
                "observed_hourly_position_count":len(hour),
                "qualifies_source_hourly_support":len(hour)>=MIN_HOURS,
                "median_selected_distance_from_source_anchor_km":(
                    float(np.median(base.geodesic([x[1] for x in hour],[x[2] for x in hour],
                        center["center_lat"],center["center_lon"]))) if hour else None)}
            for period,year in (("preseason",r["season"]),("same_summer",r["season"]+1)):
                row[period+"_model_year"]=year
                row[period+"_native_model_krill_g_m2"]=None
                row[period+"_model_valid_position_hours"]=0
                row[period+"_distinct_visited_model_cells"]=0
                if not hour:continue
                arr,tr=models[year]
                v,rr,cc=base.sampled_cells(arr,tr,
                    np.array([p[1] for p in hour]),np.array([p[2] for p in hour]))
                good=np.isfinite(v)
                cells=sorted(set(zip(rr[good].tolist(),cc[good].tolist())))
                row[period+"_model_valid_position_hours"]=int(good.sum())
                row[period+"_distinct_visited_model_cells"]=len(cells)
                if cells:row[period+"_native_model_krill_g_m2"]=float(np.mean([arr[i,j] for i,j in cells]))
            out.append(row)
    return out

def aggregate(rows):
    out=[]
    for min_dist,filtered in SENSITIVITY:
        for island,year in sorted({(r["island"],r["season_start"]) for r in rows}):
            entries=[r for r in rows if (r["island"],r["season_start"])==(island,year)
                     and r["minimum_island_center_distance_km"]==min_dist
                     and r["isolated_speed_spikes_removed"]==filtered]
            valid=[r for r in entries if r["qualifies_source_hourly_support"] and
                   r["preseason_native_model_krill_g_m2"] is not None and
                   r["same_summer_native_model_krill_g_m2"] is not None]
            output={
                "island":island,"island_name":SITES[island],"season_start":year,
                "minimum_distance_km":min_dist,"speed_spike_filter":filtered,
                "source_deployments":len(entries),"qualified_deployments":len(valid),
                "source_gps_points":sum(r["source_positions"] for r in entries),
                "qualified_hourly_positions":sum(r["observed_hourly_position_count"] for r in valid),
                "median_of_deployment_median_distance_km":(
                    float(statistics.median(r["median_selected_distance_from_source_anchor_km"] for r in valid))
                    if valid else None),
                "independent_climate_or_krill_regional_samples":1,
                "same_species_Chinstrap_only":True,
                "native_source_GPS_not_confirmed_at_sea":True}
            for period in ("preseason","same_summer"):
                v=[r[period+"_native_model_krill_g_m2"] for r in valid]
                output[period+"_mean_track_equal_model_krill_g_m2"]=(float(statistics.mean(v)) if v else None)
                output[period+"_mean_leave_one_deployment_min"]=(
                    float(min((sum(v)-z)/(len(v)-1) for z in v)) if len(v)>1 else None)
                output[period+"_mean_leave_one_deployment_max"]=(
                    float(max((sum(v)-z)/(len(v)-1) for z in v)) if len(v)>1 else None)
            out.append(output)
    return out

def comparisons(summary):
    idx={(r["island"],r["season_start"],r["minimum_distance_km"],r["speed_spike_filter"]):r
         for r in summary}
    rows=[]
    for year,other in PAIRS:
        for min_d,filtered in SENSITIVITY:
            si=idx["SI",year,min_d,filtered]
            second=idx[other,year,min_d,filtered]
            for period in ("preseason","same_summer"):
                a=si[period+"_mean_track_equal_model_krill_g_m2"]
                b=second[period+"_mean_track_equal_model_krill_g_m2"]
                rows.append({
                    "season_start":year,"island_a":"SI","island_b":other,
                    "minimum_distance_km":min_d,"spike_filter":filtered,
                    "model_year_alignment":period,
                    "n_tag_si":si["qualified_deployments"],
                    "n_tag_other":second["qualified_deployments"],
                    "si_model_g_m2":a,"other_model_g_m2":b,
                    "other_to_signy_model_ratio":b/a if a and b else None,
                    "island_a_vs_island_b_shared_breeding_season":True,
                    "same_species_not_independent_acoustic_measurement":True,
                    "source_site_anchor_not_verified_nest_or_landing":True})
    return rows

def verify(source,centers,summaries,contrasts):
    if len(source)!=308 or len(centers)!=7 or len(summaries)!=28 or len(contrasts)!=24:
        raise ValueError("original island-year or sensitivity roster changed")
    x={(r["island"],r["season_start"]):r for r in summaries
       if r["minimum_distance_km"]==10 and r["speed_spike_filter"]}
    known={
      ("SI",2011):(4,7.580665295104405,12.242522030741304),
      ("LI",2011):(48,18.498181492143335,48.61269805624229),
      ("SI",2013):(19,2.8097541843546616,8.597118848502262),
      ("PI",2013):(56,17.74193988585095,25.62195507189449),
      ("SI",2015):(26,2.9594895679832955,4.916611434696401),
      ("MI",2015):(46,8.131893701509481,9.671855423236291),
      ("SI",2018):(54,2.054,3.77)
    }
    for key,(n,pre,summer) in known.items():
        r=x[key]
        if r["qualified_deployments"]!=n:
            raise ValueError("source site/year qualified track roster changed "+str(key))
        # SI2018 rounded from preliminary independent audit, only check count.
        if key==("SI",2018):continue
        for var,val in (("preseason",pre),("same_summer",summer)):
            if not math.isclose(r[var+"_mean_track_equal_model_krill_g_m2"],val,abs_tol=1e-7):
                raise ValueError("original GPS-published-model value changed "+str((key,var)))
    for yr,site in PAIRS:
        comparison=next(r for r in contrasts if r["season_start"]==yr and r["island_b"]==site
                        and r["minimum_distance_km"]==10 and r["spike_filter"]
                        and r["model_year_alignment"]=="preseason")
        if not comparison["other_to_signy_model_ratio"]>1:
            raise ValueError("source all-three same-year observed-model contrast changed")
    return True

def write(path,values):
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(values[0]))
        w.writeheader();w.writerows(values)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--chinstrap-gps-zip",required=True,type=Path)
    p.add_argument("--krill-zip",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    tracks,qc=read_all_chinstrap(a.chinstrap_gps_zip)
    models=base.source_models(a.krill_zip)
    centers=island_source_centers(tracks)
    source=tag_exposures(tracks,centers,models)
    summary=aggregate(source)
    cross=comparisons(summary)
    if a.check:verify(tracks,centers,summary,cross)
    a.out.mkdir(parents=True,exist_ok=True)
    write(a.out/"source_tag_model_exposures.csv",source)
    write(a.out/"source_island_centers.csv",list(centers.values()))
    write(a.out/"species_island_year.csv",summary)
    write(a.out/"matched_year_island_contrasts.csv",cross)
    decision={
        "status":"EXPLORATORY_SAME_SPECIES_MATCHED_YEAR_ISLAND_GPS_VS_PUBLISHED_GAM",
        "original_source":"BAS Chinstrap Version2 doi:10.5285/8f8ccba5-01af-4b00-8a3b-c3c85b24bf92",
        "gps_original_member_sha256":GPS_SHA,
        "original_source_audit":qc,
        "n_original_nonempty_deployments":len(tracks),
        "n_island_years":len(centers),
        "n_matched_other_island_Signy_years":3,
        "matched_island_years":list(PAIRS),
        "n_predefined_sensitivity_sets":len(SENSITIVITY),
        "original_2013_combined_acoustic_survey_missing":True,
        "year2005_undefined":True,
        "method":{
            "origin_per_island_year":"median of first original GPS fix across original deployments, fixed BEFORE sampling krill raster; not ground-truthed nest",
            "prior_environment":"Freer 2025 modelled Jan-Feb season T before later Dec-Jan T/T+1 breeding tracks",
            "same_summer_model":"model Jan-Feb T+1; not available at T",
            "spike_filter":"drop isolated middle point with both 12m/s edges but plausible shortcut; no guaranteed GPS accuracy",
            "max_distance_km":MAX_KM,"min_distance_km":[5,10,20],
            "n_hours_required":MIN_HOURS,
            "primary":"10-150km, equal unique native raster cells per GPS deployment and equal deployments per island-year"
        },
        "primary_island_years":[r for r in summary if r["minimum_distance_km"]==10 and r["speed_spike_filter"]],
        "primary_3_same_season_island_contrasts":[r for r in cross if r["minimum_distance_km"]==10 and r["spike_filter"]
                                                 and r["model_year_alignment"]=="preseason"],
        "limits":[
            "Species is chinstrap in all island contrasts; spatial model estimates are not independent krill observations.",
            "Only one non-Signy island per matched year: island identity and non-Signy year do not replicate independently.",
            "Signy n=4 in 2011 with >=10h GPS, so 2011 pair is especially unstable.",
            "Origin is robust median of first GPS fix per island and year, not surveyed colony polygon or confirmed landing location.",
            "No land/ocean mask or diving confirmation; source fix at 10km may still not be proven foraging.",
            "Freer GAM itself used IMR acoustic, ice and salinity for all 2011-2020; pre-season T field is not independent validation.",
            "2013 original acoustic Combined value absent; 2013 GAM is reconstructed from source model using environmental covariates and partial surveys.",
            "No other-island original fledgling response is connected, thus no island effect on breeding success can be inferred.",
            "A 3/3 directional contrast is descriptive, not a confirmatory island-level test or p-value.",
            "No validated transfer to 2050/2100 penguin breeding pair counts, N_eff, or greening."
        ]}
    (a.out/"decision.json").write_text(json.dumps(decision,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":decision["status"],"gps":qc,"n_islands":len(centers),
                      "matched":decision["primary_3_same_season_island_contrasts"],
                      "source_verified":bool(a.check)},ensure_ascii=False))

if __name__=="__main__":
    main()
