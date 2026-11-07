#!/usr/bin/env python3
"""Join NOAA OISST monthly SST to frozen Step1 JNCC geographic site rosters; no models."""
from pathlib import Path
from collections import defaultdict,Counter
import csv,hashlib,math,json,time
import numpy as np
import requests,xarray as xr

BASE=Path(__file__).resolve().parent
DATA=BASE/"data"
OUT=BASE/"outputs"
URL="https://psl.noaa.gov/thredds/ncss/grid/Datasets/noaa.oisst.v2.highres/sst.mon.mean.nc"
MONTHS=(3,4,5)
MAX_KM=50

def rows(p):
    with p.open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))

def save(p,r):
    with p.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(r[0]),lineterminator="\n")
        w.writeheader();w.writerows(r)

def km(a,b,c,d):
    a,c=map(math.radians,(a,c))
    dl=math.radians((d-b+180)%360-180)
    h=math.sin((c-a)/2)**2+math.cos(a)*math.cos(c)*math.sin(dl/2)**2
    return 12742.0176*math.asin(min(1,math.sqrt(h)))

def source_units(main,pair):
    needed={("network_species",r["row_id"]):int(r["K"]) for r in main}
    needed.update({("network_species_pairs",r["pair_row_id"]):int(r["K_pair"]) for r in pair})
    got=defaultdict(dict)
    for r in rows(DATA/"unit_endpoints.csv"):
        k=(r["analysis_unit"],r["row_id"])
        if k not in needed:continue
        if r["dataset_id"]!="JNCC" or r["count_status"] not in ("observed_positive","observed_zero"):
            raise ValueError("Bad original endpoint: "+str(k))
        ll=(float(r["latitude"]),float(r["longitude"]))
        if not all(math.isfinite(v) for v in ll):raise ValueError("Nonfinite original location")
        site=r["component_id"]
        if site in got[k] and got[k][site]!=ll:raise ValueError("Changed original site coordinates")
        got[k][site]=ll
    for k,n in needed.items():
        if len(got[k])!=n:raise ValueError(f"Fixed cohort K drift: {k}: {len(got[k])} vs {n}")
    return got

def get_ocean():
    pieces=[];manifest=[]
    for i,(west,east) in enumerate(((341,359.99),(0,8))):
        params=dict(var="sst",north=64,south=46,west=west,east=east,
                    time_start="1998-01-01T00:00:00Z",time_end="2021-12-31T23:59:59Z",
                    accept="netcdf4")
        # PSL NCSS can rate-limit requests made seconds apart. Honor 429 with
        # bounded backoff; never switch to another temperature product.
        if i: time.sleep(20)
        for attempt in range(4):
            res=requests.get(URL,params=params,timeout=240,
                         headers={"User-Agent":"mina-sst-reproducibility-study/1.0"})
            if res.status_code != 429:
                break
            if attempt==3:
                raise RuntimeError("NOAA PSL NCSS rate limit persists after 4 attempts")
            delay=(30,65,120)[attempt]
            retry=res.headers.get("Retry-After","")
            if retry.isdigit(): delay=max(delay,min(180,int(retry)))
            print(f"NOAA NCSS HTTP 429: retry after {delay}s (tile={i}, attempt={attempt+1})",flush=True)
            time.sleep(delay)
        res.raise_for_status()
        blob=res.content
        if len(blob)<400 or blob[:3] not in (b"CDF",b"\x89HD"):
            raise ValueError(f"Unexpected NOAA response, {len(blob)} bytes: {blob[:100]!r}")
        p=BASE/"build"/"oisst"/f"tile_{i}.nc"
        p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(blob)
        with xr.open_dataset(p,decode_times=True) as ds:
            if "sst" not in ds or not {"time","lat","lon"}.issubset(ds["sst"].dims):
                raise ValueError("NOAA dimension contract failed")
            ll=np.asarray(ds["lat"].values);lo=np.asarray(ds["lon"].values)
            tt=np.asarray(ds["time"].values);ss=np.asarray(ds["sst"].values,dtype=float)
            if len(ll)>100 or len(lo)>100 or len(tt)>320:
                raise ValueError(f"NOAA service did not honor subsetting {ss.shape}")
            pieces.append((ll,lo,tt,ss))
        manifest.append(dict(source_url=res.url,sha256=hashlib.sha256(blob).hexdigest(),
                             size_bytes=len(blob)))
    lat,lon,t,v=pieces[0];lat2,lon2,t2,v2=pieces[1]
    if not np.array_equal(lat,lat2) or not np.array_equal(t,t2):
        raise ValueError("NOAA tiles have incompatible axes")
    lon=np.concatenate([lon,lon2]);v=np.concatenate([v,v2],axis=2)
    if len(np.unique(np.round(lon,6)))!=len(lon):raise ValueError("Duplicated ocean columns")
    idx={}
    for i,date in enumerate(t):
        month=np.datetime_as_string(date,unit="D")[:7]
        if month in idx:raise ValueError("Duplicate monthly period")
        idx[month]=i
    needed={f"{y}-{m:02d}" for y in range(1998,2022) for m in MONTHS}
    if not needed.issubset(idx):raise ValueError("NOAA missing fixed source months")
    return lat,lon,idx,v,manifest

