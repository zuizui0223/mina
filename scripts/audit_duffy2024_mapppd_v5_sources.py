#!/usr/bin/env python3
"""Independent source manifest for Duffy 2024 1979-2022 polynyas + MAPPPD v5 2026.
Source metadata only; no ecology model, no unsupported colony counts.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin
import urllib.request
import datetime, hashlib, json, re, time

FIG_ID="24768654"
class Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.anchors=[];self.scripts=[];self._anchor=None
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=="a": self._anchor={"href":d.get("href",""),"text":""}
        if tag=="script" and d.get("src"):self.scripts.append(d.get("src"))
    def handle_data(self,data):
        if self._anchor:self._anchor["text"]+=data
    def handle_endtag(self,tag):
        if tag=="a" and self._anchor:
            self.anchors.append(self._anchor);self._anchor=None
def get(url,limit=5_000_000):
    request=urllib.request.Request(url,headers={"User-Agent":"research-polynya-MAPPPD-original-data-audit/1.0","Accept":"application/json,text/html;q=0.9,*/*;q=0.8"})
    with urllib.request.urlopen(request,timeout=75) as r:
        body=r.read(limit+1)
        if len(body)>limit:raise ValueError(f"Too large for source manifest ({url})")
        return body
def main():
    out=Path("build/polynya44_source_metadata");out.mkdir(parents=True,exist_ok=True)
    record={"date_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"source_scope":"original open public records only","year_window":[1979,2022],"not_an_ecological_fit":True}
    u="https://api.figshare.com/v2/articles/"+FIG_ID
    try:
        obj=json.loads(get(u))
        fs=[{k:f.get(k) for k in ("id","name","size","computed_md5","download_url","is_link_only")} for f in obj.get("files",[])]
        record["figshare"]={"status":"verified","id":obj.get("id"),"doi":obj.get("doi"),
          "title":obj.get("title"),"published_date":obj.get("published_date"),"version":obj.get("version"),
          "license":obj.get("license"),"url":obj.get("url_public_html"),"files":fs,
          "files_total_bytes":sum(f.get("size") or 0 for f in fs)}
        assert str(obj.get("id"))==FIG_ID, "Figshare 24768654 record mismatch"
        assert fs, "No downloadable Figshare file objects"
    except Exception as e:
        record["figshare"]={"status":"UNRESOLVED","error":repr(e)}
    for host in ["https://penguinmap.com/mapppd/","https://www.penguinmap.com/mapppd/"]:
        key="mapppd_"+host.split("/")[2].replace(".","_")
        try:
            body=get(host)
            txt=body.decode("utf-8","replace")
            p=Anchors();p.feed(txt)
            links=[{"href":urljoin(host,a["href"]),"text":a["text"].strip()[:80]}
                for a in p.anchors if re.search(r"api|csv|download|data|darwin|all count|export|endpoint",a["href"]+" "+a["text"],re.I)]
            scripts=[urljoin(host,s) for s in p.scripts]
            save={"status":"verified_html","response_bytes":len(body),"sha256":hashlib.sha256(body).hexdigest(),
                  "title":re.search(r"<title[^>]*>(.*?)</title>",txt,re.I|re.S).group(1) if re.search(r"<title[^>]*>(.*?)</title>",txt,re.I|re.S) else None,
                  "links":links[:100],"scripts":scripts[:50],
                  "count_claims":re.findall(r".{0,70}(?:729|5487|5,487|2025/2026|v5\.0).{0,70}",txt,re.I)[:12],
                  "possible_api_paths":sorted(set(re.findall(r'''(?i)(?:https?://[^\s"'<>]{4,180}|/(?:api|exports?|downloads?)/[a-zA-Z0-9_/?=&.%+\-]+)''',txt)))[:80]}
            record[key]=save
        except Exception as e:record[key]={"status":"UNRESOLVED","error":repr(e)}
    Path(out/"source_manifest.json").write_text(json.dumps(record,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({k:v for k,v in record.items() if k.startswith(("figshare","mapppd"))},indent=2,ensure_ascii=False))
if __name__=="__main__":main()
