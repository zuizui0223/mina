#!/usr/bin/env python3
"""Check official *public* AADC EDS dataset search API for Mac Robertson Island datasets.
No authentication, no accesskey request, no restricted data bypass.
"""
from pathlib import Path
import datetime,json,urllib.request,urllib.parse,urllib.error
ROOT=Path("build/aadc_eds_authorized_public_probe");ROOT.mkdir(parents=True,exist_ok=True)
URL="https://data.aad.gov.au/eds/api"
QUERIES=[
 ("AADC 5516",f"{URL}/dataset/5516"),
 ("AADC 1103",f"{URL}/dataset/1103"),
 ("Bechervaise",f"{URL}/dataset?search=Bechervaise&size=50"),
 ("Mac Robertson",f"{URL}/dataset?search=Mac%20Robertson&size=50"),
 ("Adelie penguin",f"{URL}/dataset?search=Adelie%20penguin&size=50"),
]
def fetch(url,max_size=1_700_000):
    req=urllib.request.Request(url,headers={"User-Agent":"Scientific-Public-Data-Index-Audit/1.0","Accept":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=80) as r:
            content=r.read(max_size+1)
            if len(content)>max_size: raise ValueError("Unexpected public-index response > size cap")
            return {"status":r.status,"url":r.url,"content_type":r.headers.get("Content-Type","")},content
    except urllib.error.HTTPError as e:
        return {"status":e.code,"url":url,"content_type":e.headers.get("Content-Type","")},e.read(min(400,e.length or 400))
def main():
    report={"when":datetime.datetime.now(datetime.timezone.utc).isoformat(),"policy":"GET anonymous public AADC official endpoints only, stop on 401/403","queries":{}}
    for name,url in QUERIES:
        try:
            meta,b=fetch(url);v={"meta":meta,"size":len(b)}
            try:
                j=json.loads(b)
                if isinstance(j,list):
                    v["items_count"]=len(j)
                    v["items"]=[{k:x.get(k) for k in ["uuid","eds_id","name","title","description","access","status","public","is_public"] if k in x} for x in j[:30] if isinstance(x,dict)]
                elif isinstance(j,dict):
                    v["keys"]=list(j)[:35]
                    v["item"]={k:j.get(k) for k in ["uuid","eds_id","name","title","description","access","status","public","is_public"] if k in j}
                    v["json_text_sample"]=str(j)[:1000]
            except Exception:
                v["head"]=b[:250].decode("utf-8","replace")
            report["queries"][name]=v
            print(name,meta["status"],"bytes",len(b),"items",v.get("items_count"),"keys",v.get("keys"),flush=True)
        except Exception as e:
            report["queries"][name]={"status":"UNRESOLVED","error":repr(e)[:350]}
    (ROOT/"AADC_public_EDS_anonymous_search_audit.json").write_text(json.dumps(report,indent=2,default=str)+"\n")
if __name__=="__main__":main()
