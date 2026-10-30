"""BAS Signy 3-species GPS × Freer 2025 modelled krill (observational v1).

GPS positions are neither confirmed at-sea foraging nor independent climate
observations. The Freer krill hurdle GAM already used IMR acoustics, sea ice
and salinity. NEVER use these fields for independent climate-causality claims
or calibrated future breeding-population forecasts.
"""
from __future__ import annotations
import argparse,csv,datetime as dt,hashlib,io,json,math,statistics,zipfile
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from rasterio.io import MemoryFile

ROOT=Path(__file__).resolve().parents[4]
TIFF_PINS=ROOT/"research/climate-penguin/inputs/freer_krill_combined_raster_sha_v1.json"
TRACK_SHA="e65a884341346a95ebb4a25de492d350716fde5f5cb77a669d66846811f6800a"
TRACK_FILES={"Adelie":("SIA","adelie.zip",41),
             "Chinstrap":("SIC","chinstrap.zip",121),
             "Gentoo":("SIG","gentoo.zip",11)}
YEARS=tuple(range(2011,2021))
ANCHOR=(-60.704025,-45.6275835)
MAX_KM=150
MIN_HOURS=10
SPIKE_SPEED_M_S=12.0
SENSITIVITY=((5,True),(10,True),(20,True),(10,False))

def readcsv(path):
    with Path(path).open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))

def geodesic(lat,lon,lat0=ANCHOR[0],lon0=ANCHOR[1]):
    la=np.deg2rad(np.asarray(lat,dtype=float))
    lb=np.deg2rad(np.asarray(lat0,dtype=float))
    dlon=np.deg2rad(np.asarray(lon,dtype=float)-np.asarray(lon0,dtype=float))
    z=np.sin((la-lb)/2)**2+np.cos(la)*np.cos(lb)*np.sin(dlon/2)**2
    return 12742.0176*np.arcsin(np.sqrt(np.clip(z,0,1)))

def read_tracks(root):
    tracks=[]
    audit={}
    aggregate=hashlib.sha256()
    for sp,(prefix,source_file,n_expected) in TRACK_FILES.items():
        source=Path(root)/source_file
        if not zipfile.is_zipfile(source):
            raise ValueError("original BAS GPS ZIP invalid "+sp)
        with zipfile.ZipFile(source) as z:
            names=sorted((p for p in z.namelist()
                if Path(p).name.startswith(prefix)
                and "_GPS" in Path(p).name and Path(p).name.endswith(".csv")),
                key=lambda p:Path(p).name)
            if len(names)!=n_expected:raise ValueError("GPS source file roster changed")
            used={}
            quality=Counter()
            for name in names:
                raw=z.read(name)
                basename=Path(name).name
                sha=hashlib.sha256(raw).digest()
                aggregate.update(sp.encode()+b"\0"+basename.encode()+b"\0"+sha)
                deployment=basename.split("_")[0]
                if deployment in used:
                    if used[deployment]!=sha:
                        raise ValueError("conflicting same-deployment original GPS")
                    quality["identical_duplicate_source_file"]+=1
                    continue
                used[deployment]=sha
                rr=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
                if not rr:
                    quality["empty_gps_source_file"]+=1
                    continue
                required={"DateTime","Latitude_degrees_north","Longitude_degrees_east"}
                if not required<=set(rr[0]):raise ValueError("GPS timestamp/coordinate schema changed")
                data=[]
                for i,r in enumerate(rr):
                    time=dt.datetime.fromisoformat(r["DateTime"].replace("Z","+00:00"))
                    lat=float(r["Latitude_degrees_north"])
                    lon=float(r["Longitude_degrees_east"])
                    if not(math.isfinite(lat) and math.isfinite(lon)
                           and -90<lat<-45 and -180<lon<180):
                        raise ValueError("nonfinite/out-of-domain GPS source coordinate")
                    data.append((time,lat,lon,i))
                years={t.year if t.month>=7 else t.year-1 for t,_,_,_ in data}
                if len(years)!=1:raise ValueError("GPS crosses breeding season definitions")
                season=next(iter(years))
                if not 2011<=season<=2019:raise ValueError("unanticipated GPS source season")
                raw_count=len(data)
                data.sort(key=lambda x:(x[0],x[3]))
                seen=set()
                unique=[]
                for r in data:
                    if r[0] in seen:
                        quality["duplicate_timestamp"]+=1
                        continue
                    seen.add(r[0])
                    unique.append(r)
                tracks.append(dict(species=sp,deployment=deployment,season=season,
                                   source_sha256=sha.hex(),
                                   raw_count=raw_count,points=unique))
                quality["usable_deployments"]+=1
                quality["source_position_rows"]+=raw_count
            audit[sp]={"raw_gps_files":len(names),**dict(quality)}
    if aggregate.hexdigest()!=TRACK_SHA:raise ValueError("BAS original GPS contents changed")
    if len(tracks)!=168:raise ValueError("number of unique nonempty source deployments changed")
    return tracks,{"canonical_member_content_sha256":aggregate.hexdigest(),"species":audit}