def sample(lat,lon,y0,y1,grlat,grlon,times,sst):
    if not 46<=lat<=64:return None,"out_of_uk_bbox"
    ix=[times[f"{y}-{m:02d}"] for y in (y0,y1) for m in MONTHS]
    dx=(grlon-lon+180)%360-180
    score=(grlat[:,None]-lat)**2+(dx[None,:]*math.cos(math.radians(lat)))**2
    for p in np.argsort(score,axis=None)[:140]:
        i,j=np.unravel_index(p,score.shape)
        d=km(lat,lon,float(grlat[i]),float(grlon[j]))
        if d>MAX_KM:break
        six=sst[ix,i,j]
        if np.all(np.isfinite(six)) and np.all((six>=-3)&(six<=45)):
            return (float(np.mean(six[:3])),float(np.mean(six[3:])),d),"verified"
    return None,"no_common_wet_cell_within_50km"

def run():
    a=[r for r in rows(DATA/"network_species.csv") if r["dataset_id"]=="JNCC" and
        r["null_status"]=="computed" and r["analysis_role"]=="macro_primary"]
    b=[r for r in rows(DATA/"network_species_pairs.csv") if r["dataset_id"]=="JNCC" and
        r["null_status"]=="computed" and r["analysis_role"]=="macro_primary"]
    if (len(a),len(b))!=(663,373):raise ValueError("Fixed Step1 cohort count drift")
    geo=source_units(a,b)
    gridlat,gridlon,time,values,source=get_ocean()
    climate=rows(DATA/"network_climate_intake.csv")
    dest={(r["analysis_unit"],r["row_id"]):r for r in climate}
    outcomes=[];counts=Counter();cache={}
    for kind,group,primary in (("network_species",a,"row_id"),
                               ("network_species_pairs",b,"pair_row_id")):
        for r in group:
            key=(kind,r[primary]);y0=int(r["year0"]);y1=int(r["year1"])
            before=[];after=[];dist=[];missing=[]
            for pt in geo[key].values():
                cp=(*pt,y0,y1)
                if cp not in cache:
                    cache[cp]=sample(*pt,y0,y1,gridlat,gridlon,time,values)
                value,status=cache[cp]
                if value is None:missing.append(status)
                else:
                    before.append(value[0]);after.append(value[1]);dist.append(value[2])
            d=dest[key]
            if missing:
                reason=Counter(missing).most_common(1)[0][0]
                if d["delta_sst_C_per_decade"]:raise ValueError("Previously verified row now absent")
                d.update(source_id="",spatial_status=reason,
                         temporal_status="source_endpoint_months_verified",
                         verification_status="not_matched")
                counts[reason]+=1
            else:
                delta=10*(float(np.mean(after))-float(np.mean(before)))/(y1-y0)
                old=d["delta_sst_C_per_decade"]
                if old and not math.isclose(float(old),delta,abs_tol=1e-10):
                    raise ValueError("Already curated SST would change")
                d.update(delta_sst_C_per_decade=f"{delta:.12g}",
                         source_id="NOAA_PSL_OISST_v2.1_monthly_MAM",
                         spatial_status="verified_source_ocean_cell",
                         temporal_status="source_endpoint_months_verified",
                         verification_status="verified_same_definition_sst")
                reason="verified";counts["verified_"+kind]+=1
            outcomes.append(dict(analysis_unit=kind,row_id=r[primary],K=int(len(geo[key])),
                                 n_wet_sites=len(dist),
                                 max_wet_distance_km=f"{max(dist):.3f}" if dist else "",
                                 status=reason))
    save(DATA/"network_climate_intake.csv",climate)
    save(DATA/"oisst_uk_join_qa.csv",outcomes)
    report={"status":"SOURCE_VERIFIED_UK_SST_JOIN_NO_HYPOTHESIS_TESTS",
            "source":URL,"source_doi":"10.25921/RE9P-PT57",
            "months":"March to May in both original UK census years",
            "site_rule":"same wet OISST 0.25deg cell <=50km for all six months; equal source site weighting",
            "source_subsets":source,"n_JNCC_main":len(a),"n_JNCC_pairs":len(b),
            "stats":dict(counts),"network_receipts":len(outcomes),
            "raw_source_site_table_redistributed":False}
    OUT.mkdir(exist_ok=True)
    (OUT/"STEP2_OISST_UK_JOIN.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report,ensure_ascii=False))

if __name__=="__main__":run()
