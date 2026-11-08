#!/usr/bin/env python3
"""Source-verifiable 45-day GPS/current comparison against fixed zero-ice-weight baseline.

No beta optimization, immigration claims or uncalibrated climate population prediction.
Independent SciPy graph current solver verifies one fixed 2013 Signy day before scoring.
"""
from __future__ import annotations
from collections import defaultdict
import csv, json, math
from pathlib import Path

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve

HERE=Path(__file__).resolve().parent
OUT=HERE/"daily_outputs"
CASES=OUT/"cases"
CUR=OUT/"currents"
SCENARIOS=("uniform","ice_penalty","ice_favor")
NO=-9999.
BINS=[10,35,60,85,110,135,160]
TEST_CASE="2013_PI_20131229_SI"

def readcsv(name,delimiter=","):
    with (OUT/name).open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f,delimiter=delimiter))
def writecsv(name,records):
    if not records:return
    with (OUT/name).open(encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
def readasc(file):
    with file.open(encoding="ascii") as f:
        hdr=[next(f).strip().split() for _ in range(6)]
    meta={a.lower():float(b) for a,b in hdr}
    arr=np.loadtxt(file,skiprows=6)
    if arr.shape!=(int(meta["nrows"]),int(meta["ncols"])):
        raise ValueError("Source raster geometry mismatch: "+str(file))
    if not(np.isfinite(arr).all()):raise ValueError("NaN or infinite current/map")
    return arr,meta
def aligned(a,b):
    for key in ("ncols","nrows","xllcorner","yllcorner","cellsize"):
        if not math.isclose(a[key],b[key],abs_tol=1e-9,rel_tol=1e-12):
            raise ValueError("Current map misaligned with original OSI footprint")
def mean(xs):
    return float(np.mean(xs)) if xs else None
def score_current(current,habitat,distance,source,ground,visit,record):
    good=(habitat>0)&np.isfinite(habitat)&(distance>=10)&(distance<160)&(source<0)&(ground<0)
    if not np.any(good):return None,0,0
    bg=[current[good&(distance>=BINS[i])&(distance<BINS[i+1])]
        for i in range(6)]
    perc=[];raw=[];visited_count=0
    y0=int(record["native_min_row"]);x0=int(record["native_min_col"])
    ny=int(record["grid_shape_rows"]);nx=int(record["grid_shape_cols"])
    xr=record["x_reversed_in_ascii"]=="True"; yr=record["y_reversed_in_ascii"]=="True"
    for row in visit:
        if row["within_fixed_score_distance_bins"]!="True":continue
        src=int(row["native_source_pixel"])
        r,c=divmod(src,432);i=r-y0;j=c-x0
        if not(0<=i<ny and 0<=j<nx):raise ValueError("Original GPS cell marked eligible beyond crop")
        if yr:i=ny-i-1
        if xr:j=nx-j-1
        if not good[i,j]:raise ValueError("GPS site marked eligible but not source-connected interior")
        original=float(row["source_cell_distance_km"])
        if abs(distance[i,j]-original)>1e-4:
            raise ValueError("GPS native pixel center and case EASE2 crop not aligned")
        b=int(np.searchsorted(BINS,original,side="right")-1)
        if b<0 or b>=6:raise ValueError("GPS visit outside frozen rank bins")
        arr=bg[b]
        if len(arr)<3:raise ValueError("Less than 3 available background cells in fixed radial bin")
        value=current[i,j]
        # Standard empirical midrank, same availability cells for every scenario.
        pct=(int(np.count_nonzero(arr<value))+0.5*int(np.count_nonzero(arr==value)))/len(arr)
        if not(0<=pct<=1):raise ValueError("Rank percentile invalid")
        perc.append(float(pct));raw.append(float(value))
        visited_count+=1
    return {"mean_rank_percentile":mean(perc),"median_rank_percentile":float(np.median(perc)) if perc else None,
            "mean_actual_circuit_current_at_GPS":mean(raw),
            "fraction_GPS_pixels_in_upper_quartile":mean([v>=.75 for v in perc]),
            "n_available_ocean_cells_in_fixed_radius":int(good.sum()),
            "n_distance_bins_with_background_at_least_3":sum(len(x)>=3 for x in bg)},visited_count,len(perc)

def independent_advanced_map(habitat,source,ground):
    good=(habitat>0)&np.isfinite(habitat)
    src=np.argwhere(source>0)
    gr=np.argwhere(ground==0)
    if len(src)!=1 or len(gr)<8 or not good[tuple(src[0])] or not np.all(good[gr[:,0],gr[:,1]]):
        raise ValueError("Bad source/ground for independent circuit")
    h,w=good.shape
    ix=np.full(good.shape,-1,dtype=np.int32);ix[good]=np.arange(good.sum())
    n=int(good.sum())
    units=[];targets=[];gs=[]
    for dr,dc in ((1,0),(0,1),(1,1),(1,-1)):
        r0=max(0,-dr);r1=min(h,h-dr);c0=max(0,-dc);c1=min(w,w-dc)
        s0=(slice(r0,r1),slice(c0,c1));s1=(slice(r0+dr,r1+dr),slice(c0+dc,c1+dc))
        mask=good[s0]&good[s1]
        u=ix[s0][mask];v=ix[s1][mask]
        g=(1/habitat[s0][mask]+1/habitat[s1][mask])/2
        if abs(dr)+abs(dc)==2:g=g/math.sqrt(2.)
        units.append(u);targets.append(v);gs.append(g)
    u=np.concatenate(units);v=np.concatenate(targets);g=np.concatenate(gs)
    rows=np.concatenate([u,u,v,v]);cols=np.concatenate([u,v,u,v]);data=np.concatenate([g,-g,-g,g])
    L=coo_matrix((data,(rows,cols)),shape=(n,n)).tocsr()
    ground_nodes=ix[gr[:,0],gr[:,1]]
    free=np.ones(n,dtype=bool);free[ground_nodes]=False
    source_id=int(ix[tuple(src[0])])
    if not free[source_id]:raise ValueError("Source at ground")
    rhs=np.zeros(n,dtype=float);rhs[source_id]=1.
    volt=np.zeros(n,dtype=float)
    volt[free]=spsolve(L[free][:,free],rhs[free])
    edge=g*(volt[u]-volt[v])
    inflow=np.zeros(n,dtype=float);outflow=np.zeros(n,dtype=float)
    pos=edge>=0
    np.add.at(outflow,u[pos],edge[pos]);np.add.at(inflow,v[pos],edge[pos])
    np.add.at(inflow,u[~pos],-edge[~pos]);np.add.at(outflow,v[~pos],-edge[~pos])
    curr=np.maximum(inflow,outflow)
    grid=np.zeros(good.shape,dtype=float);grid[good]=curr
    net_source=float(outflow[source_id]-inflow[source_id])
    if not math.isclose(net_source,1.,abs_tol=1e-8):
        raise ValueError("Independent source conservation failure")
    return grid,{"nodes":n,"links":len(edge),"source_net_amps":net_source,"n_direct_ground_cells":len(gr)}

def verify_native_numerics():
    checks=[]
    for name in SCENARIOS:
        original_dir=CASES/TEST_CASE
        src,info=readasc(original_dir/"source.asc")
        grd,ig=readasc(original_dir/"grounds.asc");aligned(info,ig)
        hab,ih=readasc(original_dir/f"resistance_{name}.asc");aligned(info,ih)
        actual,ic=readasc(CUR/f"{TEST_CASE}_{name}_curmap.asc");aligned(info,ic)
        expected,detail=independent_advanced_map(hab,src,grd)
        tested=(hab>0)&(src<0)&(grd<0)
        err=np.abs(actual[tested]-expected[tested])
        rel=err/np.maximum(1e-5,np.abs(expected[tested]))
        test={"case":TEST_CASE,"scenario":name,**detail,"n_compared_interior_nodes":int(tested.sum()),
              "max_absolute_diff":float(err.max()),"max_regularized_relative_diff":float(rel.max()),
              "n_source_cells":int((src>0).sum()),"n_ground_cells":int((grd==0).sum())}
        checks.append(test)
    # Numeric criteria frozen from contract: interior current value agrees within float-grid tolerance.
    for c in checks:
        if c["max_absolute_diff"]>1e-4 or c["max_regularized_relative_diff"]>.01:
            raise ValueError("Independent current map and Circuitscape disagree: "+str(c))
    (OUT/"independent_advanced_current_validation.json").write_text(json.dumps(checks,indent=2)+"\n")
    return checks

def main():
    with (OUT/"source_and_model_preflight.json").open(encoding="utf-8") as f:source=json.load(f)
    rows=readcsv("fixed_270_circuit_scenario_manifest.csv")
    gps=readcsv("gps_original_source_pixel_visits.csv")
    cases=readcsv("island_day_source_domain_support.csv")
    receipts=readcsv("julia_curmap_receipts.tsv","\t")
    if len(cases)!=90 or len(rows)!=3*source["supported_island_days"] or len(receipts)!=len(rows):
        raise ValueError("Incomplete original day/circuit/output cohort")
    if len({r["solve_id"] for r in receipts})!=len(receipts):
        raise ValueError("Duplicate native Circuitscape output key")
    validreceipts={r["solve_id"]:r for r in receipts}
    gpsby=defaultdict(list)
    for row in gps:gpsby[row["case_id"]].append(row)
    caseby={r["case_id"]:r for r in cases}
    q=verify_native_numerics()
    panel=[];island_rows=[]
    allmodels=defaultdict(dict)
    for row in rows:
        key=row["case_id"];name=row["scenario"]
        c=caseby[key]
        prefix=f"{key}_{name}"
        if prefix not in validreceipts:raise ValueError("No native Julia current map for "+prefix)
        original_dir=CASES/key
        habitat,ih=readasc(original_dir/f"resistance_{name}.asc")
        distance,idis=readasc(original_dir/"distance.asc")
        src,isr=readasc(original_dir/"source.asc")
        ground,igr=readasc(original_dir/"grounds.asc")
        current,ic=readasc(CUR/f"{prefix}_curmap.asc")
        for meta in (idis,isr,igr,ic):aligned(ih,meta)
        if not (np.isfinite(current).all() and current.min()>=-1e-7 and current.max()<=1.0001):
            raise ValueError("Circuit current map physically out of [0,1] expected source-bound range")
        scored,n,nn=score_current(current,habitat,distance,src,ground,gpsby[key],c)
        a={"case_id":key,"season_start":int(row["year"]),"date":row["date"],
           "island":row["site"],"other_island":row["other_island"],
           "scenario":name,"beta":float(row["beta"]),
           "n_original_GPS_source_pixels":int(row["n_original_matched_GPS_pixels"]),
           "n_circuit_eligible_GPS_source_pixels":n,
           "source_ice_sic_scenario_model_only":True,
           "actual_Circuitscape_advanced_raster_file":validreceipts[prefix]["current_raster"]}
        if scored:a.update(scored)
        else:a.update({"mean_rank_percentile":None,"median_rank_percentile":None,
                       "mean_actual_circuit_current_at_GPS":None,
                       "fraction_GPS_pixels_in_upper_quartile":None,
                       "n_available_ocean_cells_in_fixed_radius":0,
                       "n_distance_bins_with_background_at_least_3":0})
        panel.append(a)
        if name in allmodels[key]:raise ValueError("Duplicate model within source GPS date")
        allmodels[key][name]=a
    for c in cases:
        key=c["case_id"]
        if c["status"]!="READY":
            island_rows.append({"case_id":key,"status":c["status"],"season_start":int(c["season_start"]),
              "date":c["date"],"island":c["island"],"n_GPS_cells_scored":0})
            continue
        model=allmodels[key]
        if set(model)!=set(SCENARIOS):raise ValueError("Incomplete exactly-3 beta comparison")
        ns={z["n_circuit_eligible_GPS_source_pixels"] for z in model.values()}
        if len(ns)!=1:raise ValueError("Different GPS cohorts among resistance hypotheses")
        cnt=next(iter(ns))
        ok=cnt>0
        z={"case_id":key,"status":"SCORED" if ok else "NO_ELIGIBLE_GPS_PIXELS",
            "season_start":int(c["season_start"]),"date":c["date"],
            "island":c["island"],"other_island":c["other_island"],
            "n_GPS_cells_scored":cnt}
        for name in SCENARIOS:
            z["score_"+name]=model[name]["mean_rank_percentile"]
        for name in ("ice_penalty","ice_favor"):
            z["gain_"+name]=float(z["score_"+name]-z["score_uniform"]) if ok else None
        island_rows.append(z)
    scored=[r for r in island_rows if r["status"]=="SCORED"]
    block=defaultdict(list)
    for row in scored:block[(row["season_start"],row["island"])].append(row)
    six=[]
    for (season,island),arr in sorted(block.items()):
        values={"season_start":season,"island":island,
                "n_source_GPS_days_scored":len(arr),
                "n_individual_GPS_ocean_cells_scored":sum(x["n_GPS_cells_scored"] for x in arr)}
        for name in SCENARIOS:
            values["mean_rank_"+name]=mean([x["score_"+name] for x in arr])
        for name in ("ice_penalty","ice_favor"):
            values["mean_daily_gain_"+name]=mean([x["gain_"+name] for x in arr])
            values["positive_gain_days_"+name]=sum(x["gain_"+name]>0 for x in arr)
        six.append(values)
    enough=len(scored)>=60 and sum(x["n_source_GPS_days_scored"]>=3 for x in six)>=4
    summary={"status":"DESCRIPTIVE_SCENARIO_COMPARISON_ONLY" if enough else "INSUFFICIENT_VALIDATION_SUPPORT",
       "n_original_matched_calendar_days":45,"n_original_island_days":90,
       "n_island_days_source_ready":source["supported_island_days"],
       "n_island_days_GPS_scored":len(scored),
       "n_unique_island_year_blocks_scored":len(six),
       "n_blocks_with_at_least_3_days":sum(x["n_source_GPS_days_scored"]>=3 for x in six),
       "n_native_julia_Circuitscape_scenarios_solved":len(rows),
       "n_deduplicated_GPS_native_source_cells_scored":sum(x["n_GPS_cells_scored"] for x in scored),
       "mean_block_equal_gain_ice_penalty":mean([x["mean_daily_gain_ice_penalty"] for x in six]),
       "mean_block_equal_gain_ice_favor":mean([x["mean_daily_gain_ice_favor"] for x in six]),
       "n_blocks_positive_gain_ice_penalty":sum(x["mean_daily_gain_ice_penalty"]>0 for x in six),
       "n_blocks_positive_gain_ice_favor":sum(x["mean_daily_gain_ice_favor"]>0 for x in six),
       "independent_scipy_advanced_current_validation":q,
       "estimated_migration_rate":None,"known_true_penguin_mobility_beta":None,
       "caution":["All 45 shared days have within-season GPS, not individual breeding site changes.",
          "One source center per island-year is a first-GPS-fix median, not a verified nesting-origin field point.",
          "Radial ground ring at 175–210 km is a fixed physical model choice, not an actual foraging destination.",
          "GPS locations and satellite cells are not independent replicates. Six island-years only.",
          "Same-day 24-hour SIC and GPS timestamps differ in temporal resolution.",
          "Available background water cells are not known to be avoided or ecologically available to each individual.",
          "Hypothetical beta +2/-2 scenarios not calibrated from independent species movement."]
    }
    writecsv("all_same_day_advanced_current_GPS_scores.csv",panel)
    writecsv("island_day_paired_beta_gains.csv",island_rows)
    writecsv("island_year_block_equal_summary.csv",six)
    (OUT/"same_day_current_validation_result.json").write_text(json.dumps(summary,indent=2)+"\n")
    print("GPS_MATCHED_NATIVE_CIRCUIT_RESULT="+json.dumps(summary),flush=True)
    print("SIX_ISLAND_YEAR_BLOCKS="+json.dumps(six),flush=True)
    if not enough:raise SystemExit(3)

if __name__=="__main__":
    main()
