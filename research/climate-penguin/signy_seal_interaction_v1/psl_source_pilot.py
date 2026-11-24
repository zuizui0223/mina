"""Single alternate-distribution OISST source audit, no outcome join."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import requests,xarray as xr
URL="https://psl.noaa.gov/thredds/fileServer/Datasets/noaa.oisst.v2.highres/icec.day.mean.1999.nc"
def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    rec={"url":URL,"year":1999,"status":"SOURCE_PILOT_BLOCKED","outcome_joined":False}
    try:
        f=a.out/"psl_1999.nc";h=hashlib.sha256()
        with requests.get(URL,stream=True,timeout=(20,90)) as r:
            r.raise_for_status()
            with f.open("wb") as w:
                for b in r.iter_content(1024*1024):
                    if b:w.write(b);h.update(b)
        rec.update(sha256=h.hexdigest(),bytes=f.stat().st_size)
        with xr.open_dataset(f) as ds:
            da=ds["icec"].sel(time=slice("1999-05-01","1999-10-31"),lat=slice(-61.875,-60.125),lon=slice(313.125,315.875)).transpose("time","lat","lon")
            d=pd.DatetimeIndex(da.time.values).normalize()
            if not d.equals(pd.date_range("1999-05-01","1999-10-31")) or da.shape!=(184,8,12) or not np.allclose(da.lat,np.arange(-61.875,-60,.25)) or not np.allclose(da.lon,np.arange(313.125,316,.25)):raise ValueError("calendar/grid mismatch")
            vals=da.values.astype(float);finite=np.isfinite(vals)
            rec.update(status="PSL_SOURCE_MISSINGNESS_AUDITED",shape=list(vals.shape),units=str(da.attrs.get("units")),valid_range=str(da.attrs.get("valid_range")),finite_range=[float(vals[finite].min()),float(vals[finite].max())] if finite.any() else None,cell_count_any=int(finite.any(axis=0).sum()),cell_count_all=int(finite.all(axis=0).sum()),missing_fraction=float(1-finite.mean()),same_D1_mask_gate_pass=bool(finite.any() and finite[:,finite.any(axis=0)].all()))
    except Exception as e:rec["error"]=str(e)
    (a.out/"psl_source_pilot.json").write_text(json.dumps(rec,indent=2)+"\n");print(json.dumps(rec))
if __name__=="__main__":main()
