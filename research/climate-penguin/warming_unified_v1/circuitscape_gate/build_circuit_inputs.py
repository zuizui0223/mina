#!/usr/bin/env python3
"""Build actual, spatially aligned Circuitscape ASCII rasters from original OSI SAF NetCDF.
This stage reads NO penguin count outcomes, GPS outcomes, or future climate projections.
"""
from __future__ import annotations
from collections import deque
import csv, hashlib, json, math, os, time
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import numpy as np
import xarray as xr

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=HERE/"circuit_outputs"
RAW=OUT/"original_netcdf"
RASTER=OUT/"inputs"
for p in (OUT,RAW,RASTER):p.mkdir(exist_ok=True,parents=True)
COLS=432
SITES=("ARDL","BISC","LION","LLAN","PCHA","PETE")
SITE_PINS={"ARDL":65774,"BISC":71828,"LION":64911,"LLAN":65343,"PCHA":72260,"PETE":72693}
SAMPLES={
 1993:"944be76f732c07e550703e20cb1c7c561270153e60a64d0e9399cedb812c39f8",
 2018:"620d242d86b0db26fe81a2b7c41f136d91ec0a357be32fa2d89b9ccf666e7eeb"}
COORD_SHA="5a211a0eaa63b6a5d3516353dd9431428618dbd3"
YLO,YHI=120,201
XLO,XHI=75,156
NODATA=-9999
MODELS=(("uniform",0.),("ice_penalty",2.),("ice_favor",-2.))
NEIGH=(8,4)

def gitblob(data:bytes)->str:
 return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
def get_year(year):
 filename=f"ice_conc_sh_ease2-250_cdr-v3p1_{year}09.nc"
 url=f"https://thredds.met.no/thredds/fileServer/osisaf/met.no/reprocessed/ice/conc_450a1_files/monthly/{year}/{filename}"
 path=RAW/filename
 if not path.exists():
  err=None
  for attempt in range(3):
   try:
    with urlopen(Request(url,headers={"User-Agent":"mina-circuitscape-native-v1/20261108"}),timeout=80) as req:
     if urlparse(req.geturl()).hostname!="thredds.met.no":raise ValueError("publisher redirect host changed")
     data=req.read(12000001)
    if len(data)>12000000 or not(data.startswith(b"CDF") or data.startswith(b"\x89HDF")):
     raise ValueError("invalid NetCDF file")
    p=path.with_suffix(".part");p.write_bytes(data);p.replace(path)
    break
   except Exception as e:
    err=e;time.sleep(attempt+1)
  if not path.exists():raise RuntimeError(f"{filename}: {err}")
 data=path.read_bytes()
 sha=hashlib.sha256(data).hexdigest()
 if sha!=SAMPLES[year]:raise ValueError(f"Publisher source hash drift {filename}: {sha}")
 with xr.open_dataset(path) as ds:
  assert str(ds.attrs.get("product_version"))=="3.1"
  assert ds.ice_conc.shape==(1,COLS,COLS)
  x=np.asarray(ds.xc.values,dtype=float);y=np.asarray(ds.yc.values,dtype=float)
  ice=np.asarray(ds.ice_conc.values[0],dtype=float)
  flag=np.asarray(ds.status_flag.values[0],dtype=float)
  if not math.isclose(abs(x[1]-x[0]),25.,abs_tol=0.001):raise ValueError("Unexpected EASE2 x pixels")
  if not math.isclose(abs(y[1]-y[0]),25.,abs_tol=0.001):raise ValueError("Unexpected EASE2 y pixels")
  if not(np.allclose(abs(np.diff(x)),25.) and np.allclose(abs(np.diff(y)),25.)):
   raise ValueError("Inconsistent geospatial cell pitch")
  fi=np.where(np.isfinite(flag),flag,32767).astype(np.int32)
  ocean=np.isfinite(flag)&((fi&3)==0)&np.isfinite(ice)
  ice=np.where(ocean,ice,np.nan)
  if np.any((ice[ocean]<0)|(ice[ocean]>100.001)):raise ValueError("SIC outside physical bounds")
  return {"url":url,"sha256":sha,"bytes":len(data),
    "ice":ice[YLO:YHI,XLO:XHI],"valid":ocean[YLO:YHI,XLO:XHI],
    "x":x[XLO:XHI],"y":y[YLO:YHI],
    "all_ocean_cells":int(ocean.sum())}

def component(seed,mask,eight):
 h,w=mask.shape;queue=deque([seed]);seen=np.zeros_like(mask,bool);seen[seed]=True
 steps=((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)) if eight else ((1,0),(-1,0),(0,1),(0,-1))
 while queue:
  y,x=queue.popleft()
  for a,b in steps:
   yy,xx=y+a,x+b
   if 0<=yy<h and 0<=xx<w and mask[yy,xx] and not seen[yy,xx]:
    seen[yy,xx]=True;queue.append((yy,xx))
 return seen

def ascii_grid(path,values,x,y,fmt):
 # ArcInfo ASCII maps list the north-most row first and west-most column first.
 # xc/yc are in source file km units. Coordinate projection is EASE2, not WGS84.
 a=np.asarray(values)
 if x[1]<x[0]:a=np.fliplr(a)
 if y[1]>y[0]:a=np.flipud(a)
 with open(path,"w",encoding="ascii") as f:
  f.write(f"ncols {len(x)}\nnrows {len(y)}\nxllcorner {min(x)-12.5:.8f}\nyllcorner {min(y)-12.5:.8f}\ncellsize 25\nNODATA_value {NODATA}\n")
  np.savetxt(f,a,fmt=fmt)
