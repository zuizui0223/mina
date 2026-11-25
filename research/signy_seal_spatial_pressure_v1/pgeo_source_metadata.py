"""Public source metadata gate. No private reviewer URLs or ecological outcomes."""
import hashlib,json
from pathlib import Path
import requests
OUT=Path("build/pgeo_source")
URLS={
 "meheust_figshare":"https://api.figshare.com/v2/articles/22341229",
 "meheust_datacite":"https://api.datacite.org/dois/10.6084/m9.figshare.22341229",
 "barbraud2015_dryad":"https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.3c2v9",
 "youngflesh2021_dryad_metadata_only":"https://datadryad.org/api/v2/datasets/doi%3A10.5068%2FD1KT10"
}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    result={"status":"PUBLIC_METADATA_AUDIT_ONLY","ecological_fit":False,"files_downloaded":False,"contact_required_for_youngflesh2021_data":True,"sources":{}}
    for key,url in URLS.items():
        v={"url":url};result["sources"][key]=v
        try:
            with requests.get(url,timeout=(15,45),allow_redirects=False,stream=True) as r:
                v["http_status"]=r.status_code
                v["location_header"]=r.headers.get("Location")
                if r.status_code!=200:continue
                b=bytearray()
                for c in r.iter_content(65536):
                    b.extend(c)
                    if len(b)>3_000_000:raise ValueError("metadata size bound")
                raw=bytes(b);j=json.loads(raw)
                v.update(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
                if key=="meheust_figshare":
                    if j.get("id")!=22341229 or str(j.get("doi","")).lower()!="10.6084/m9.figshare.22341229":raise ValueError("figure repository identity mismatch")
                    v.update(title=j.get("title"),license=j.get("license"),files=[{k:f.get(k) for k in ("id","name","size","downloadUrl","computed_md5","supplied_md5")} for f in j.get("files",[])],is_public=j.get("is_public"))
                elif key=="meheust_datacite":
                    a=j["data"]["attributes"];v.update(doi=a.get("doi"),titles=a.get("titles"),rights=a.get("rightsList"),state=a.get("state"),url_landing=a.get("url"))
                else:
                    v.update(title=j.get("title"),identifier=j.get("identifier"),license=j.get("license"),links=j.get("_links"),usageNotes=j.get("usageNotes"))
                    # Metadata only: do not follow any data download links here.
        except Exception as e:v["error"]=f"{type(e).__name__}: {e}"[:600]
    (OUT/"receipt.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(result,ensure_ascii=False))
if __name__=="__main__":main()
