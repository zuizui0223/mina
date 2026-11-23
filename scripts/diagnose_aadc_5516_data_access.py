#!/usr/bin/env python3
"""Diagnose Australian Antarctic Data Centre download route for 1991–2019 Mac. Robertson colony counts."""
import urllib.request,urllib.error,json,re,hashlib,datetime
from pathlib import Path
O=Path("build/aadc_endpoint_diagnostic");O.mkdir(parents=True,exist_ok=True)
urls={
  "mawson_2022":"https://data.aad.gov.au/eds/5516/download",
  "bechervaise_2017":"https://data.aad.gov.au/eds/1356/download",
  "mawson_metadata":"https://data.aad.gov.au/metadata/records/AAS_4518_MacRobertson_Land_Adelie_Penguins",
  "bechervaise_metadata":"https://data.aad.gov.au/metadata/records/breeding_success_BI",
  "windmill_metadata":"https://data.aad.gov.au/metadata/records/AAS_4518_AAS_Reproductive_Success_Windmill_Islands"
}
out={"created_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"source":{}}
for key,url in urls.items():
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; OpenEcologicalResearch/1.0)","Accept":"*/*"})
        with urllib.request.urlopen(req,timeout=70) as resp:
            body=resp.read(1500000);ctype=resp.headers.get("Content-Type","");final=resp.url
        data={"status":"retrieved","contenttype":ctype,"final_url":final,"bytes":len(body),
              "sha256":hashlib.sha256(body).hexdigest(),"first400_printable":body[:400].decode("utf-8","replace")}
        if body.lstrip().startswith(b"{"):
            try:
                obj=json.loads(body)
                data["json_keys"]=list(obj)
                if obj.get("data") and isinstance(obj["data"],dict):
                    md=obj["data"]
                    data["entry_title"]=md.get("entry_title")
                    data["online_resources"]=str(md.get("data_set_citation",{}).get("online_resource"))[:500]
                    data["urls_in_json"]=sorted(set(re.findall(r"https?://[a-zA-Z0-9./_?&=%:+\-]+",str(md))))[:20]
            except Exception as e: data["json_parse_error"]=str(e)
        elif ctype.startswith("text/html") or body.lower().lstrip().startswith(b"<!doctype"):
            (O/(key+"_response.html")).write_bytes(body)
            data["html_title"]=re.search(r"<title[^>]*>(.*?)</title>",body.decode("utf-8","replace"),re.I|re.S).group(1) if re.search(r"<title[^>]*>(.*?)</title>",body.decode("utf-8","replace"),re.I|re.S) else None
            data["urls_inside"]=sorted(set(re.findall(r"https?://[a-zA-Z0-9./_?&=%:+\-]+",body.decode("utf-8","replace"))))[:30]
        out["source"][key]=data
        print(key,data["status"],"ctype",ctype,"bytes",len(body),"title",data.get("html_title"),flush=True)
    except Exception as e:
        out["source"][key]={"status":"unavailable","error":str(e),"url":url}
        print("UNAVAILABLE",key,str(e)[:150],flush=True)
(O/"aadc_source_route_diagnostic.json").write_text(json.dumps(out,indent=2)+"\n")
