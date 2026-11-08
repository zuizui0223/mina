#!/usr/bin/env python3
"""Independent SciPy Laplacian cross-check of actual Circuitscape.jl effective resistances.

Reads outputs of Circuitscape.jl, not any penguin ecological outcomes.
"""
from __future__ import annotations
from collections import defaultdict
import csv, itertools, json, math
from pathlib import Path
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import factorized

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"circuit_outputs"
SCENARIOS=OUT/"circuit_scenarios.tsv"
EXPECTED=("ARDL","BISC","LION","LLAN","PCHA","PETE")
NODATA=-9999
TOL=0.005

def read_asc(path):
    with path.open(encoding="ascii") as f:
        header=[next(f).strip().split() for _ in range(6)]
    info={k.lower():float(v) for k,v in header}
    data=np.loadtxt(path,skiprows=6)
    if data.shape!=(int(info["nrows"]),int(info["ncols"])):
        raise ValueError("Wrong ArcInfo source raster geometry")
    return data,info

def independent_effective_resistance_grid(habitat,point,neighbors):
    """Construct graph explicitly with native per-cell average conductance edges."""
    good=np.isfinite(habitat)&(habitat>0)&(habitat!=NODATA)
    idx=np.full(good.shape,-1,dtype=np.int32)
    idx[good]=np.arange(good.sum())
    N=int(good.sum())
    if N<6:raise ValueError("Only a few ocean cells in raster")
    starts={}
    for row,col in np.argwhere(point>0):
        k=int(point[row,col])
        if k in starts:raise ValueError("Duplicate focal node")
        if not good[row,col]:raise ValueError("Focal point is on missing habitat")
        starts[k]=int(idx[row,col])
    if set(starts)!=set(range(1,7)):raise ValueError("Focal point IDs changed")
    steps=[(0,1),(1,0)]+([(1,1),(1,-1)] if neighbors==8 else [])
    rr=[];cc=[];dd=[]
    H,W=habitat.shape
    for dr,dc in steps:
        ya=max(0,-dr);yb=min(H,H-dr);xa=max(0,-dc);xb=min(W,W-dc)
        original=(slice(ya,yb),slice(xa,xb))
        target=(slice(ya+dr,yb+dr),slice(xa+dc,xb+dc))
        aa=good[original]&good[target]
        if not np.any(aa):continue
        u=idx[original][aa];v=idx[target][aa]
        c=(1./habitat[original][aa]+1./habitat[target][aa])/2
        if abs(dr)+abs(dc)==2:c=c/math.sqrt(2)
        rr.extend([u,v,u,v]);cc.extend([u,v,v,u]);dd.extend([c,c,-c,-c])
    r=np.concatenate(rr);c=np.concatenate(cc);data=np.concatenate(dd)
    L=coo_matrix((data,(r,c)),shape=(N,N)).tocsr()
    factor=factorized(L[:-1,:-1].tocsc())
    reference={}
    for a,b in itertools.combinations(range(1,7),2):
        rhs=np.zeros(N-1)
        s,t=starts[a],starts[b]
        if s!=N-1:rhs[s]+=1.
        if t!=N-1:rhs[t]-=1.
        volt=factor(rhs)
        vs=0. if s==N-1 else volt[s]
        vt=0. if t==N-1 else volt[t]
        reference[(a,b)]=float(vs-vt)
    return reference,N,int(len(data)//4)

def main():
    with SCENARIOS.open(encoding="utf-8") as f:jobs=list(csv.DictReader(f,delimiter="\t"))
    if not jobs:raise ValueError("No circuit jobs")
    point,point_hdr=read_asc(OUT/"inputs/six_focal_nodes.asc")
    found={}
    for j in jobs:
        key=j["key"]
        if key in found:raise ValueError("Duplicate scenario key")
        matrix_path=OUT/"solves"/(key+"_matrix_from_actual_julia.csv")
        if not matrix_path.exists():raise ValueError("Circuitscape did not actually write matrix: "+key)
        m=np.loadtxt(matrix_path,delimiter=",")
        if m.shape!=(7,7) or not np.array_equal(m[0,1:],np.arange(1,7)) or not np.array_equal(m[1:,0],np.arange(1,7)):
            raise ValueError("Unexpected Circuitscape pairwise matrix format: "+key+" "+str(m))
        a=m[1:,1:]
        if not (np.isfinite(a).all() and np.allclose(a,a.T,atol=1e-8,rtol=1e-8) and np.allclose(np.diag(a),0,atol=1e-8)
                and np.all(a[np.triu_indices(6,1)]>0)):
            raise ValueError("Circuitscape matrix is disconnected, not symmetric, or non-positive: "+key)
        found[key]={"job":j,"matrix":a}
    res=[]
    for year,kind,neighbors in itertools.product([1993,2018],["uniform","ice_penalty","ice_favor"],[8,4]):
        key=f"{year}_{kind}_{neighbors}n"
        if key not in found:continue
        a=found[key]["matrix"]
        for i in range(6):
            for j in range(i+1,6):
                res.append({"year":year,"scenario":kind,"neighbors":neighbors,
                  "site_a":EXPECTED[i],"site_b":EXPECTED[j],
                  "effective_resistance_model_units":float(a[i,j]),
                  "scenario_key":key})
    if len(res)!=15*len(jobs):raise ValueError("Result panel is not complete")
    diff=[]
    for item in res:
        base=found[f'{item["year"]}_uniform_{item["neighbors"]}n']["matrix"]
        i=EXPECTED.index(item["site_a"]);j=EXPECTED.index(item["site_b"])
        item["ratio_to_same_year_uniform"]=item["effective_resistance_model_units"]/base[i,j]
        if item["scenario"]=="uniform":item["ratio_to_same_year_uniform"]=1.
    common1=found["1993_uniform_8n"]["matrix"];common2=found["2018_uniform_8n"]["matrix"]
    baseline_error=float(np.max(np.abs(common1-common2)))
    if baseline_error>1e-8:raise ValueError("Constant ocean geometry base changed across years")
    independent=[]
    for key in ["1993_uniform_8n","2018_ice_penalty_8n"]:
        habitat,header=read_asc(OUT/"inputs"/(found[key]["job"]["habitat_raster"].split("/")[-1]))
        if any(abs(point_hdr[k]-header[k])>1e-9 for k in ("nrows","ncols","xllcorner","yllcorner","cellsize")):
            raise ValueError("Focal and resistance grids not aligned")
        pred,N,E=independent_effective_resistance_grid(habitat,point,8)
        mat=found[key]["matrix"]
        for (id_a,id_b),v in pred.items():
            observed=float(mat[id_a-1,id_b-1])
            err=abs(observed-v)/max(abs(v),1e-12)
            independent.append({"scenario":key,"source":EXPECTED[id_a-1],"target":EXPECTED[id_b-1],
               "julia_circuitscape_effective_resistance":observed,
               "scipy_laplacian_effective_resistance":v,
               "relative_error":err,"n_connected_nodes":N,"n_adjacent_links":E})
    max_err=max(z["relative_error"] for z in independent)
    if max_err>TOL:raise ValueError("Native Circuitscape disagreed with independent SciPy Laplacian: "+str(max_err))
    with (OUT/"pairwise_effective_resistances.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(res[0]));w.writeheader();w.writerows(res)
    with (OUT/"scipy_independent_solver_crosscheck.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(independent[0]));w.writeheader();w.writerows(independent)
    summary={}
    for j in jobs:
        key=j["key"]
        cells=[x for x in res if x["scenario_key"]==key]
        summary[key]={"count":len(cells),"median_effective_resistance":float(np.median([x["effective_resistance_model_units"] for x in cells])),
           "median_ratio_to_same_year_uniform":float(np.median([x["ratio_to_same_year_uniform"] for x in cells])),
           "min_ratio_to_same_year_uniform":float(min(x["ratio_to_same_year_uniform"] for x in cells)),
           "max_ratio_to_same_year_uniform":float(max(x["ratio_to_same_year_uniform"] for x in cells))}
    out={"status":"NATIVE_CIRCUITSCAPE_COMPUTED_INDEPENDENT_CIRCUIT_CHECK_PASS",
       "n_scenarios":len(jobs),"n_site_pairs":15,"n_scenario_pair_results":len(res),
       "uniform_1993_2018_max_abs_difference":baseline_error,
       "independent_scipy_checked_scenario_pairs":len(independent),
       "independent_scipy_max_relative_error":max_err,
       "by_scenario":summary,
       "interpretation":"The solver confirms relative resistances of assumed 25km sea-ice cost surfaces. Values are not measured penguin migration, climate-demographic causation or SSP forecasts.",
       "no_biological_response_fitted":True}
    (OUT/"comparison_summary.json").write_text(json.dumps(out,indent=2)+"\n")
    print("ACTUAL_CIRCUITSCAPE_VERDICT="+json.dumps(out),flush=True)

if __name__=="__main__":main()
