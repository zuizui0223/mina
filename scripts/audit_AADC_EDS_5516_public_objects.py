#!/usr/bin/env python3
"""Official public AADC EDS 5516 object listing and current Download component.
Only anonymous documented GET requests; obey access controls; no credentials or presigning.
"""
from pathlib import Path
import datetime,hashlib,json,re,urllib.request,urllib.error
ROOT=Path("build/aadc_public_dataset5516")
ROOT.mkdir(parents=True,exist_ok=True)
HOST="https://data.aad.gov.au"
QUERIES={
"metadata_5516":HOST+"/eds/api/dataset/5516",
"objects_5516":HOST+"/eds/api/dataset/5516/objects?recursive=true&removeBasePath=true",
"objects_1103":HOST+"/eds/api/dataset/1103/objects?recursive=true&removeBasePath=true",
"download_component":HOST+"/assets/Download-BzctVwkO.js",
}
def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Original-Polar-Science-Public-Dataset-Metadata-Audit/1.0",
     "Accept":"application/json,application/javascript,text/javascript,*/*;q=0.7"})
    try:
        with urllib.request.urlopen(req,timeout=90) as r:
            b=r.read(3_000_001)
            if len(b)>3_000_000:raise ValueError("STOP >3MB public metadata")
            return {"http":r.status,"type":r.headers.get("Content-Type",""),"final":r.url},b
    except urllib.error.HTTPError as e:
        return {"http":e.code,"type":e.headers.get("Content-Type",""),"final":url},e.read(256)
def main():
    result={"utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "scope":"Only published anonymous GET metadata endpoints and public client docs","requests":{}}
    for name,url in QUERIES.items():
        try:
            meta,b=get(url);data={"request":url,**meta,"size":len(b)}
            if meta["http"] in (401,403):
                data["status"]="AUTHORIZATION_REQUIRED_STOP";result["requests"][name]=data;continue
            if name.startswith("objects") and meta["http"]==200:
                try:
                    j=json.loads(b)
                    data["json_type"]=type(j).__name__
                    if isinstance(j,list):
                        data["objects_count"]=len(j)
                        data["objects"]=[{k:v.get(k) for k in ("name","size","hash","lastModified","etag","isDirectory") if k in v}
                            for v in j[:150] if isinstance(v,dict)]
                    else:
                        data["json_keys"]=list(j)[:40] if isinstance(j,dict) else []
                        data["json_sample"]=str(j)[:1300]
                except Exception as e:data["json_error"]=repr(e)
            elif name=="metadata_5516" and meta["http"]==200:
                try:
                    j=json.loads(b)
                    data["dataset_identifiers"]={k:j.get(k) for k in (
                        "uuid","eds_id","dataset_name","dataset_description","status","dataset_visibility_status",
                        "dataset_visibility_status_reason","metadata_entry_id","dataset_size","accessObjects","accessDetails")}
                    data["object_fields"]={k:type(v).__name__ for k,v in j.items()}
                except Exception as e:data["json_error"]=repr(e)
            elif name=="download_component" and meta["http"]==200:
                s=b.decode("utf-8","replace")
                keys=["/eds/api/","download","file","object?","presigned","token","access","request"]
                data["snippet_matches"]={q:[s[max(0,m.start()-135):min(len(s),m.end()+220)].replace("\n"," ")[:450]
                     for m in list(re.finditer(re.escape(q),s,re.I))[:12]] for q in keys}
                data["sha256"]=hashlib.sha256(b).hexdigest()
            else:data["first200"]=b[:200].decode("utf-8","replace")
            result["requests"][name]=data
            print(name,data["http"],data.get("objects_count"),data.get("dataset_identifiers"),flush=True)
        except Exception as e:
            result["requests"][name]={"status":"SOURCE_UNAVAILABLE","error":repr(e)[:230],"url":url}
    (ROOT/"AADC_public_5516_object_access.json").write_text(json.dumps(result,indent=2,default=str)+"\n")
if __name__=="__main__":main()