def singleton_spike_mask(data):
    n=len(data)
    bad=np.zeros(n,dtype=bool)
    if n<3:return bad
    t=np.array([(r[0]-data[0][0]).total_seconds() for r in data])
    if np.any(np.diff(t)<=0):raise ValueError("GPS timestamp sorting failed")
    lat=np.array([r[1] for r in data])
    lon=np.array([r[2] for r in data])
    prev=geodesic(lat[1:],lon[1:],lat[:-1],lon[:-1])*1000/np.diff(t)
    skip=geodesic(lat[2:],lon[2:],lat[:-2],lon[:-2])*1000/(t[2:]-t[:-2])
    bad[1:-1]=(prev[:-1]>SPIKE_SPEED_M_S)&(prev[1:]>SPIKE_SPEED_M_S)&(skip<=SPIKE_SPEED_M_S)
    return bad

def selected_hourly(data):
    groups=defaultdict(list)
    for p in data:
        key=p[0].replace(minute=0,second=0,microsecond=0)
        groups[key].append(p)
    out=[]
    for hour in sorted(groups):
        ordered=sorted(groups[hour],key=lambda x:x[0])
        out.append(ordered[(len(ordered)-1)//2])
    return out

def source_models(path):
    pins=json.loads(TIFF_PINS.read_text(encoding="utf-8"))
    if set(pins)!={f"{y}_predict_combined_mean.tif" for y in YEARS}:
        raise ValueError("model TIFF pin roster changed")
    if not zipfile.is_zipfile(path):raise ValueError("published model ZIP invalid")
    out={}
    with zipfile.ZipFile(path) as z:
        for year in YEARS:
            name=f"{year}_predict_combined_mean.tif"
            paths=[p for p in z.namelist() if Path(p).name==name]
            if len(paths)!=1:raise ValueError("modelled annual source TIFF ambiguous")
            raw=z.read(paths[0])
            if hashlib.sha256(raw).hexdigest()!=pins[name]:
                raise ValueError("original publisher model TIFF checksum changed")
            with MemoryFile(raw) as mf:
                with mf.open() as src:
                    if src.crs.to_epsg()!=4326 or src.count!=1 or src.width!=241 or src.height!=121:
                        raise ValueError("publisher model raster shape/CRS changed")
                    tr=src.transform
                    if not(math.isclose(tr.a,1/12,abs_tol=1e-10) and math.isclose(-tr.e,1/12,abs_tol=1e-10)):
                        raise ValueError("actual source TIFF resolution changed")
                    out[year]=(np.asarray(src.read(1,masked=True).filled(np.nan),dtype=float),tr)
    return out

def sampled_cells(arr,tr,lat,lon):
    # Original EPSG:4326 affine; never interpolate pixel values.
    col=np.floor((lon-tr.c)/tr.a).astype(int)
    row=np.floor((lat-tr.f)/tr.e).astype(int)
    within=(row>=0)&(row<arr.shape[0])&(col>=0)&(col<arr.shape[1])
    vals=np.full(len(lat),np.nan)
    vals[within]=arr[row[within],col[within]]
    return vals,row,col

def annual_stage(source):
    vals={}
    for r in readcsv(source):
        key=r["species"],int(r["season_start"])
        if key[0] not in TRACK_FILES or key[1] not in range(2011,2020):continue
        if key in vals:raise ValueError("duplicate BAS species-year fledgling stage")
        if int(r["has_reported_fledglings_n"])<1:raise ValueError("invalid original fledgling stage")
        vals[key]=float(r["median_recorded_fledglings_per_pair"])
    if len(vals)!=27:raise ValueError("three species × nine years stage source incomplete")
    return vals

def tracking_vs_models(tracks,models):
    rows=[]
    for r in tracks:
        data=r["points"]
        spikes=singleton_spike_mask(data)
        lat=np.array([z[1] for z in data])
        lon=np.array([z[2] for z in data])
        km=geodesic(lat,lon)
        for dmin,remove_spikes in SENSITIVITY:
            keep=(km>=dmin)&(km<=MAX_KM)
            if remove_spikes:keep &= ~spikes
            hourly=selected_hourly([data[i] for i in np.flatnonzero(keep)])
            row=dict(species=r["species"],season_start=r["season"],deployment=r["deployment"],
                     source_member_sha256=r["source_sha256"],
                     minimum_distance_km=dmin,isolated_spike_filter=remove_spikes,
                     source_positions=r["raw_count"],
                     duplicate_timestamp_dropped=r["raw_count"]-len(data),
                     isolated_spikes_detected=int(spikes.sum()),
                     in_distance_positions=int(keep.sum()),
                     hourly_positions=len(hourly),qualifies=len(hourly)>=MIN_HOURS,
                     median_selected_distance_km=(float(np.median(
                         geodesic([z[1] for z in hourly],[z[2] for z in hourly])))
                         if hourly else None))
            for label,year in (("preseason",r["season"]),("same_summer",r["season"]+1)):
                row[label+"_survey_model_year"]=year
                row[label+"_valid_hourly_fixes"]=0
                row[label+"_unique_raster_cells"]=0
                row[label+"_krill_model_g_m2_equal_hours"]=None
                row[label+"_krill_model_g_m2_equal_visited_cells"]=None
                if hourly:
                    arr,tr=models[year]
                    v,rr,cc=sampled_cells(arr,tr,np.array([p[1] for p in hourly]),
                                          np.array([p[2] for p in hourly]))
                    good=np.isfinite(v)
                    cells=sorted(set(zip(rr[good].tolist(),cc[good].tolist())))
                    row[label+"_valid_hourly_fixes"]=int(good.sum())
                    row[label+"_unique_raster_cells"]=len(cells)
                    if cells:
                        row[label+"_krill_model_g_m2_equal_hours"]=float(np.mean(v[good]))
                        row[label+"_krill_model_g_m2_equal_visited_cells"]=float(np.mean([arr[i,j] for i,j in cells]))
            rows.append(row)
    return rows

def geographic_index(models):
    rows=[]
    for year,(arr,tr) in sorted(models.items()):
        yy,xx=np.indices(arr.shape)
        lat=tr.f+(yy+0.5)*tr.e
        lon=tr.c+(xx+0.5)*tr.a
        km=geodesic(lat,lon)
        weights=np.cos(np.deg2rad(lat))
        for dmin in (5,10,20):
            mask=np.isfinite(arr)&(km>=dmin)&(km<=MAX_KM)
            if not np.any(mask):raise ValueError("no reference model grid cells")
            rows.append(dict(model_year=year,minimum_distance_km=dmin,
                             total_model_valid_cells=int(mask.sum()),
                             modelled_krill_g_m2_area_weighted=float(np.average(arr[mask],weights=weights[mask])),
                             validated_independent_ocean_mask=False))
    return rows

def by_species_year(rows,stage,reference):
    idx={(z["model_year"],z["minimum_distance_km"]):z for z in reference}
    out=[]
    for dmin,filtered in SENSITIVITY:
        for species in TRACK_FILES:
            years=sorted({r["season_start"] for r in rows if r["species"]==species})
            for year in years:
                cohort=[r for r in rows if r["species"]==species and r["season_start"]==year
                        and r["minimum_distance_km"]==dmin and r["isolated_spike_filter"]==filtered]
                qualified=[r for r in cohort if r["qualifies"] and
                           r["preseason_krill_model_g_m2_equal_visited_cells"] is not None and
                           r["same_summer_krill_model_g_m2_equal_visited_cells"] is not None]
                annual=dict(species=species,season_start=year,minimum_distance_km=dmin,
                            isolated_spike_filter=filtered,n_deployments_source=len(cohort),
                            n_qualified_deployments=len(qualified),
                            n_original_source_positions=sum(r["source_positions"] for r in cohort),
                            n_positions_in_geographic_window=sum(r["in_distance_positions"] for r in cohort),
                            n_hourly_positions_qualified=sum(r["hourly_positions"] for r in qualified),
                            median_deployment_median_distance_km=(
                                float(statistics.median(r["median_selected_distance_km"] for r in qualified))
                                if qualified else None),
                            reported_fledglings_per_pair_original_BAS=stage.get((species,year)),
                            sufficient_tracking_deployments_for_description=len(qualified)>=3,
                            geographic_foraging_zone_confirmed=False)
                for label in ("preseason","same_summer"):
                    observed=[r[label+"_krill_model_g_m2_equal_visited_cells"] for r in qualified]
                    hourly=[r[label+"_krill_model_g_m2_equal_hours"] for r in qualified]
                    annual[label+"_track_equal_visited_cell_krill_model_g_m2"]=(
                        float(statistics.mean(observed)) if observed else None)
                    annual[label+"_track_equal_hourly_krill_model_g_m2"]=(
                        float(statistics.mean(hourly)) if hourly else None)
                    ref=idx[(year+(label=="same_summer"),dmin)]["modelled_krill_g_m2_area_weighted"]
                    annual[label+"_fixed_geographic_model_g_m2"]=ref
                    annual[label+"_track_vs_geographic_ratio"]=(
                        annual[label+"_track_equal_visited_cell_krill_model_g_m2"]/ref if observed else None)
                out.append(annual)
    return out

def verify(rows,output):
    if output["original_unique_deployments"]!=168 or output["source_positions"]!=174127:
        raise ValueError("source GPS valid track counts drifted")
    if output["qualifying_deployments_primary"]!=152:
        raise ValueError("n qualifying 10-150 km/10h GPS deployments changed")
    if output["common_3species_seasons"]!=[2013,2015]:
        raise ValueError("three-species GPS calendar overlap changed")
    a={(r["species"],r["season_start"]):r for r in output["primary_species_years"]}
    must={("Adelie",2013):(22,4.083445822723697,9.24151788796438),
          ("Chinstrap",2013):(20,3.159565282642903,8.648863003959303),
          ("Gentoo",2013):(7,6.6401306682162815,10.865938401222229),
          ("Gentoo",2015):(1,4.574066189468884,8.350604127665035)}
    for key,(n,pre,summer) in must.items():
        r=a[key]
        if r["n_qualified_deployments"]!=n:
            raise ValueError("source GPS per-species support drift "+str(key))
        for col,value in (("preseason_track_equal_visited_cell_krill_model_g_m2",pre),
                          ("same_summer_track_equal_visited_cell_krill_model_g_m2",summer)):
            if not math.isclose(r[col],value,abs_tol=1e-7):
                raise ValueError("independently calculated krill exposure receipt mismatch "+str((key,col)))
    return True

def save(path,rows):
    if not rows:raise ValueError("empty analytic output")
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)

def leave_one_deployment_out(source):
    """Leave-one-tag deletion ranges: descriptive, not confidence intervals."""
    selected=[r for r in source if r["minimum_distance_km"]==10 and r["isolated_spike_filter"]
              and r["qualifies"] and r["preseason_krill_model_g_m2_equal_visited_cells"] is not None
              and r["same_summer_krill_model_g_m2_equal_visited_cells"] is not None]
    cohorts=sorted({(r["species"],r["season_start"]) for r in selected})
    rows=[]
    for species,year in cohorts:
        group=[r for r in selected if r["species"]==species and r["season_start"]==year]
        n=len(group)
        record={"species":species,"season_start":year,"n_eligible_deployments":n}
        for label in ("preseason","same_summer"):
            x=[r[label+"_krill_model_g_m2_equal_visited_cells"] for r in group]
            mean=float(statistics.mean(x))
            loo=[float((sum(x)-v)/(n-1)) for v in x] if n>1 else []
            record[label+"_mean_model_g_m2"]=mean
            record[label+"_leave_one_deployment_min"]=min(loo) if loo else None
            record[label+"_leave_one_deployment_max"]=max(loo) if loo else None
            record[label+"_single_deployment_is_not_robust"]=n==1
        rows.append(record)
    return rows

def verify_2013_loo(source):
    """Do not infer a transferable species ranking, only 2013 source consistency."""
    x={(r["species"],r["season_start"]):r for r in source}
    if {s:x[s,2013]["n_eligible_deployments"] for s in
        ("Adelie","Chinstrap","Gentoo")}!={"Adelie":22,"Chinstrap":20,"Gentoo":7}:
        raise ValueError("2013 GPS individual roster drift")
    for k in ("preseason","same_summer"):
        a=x["Adelie",2013]
        c=x["Chinstrap",2013]
        g=x["Gentoo",2013]
        if not(g[k+"_leave_one_deployment_min"] > a[k+"_leave_one_deployment_max"]
               > c[k+"_leave_one_deployment_max"]):
            raise ValueError("2013 track deletion sensitivity no longer separates source pattern")
    if x["Gentoo",2015]["n_eligible_deployments"]!=1:
        raise ValueError("2015 gentoo n=1 warning no longer applies")
    return True

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--gps-root",required=True,type=Path)
    ap.add_argument("--model-zip",required=True,type=Path)
    ap.add_argument("--stage-annual",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    ap.add_argument("--check",action="store_true")
    a=ap.parse_args()
    tracks,source_audit=read_tracks(a.gps_root)
    models=source_models(a.model_zip)
    stage=annual_stage(a.stage_annual)
    deployment=tracking_vs_models(tracks,models)
    geography=geographic_index(models)
    years=by_species_year(deployment,stage,geography)
    primary=[r for r in years if r["minimum_distance_km"]==10 and r["isolated_spike_filter"]]
    common=sorted(set.intersection(*[
        {r["season_start"] for r in primary if r["species"]==species} for species in TRACK_FILES
    ]))
    result={
        "status":"GPS_TRACK_ACCESSED_PUBLISHED_GAM_KRILL_NOT_CONFIRMED_FORAGING_OR_PREY_CAUSALITY",
        "source_gps_canonical_digest":source_audit["canonical_member_content_sha256"],
        "source_audit":source_audit,
        "source_models":"Freer 2025 BAS originally published 2011-2020 hurdle-GAM combined GeoTIFFs, all 10 SHA-pinned",
        "geographic_center":{"lat":ANCHOR[0],"lon":ANCHOR[1],
            "meaning":"bbox midpoint of 14 original Adelie/Chinstrap colony GPS reference points; not Gentoo colony"},
        "original_unique_deployments":len(tracks),
        "source_positions":sum(r["raw_count"] for r in tracks),
        "qualifying_deployments_primary":sum(r["n_qualified_deployments"] for r in primary),
        "common_3species_seasons":common,
        "primary_species_years":primary,
        "protocol":{
            "source_year_label":"Dec T–Jan/Feb T+1 breeding season year T",
            "preseason_model_year":"T: Jan-Feb before nesting",
            "same_summer_model_year":"T+1: contemporaneous / potentially later than GPS fixes",
            "krill_model_fit":"same 2011-2020 observational acoustic+ice+salinity; not temporal held-out model",
            "window_maximum_km":MAX_KM,
            "minimum_distance_km_sensitivities":[5,10,20],
            "isolated_spike_threshold_m_s":SPIKE_SPEED_M_S,
            "hourly_sampling":"one original median-time timestamp per hour/deployment",
            "minimum_hourly_observations":MIN_HOURS,
            "primary_weighting":"mean unique source raster cells within each deployment, then mean equal-weighted deployments within species-year",
            "sensitivity_weighting":"mean equal-hourly-position model values per deployment then equal deployments",
            "important_non_independence":"~174,000 GPS fixes are repeated tracks, not ~174,000 independent krill-climate trials",
        },
        "limits":[
            "GPS points are recorded movement, not confirmed feeding or prey capture; coastlines/land masking not independently verified.",
            "5/10/20 km lower cutoff and 150 km upper cap are proxy geometric sensitivity, not measured species foraging availability.",
            "Published model cells are ~0.083333 degree, and many positions share one pixel.",
            "The original 2011-2020 Freer GAM was fitted using original IMR data with salinity and sea ice; no independent krill or climate-effect validation.",
            "Only 2013 and 2015 are tracked for all 3 species, and Gentoo 2015 has only one qualified deployment.",
            "Unequal deployments per species-year, heterogeneous tracked birds and nest locations prohibit population-wide statements.",
            "Same-summer T+1 raster year may occur later than GPS collection; not an operational prediction.",
            "Original BAS fledgling stage is native-colony medians (Adelie/Chinstrap) versus island aggregate (Gentoo), not common nest-level success.",
            "No forecast of penguin pairs, N_eff, colony occupancy, vegetation or breeding success at 2050/2100 is validated."
        ]
    }
    robustness=leave_one_deployment_out(deployment)
    result["leave_one_deployment_out"]=robustness
    if a.check:
        verify(deployment,result)
        verify_2013_loo(robustness)
    a.out.mkdir(parents=True,exist_ok=True)
    save(a.out/"original_deployment_model_exposures.csv",deployment)
    save(a.out/"species_year_exposures.csv",years)
    save(a.out/"source_model_geographic_reference.csv",geography)
    save(a.out/"leave_one_deployment_out.csv",robustness)
    (a.out/"result.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],
        "source_deployments":result["original_unique_deployments"],
        "positions":result["source_positions"],
        "primary_qualified_deployments":result["qualifying_deployments_primary"],
        "overlap_years":common,
        "primary_species_years":[{
          k:r[k] for k in (
            "species","season_start","n_qualified_deployments","median_deployment_median_distance_km",
            "preseason_track_equal_visited_cell_krill_model_g_m2",
            "same_summer_track_equal_visited_cell_krill_model_g_m2")
        } for r in primary],"receipt":bool(a.check)},ensure_ascii=False))

if __name__=="__main__":
    main()
