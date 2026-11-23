#!/usr/bin/env python3
"""NOAA/NSIDC G02202 V4 Southern Hemisphere monthly continuous SIC source preflight."""
import datetime,hashlib,html.parser,io,json,re,urllib.request
from pathlib import Path
from urllib.parse import urljoin

SOURCES=[
"https://coastwatch.pfeg.noaa.gov/erddap/files/nsidcG02202v4shmday/",
"https://polarwatch.noaa.gov/erddap/files/nsidcG02202v4shmday/",
]
class Links(html.parser.HTMLParser):
    def __init__(self):super().__init__();self.items=[]
    def handle_starttag(self,tag,attrs):
        if tag=="a":
            for k,v in attrs:
                if k=="href":self.items.append(v)
def load(url,cap=30_000_000):
    req=urllib.request.Request(url,headers={"User-Agent":"Independent-Antarctic-Biogeography-Public-Research/1.0","Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=90) as r:
        x=r.read(cap+1)
        if len(x)>cap:raise ValueError("Received payload > cap")
        return x,{"url":r.url,"content_type":r.headers.get("Content-Type")}
def main():
    out=Path("build/nsidc_preflight");out.mkdir(parents=True,exist_ok=True)
    res={"tested_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
         "goal":"original monthly south sea-ice CDR grid header/URL, no original NetCDF redistribution",
         "probes":[]}
    for base in SOURCES:
        try:
            txt,meta=load(base,1_500_000); s=txt.decode("utf-8","replace")
            p=Links();p.feed(s)
            files=[urljoin(base,x) for x in p.items if re.search(r"seaice_conc_monthly_sh_20\d{4}.*v04.*\.nc$",x)]
            if len(files)<200:
                files=sorted(set(urljoin(base,x) for x in re.findall(r"seaice_conc_monthly_sh_20\d{4}[^\s\"'<>]*v04[^\s\"'<>]*\.nc",s)))
            res["probes"].append({"base":base,"status":"directory_ok","size":len(txt),"files_found":len(files),
                                   "sample_filenames":files[:6],
                                   "2018_06":[f for f in files if "201806" in f][:3]})
            if not files:continue
            pick=next((f for f in files if "201806" in f),next((f for f in files if "2018" in f),files[0]))
            b,m=load(pick,3_000_000)
            import netCDF4
            with netCDF4.Dataset("sample",memory=b) as n:
                dims={k:len(v) for k,v in n.dimensions.items()}
                vars={k:{"dims":v.dimensions,"shape":v.shape,"dtype":str(v.dtype),
                         "units":getattr(v,"units",None),"fill":getattr(v,"_FillValue",None)} for k,v in n.variables.items()}
                if "cdr_seaice_conc_monthly" not in vars:raise ValueError("Monthly CDR variable absent")
                if not ({"xgrid","ygrid"}<=set(vars)):raise ValueError("xgrid/ygrid absent from official file")
            res["selected"]={"url":pick,"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b),"netcdf_dimensions":dims,"netcdf_vars":vars,"original_directory":base}
            break
        except Exception as e:
            res["probes"].append({"base":base,"status":"failed","error":repr(e)[:280]})
    if "selected" not in res:
        # Guard against a false zero: the independent monthly baseline remains unverified.
        res["status"]="NO_VALIDATED_NSIDC_MONTHLY_SOURCE"
    else:res["status"]="VALIDATED_NSIDC_V4_MONTHLY_SOUTHERN_SOURCE"
    (out/"NSIDC_V4_SOUTH_MONTHLY_PREFLIGHT.json").write_text(json.dumps(res,indent=2,default=str)+"\n")
    print(json.dumps(res,indent=2,default=str))
if __name__=="__main__":main()
