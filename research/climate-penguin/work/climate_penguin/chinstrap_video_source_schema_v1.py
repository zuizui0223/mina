"""Read public Dryad video-labelled chinstrap 2018/19 original CSV schema only.

DOI 10.5061/dryad.x69p8czmk; no outcomes opened; do not assume
BAS GPS/TDR version2 tags are the SAME original camera-labelled birds.
"""
import argparse,csv,hashlib,io,json,re,zipfile
from collections import Counter
from pathlib import Path
NAME="ChinstrapForagingDiveOutcomesVariables.csv"
DOI="10.5061/dryad.x69p8czmk"
def audit(zip_path):
    if not zipfile.is_zipfile(zip_path):
        raise ValueError("original Dryad dataset download is not ZIP")
    with zipfile.ZipFile(zip_path) as source:
        found=[n for n in source.namelist() if Path(n).name==NAME]
        if len(found)!=1:
            raise ValueError("expected exactly one video-validated original CSV, got "+str(found))
        raw=source.read(found[0])
        try:text=raw.decode("utf-8-sig");encoding="utf-8-sig"
        except UnicodeDecodeError:
            text=raw.decode("cp1252");encoding="cp1252"
        it=csv.reader(io.StringIO(text))
        fields=[h.strip() for h in next(it)]
        if len(fields)<5 or len(fields)!=len(set(fields)):
            raise ValueError("invalid original camera header")
        n=0; widths=Counter()
        for row in it:
            if not row or not any(x.strip() for x in row):continue
            n+=1;widths[len(row)]+=1
        if n!=770:raise ValueError(f"original camera rows changed: {n} vs 770")
        readmes=[p for p in source.namelist() if Path(p).name=="README_file.txt"]
        return {"status":"FIRST_PARTY_VIDEO_DIVE_SOURCE_SCHEMA_VALIDATED_NO_OUTCOMES_OPENED",
                "doi":DOI,"original_member_name":NAME,"original_member_sha256":hashlib.sha256(raw).hexdigest(),
                "original_archive_sha256":hashlib.sha256(Path(zip_path).read_bytes()).hexdigest(),
                "original_member_bytes":len(raw),"source_n_dives":n,
                "source_n_video_annotated_birds_from_publication":16,
                "source_breeding_season":"2018/19 Signy",
                "csv_encoding":encoding,"csv_columns":fields,
                "source_record_field_widths":dict(widths),
                "readme_exists":bool(readmes),
                "source_readme_sha256":hashlib.sha256(source.read(readmes[0])).hexdigest() if readmes else None,
                "id_candidate_columns":[h for h in fields if re.search(r"bird|animal|tag|individual|deploy|^id$",h,re.I)],
                "time_candidate_columns":[h for h in fields if re.search(r"time|date|season|year",h,re.I)],
                "coordinate_candidates":[h for h in fields if re.search(r"lat|lon|position|coord",h,re.I)],
                "outcome_candidate_columns":[h for h in fields if re.search(r"krill|capture|prey|encounter|swarm|success",h,re.I)],
                "raw_outcome_values_opened":False,
                "native_BAS_v2_deployment_crosswalk_established":False,
                "warnings":[
                  "2022 published video labels, not independent new observations by mina.",
                  "Video capture events are verified for one season and limited birds, not 770 independent island years.",
                  "Do not equate camera IDs with BAS version2 GPS/TDR IDs absent original matching metadata.",
                  "Do not train/select a foraging classifier based on information from future validation individuals.",
                  "Neither video nor modelled krill independently identifies sea ice/salinity causal effect."
                ]}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args();result=audit(a.source)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in ("status","source_member_sha256","source_n_dives","csv_columns","id_candidate_columns","time_candidate_columns","outcome_candidate_columns")},ensure_ascii=False))
if __name__=="__main__": main()
