#!/usr/bin/env python3
"""Bounded inspection of Australian Antarctic Data Centre public frontend routing.
No credential, bypass, challenge solving, or restricted access: identify openly linked file endpoints only.
"""
import datetime,hashlib,json,re,urllib.request
from pathlib import Path
O=Path("build/aadc_public_frontend");O.mkdir(parents=True,exist_ok=True)
URL="https://data.aad.gov.au/assets/index-B9VUhsc-.js"
q=urllib.request.Request(URL,headers={"User-Agent":"Scientific-Open-Data-Metadata/1.0","Accept":"text/javascript,*/*"})
report={"date":datetime.datetime.now(datetime.timezone.utc).isoformat(),"url":URL}
try:
    with urllib.request.urlopen(q,timeout=70) as r:
        data=r.read(20_000_001)
        if len(data)>20_000_000:raise ValueError("Too large front-end bundle")
    report["bytes"]=len(data);report["sha256"]=hashlib.sha256(data).hexdigest()
    text=data.decode("utf-8","replace")
    keywords=["/eds/","/download","/api/","file/download","fileDownload","datasets/","dataset/","s3","api.aad.gov.au","downloadFile","downloadfile","data.aad.gov.au","fileUrl","getFiles","s3.amazonaws"]
    excerpts={}
    for keyword in keywords:
        pos=[m.start() for m in re.finditer(re.escape(keyword),text,re.I)]
        excerpts[keyword]={"occurrences":len(pos),
           "examples":[text[max(0,i-140):min(len(text),i+290)].replace("\n"," ")[:410] for i in pos[:12]]}
    report["excerpts"]=excerpts
    urls=re.findall(r"https?://[a-zA-Z0-9.:/_?&=%+\-]{5,220}",text)
    report["candidate_AADC_service_domains"]=sorted(set(u[:180] for u in urls if
        "aad.gov.au" in u or "aadc" in u.lower()))[:50]
    report["status"]="PUBLIC_FRONTEND_BUNDLE_SCANNED_FOR_DOCUMENTED_LINKS"
except Exception as e:
    report["status"]="UNAVAILABLE_PUBLIC_FRONTEND"
    report["error"]=repr(e)
(O/"AADC_original_EDS_public_interface_routes.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(json.dumps(report,indent=2,ensure_ascii=False)[:20000])