def oriented_index(orig_native_flat,x,y):
 row,col=divmod(orig_native_flat,COLS)
 if not(YLO<=row<YHI and XLO<=col<XHI):raise ValueError("Focal node outside frozen crop")
 rr=row-YLO;cc=col-XLO
 if y[1]>y[0]:rr=(YHI-YLO)-rr-1
 if x[1]<x[0]:cc=(XHI-XLO)-cc-1
 return rr,cc

def main():
 pin=(ROOT/"outputs/sic_spatial_coherence_macro40_v1/macro40_site_coordinates.csv").read_bytes()
 if gitblob(pin)!=COORD_SHA:raise ValueError("Original 40-site geo source changed")
 dataset={yr:get_year(yr) for yr in SAMPLES}
 d93=dataset[1993];d18=dataset[2018]
 if not(np.array_equal(d93["x"],d18["x"]) and np.array_equal(d93["y"],d18["y"])):
  raise ValueError("Original EASE2 coordinate drift")
 x,y=d93["x"],d93["y"]
 common=d93["valid"]&d18["valid"]
 nodes={}
 for idx,site in enumerate(SITES,1):
  original=SITE_PINS[site];r,c=divmod(original,COLS);rr=r-YLO;cc=c-XLO
  if not common[rr,cc]:raise ValueError(f"Frozen original node no longer valid sea pixel: {site}")
  nodes[site]={"source_id":idx,"native_flat_index":original,"native_row":r,"native_col":c,
    "local_row":rr,"local_col":cc}
 near8=component((nodes[SITES[0]]["local_row"],nodes[SITES[0]]["local_col"]),common,True)
 if any(not near8[z["local_row"],z["local_col"]] for z in nodes.values()):
  raise ValueError("All sites are not eight-neighbor physically connected in this fixed crop")
 # Exclude independent disconnected ocean components, ensuring one identifiable reference component.
 supported_mask=near8
 near4=component((nodes[SITES[0]]["local_row"],nodes[SITES[0]]["local_col"]),supported_mask,False)
 four_ok=all(bool(near4[z["local_row"],z["local_col"]]) for z in nodes.values())
 points=np.full(common.shape,NODATA,dtype=int)
 for site,v in nodes.items():
  points[v["local_row"],v["local_col"]]=v["source_id"]
 ascii_grid(RASTER/"six_focal_nodes.asc",points,x,y,"%d")
 manifest=[]
 for yr in sorted(SAMPLES):
  ice=dataset[yr]["ice"]
  for name,beta in MODELS:
   vals=np.full(common.shape,NODATA,dtype=np.float64)
   vals[supported_mask]=np.exp(beta*ice[supported_mask]/100.)
   if np.any(~np.isfinite(vals[supported_mask])):raise ValueError("Bad resistance")
   if not np.all(vals[supported_mask]>0):raise ValueError("Resistance nonpositive")
   asc=RASTER/f"r_{yr}_{name}.asc"
   ascii_grid(asc,vals,x,y,"%.12f")
   for neighbor in NEIGH:
    if neighbor==4 and (not four_ok or name=="ice_favor"):
     continue
    key=f"{yr}_{name}_{neighbor}n"
    manifest.append({"key":key,"year":yr,"model":name,"beta":beta,
      "neighbor_count":neighbor,"habitat_raster":str(asc.relative_to(OUT)),
      "focal_raster":"inputs/six_focal_nodes.asc",
      "write_cumulative_current_map":bool(neighbor==8 and name in ("uniform","ice_penalty")),
      "min_resistance":float(vals[supported_mask].min()),
      "mean_resistance":float(vals[supported_mask].mean()),
      "max_resistance":float(vals[supported_mask].max())})
 result={"status":"INPUTS_READY" if four_ok else "INPUTS_READY_8_NEIGHBOR_ONLY",
   "n_focal_sites":len(SITES),"focal_sites":nodes,
   "source_url_sha256":{str(k):{n:v[n] for n in ("url","sha256","bytes","all_ocean_cells")} for k,v in dataset.items()},
   "crop_native_y":[YLO,YHI],"crop_native_x":[XLO,XHI],
   "crop_native_shape":list(common.shape),"common_valid_ocean_cells_in_crop":int(common.sum()),
   "source_connected_8_neighbor_ocean_cells":int(supported_mask.sum()),
   "four_neighbor_all_six_connected":bool(four_ok),
   "projection_units":"OSI SAF original EASE2 km coordinates, not WGS84",
   "x_reversed_for_ESRI_ASCII":bool(x[1]<x[0]),
   "y_reversed_for_ESRI_ASCII":bool(y[1]>y[0]),
   "source_input_coordinates_git_blob":COORD_SHA,
   "circuit_scenarios":manifest,
   "scientific_boundary":"Physical model-only R=exp(beta*SIC/100); zero calibrated penguin movement coefficients."}
 (OUT/"build_manifest.json").write_text(json.dumps(result,indent=2)+"\n")
 with (OUT/"circuit_scenarios.tsv").open("w",encoding="utf-8") as scenario_f:
  scenario_f.write("key\tyear\tmodel\tbeta\tneighbor_count\thabitat_raster\tfocal_raster\twrite_current\n")
  for row in manifest:
   scenario_f.write("\t".join(str(row[k]) for k in ("key","year","model","beta","neighbor_count","habitat_raster","focal_raster","write_cumulative_current_map"))+"\n")
 print("CIRCUIT_INPUT_GATE="+json.dumps({"status":result["status"],"n_inputs":len(manifest),
   "supported_ocean":result["source_connected_8_neighbor_ocean_cells"],
   "four_neighbor_all_six_connected":four_ok,
   "crop_shape":result["crop_native_shape"],
   "selected_nodes":nodes}),flush=True)
 if not four_ok:\n  print("SOURCE_WARNING=four-neighbor not supported by all six nodes; eight-neighbor pilot remains valid",flush=True)
if __name__=="__main__":main()
