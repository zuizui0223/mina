"""Source-first retrieval audit for Dunn 2018 Signy mean hatching dates.

Expected public DOI 10.5285/274b49bd-40a4-4e5d-bd5f-69a1ba09d403.
Do not digitize published figure or infer raw nests from mean estimates.
No environmental associations until date units, original source grain and
source year coverage are established. This entry may be source-restricted.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,zipfile
from pathlib import Path

DOI="10.5285/274b49bd-40a4-4e5d-bd5f-69a1ba09d403"
SOURCE="https://ramadda.data.bas.ac.uk/repository/entry/show?entryid=274b49bd-40a4-4e5d-bd5f-69a1ba09d403&output=zip.tree"
def run(original,outdir):
    original,outdir=Path(original),Path(outdir)
    raw=original.read_bytes()
    if not zipfile.is_zipfile(original):
        raise ValueError("DOI entry did not return source archive ZIP: "+raw[:130].decode("utf-8","replace"))
    inventories=[]
    with zipfile.ZipFile(original) as z:
        for item in sorted(z.infolist(),key=lambda x:x.filename):
            if item.is_dir():continue
            name=item.filename
            ext=name.rsplit(".",1)[-1].lower() if "." in name else ""
            content=z.read(item)
            result={"path":name,"size_bytes":len(content),
                "original_file_sha256":hashlib.sha256(content).hexdigest(),
                "extension":ext}
            if ext in ("csv","tsv","txt"):
                enc=None; decoded=None
                for tryencoding in ("utf-8-sig","utf-8","cp1252","latin1"):
                    try:decoded=content.decode(tryencoding);enc=tryencoding;break
                    except UnicodeError:pass
                if decoded is None:raise ValueError("Cannot decode source "+name)
                result["encoding"]=enc
                result["first_3_source_lines"]=decoded.splitlines()[:3]
                rows=list(csv.reader(io.StringIO(decoded),delimiter="\t" if ext=="tsv" else ","))
                if rows:
                    result["columns"]=rows[0]
                    result["n_data_rows"]=max(0,len(rows)-1)
                    result["first_4_original_rows"]=rows[1:5]
            elif ext in ("xlsx","xls"):
                import pandas as pd
                xl=pd.ExcelFile(io.BytesIO(content))
                result["sheets"]={}
                for sheet in xl.sheet_names:
                    frame=pd.read_excel(xl,sheet_name=sheet)
                    result["sheets"][sheet]={"n_rows":len(frame),
                        "columns":list(map(str,frame.columns)),
                        "first_4_rows":frame.head(4).fillna("").astype(str).to_dict("records")}
            inventories.append(result)
    if not inventories:raise ValueError("Empty source ZIP")
    summary={"state":"original_public_source_structure_audited_not_yet_time_climate_response",
      "source_doi":DOI,"source_url":SOURCE,
      "original_zip_size":len(raw),"original_zip_sha256":hashlib.sha256(raw).hexdigest(),
      "n_files":len(inventories),"files":inventories,
      "existing_article_results_not_new":"Clewlow et al. 2019: both species ~1.02 days/degree C, mean gap ~27.89 days, shared response.",
      "limitations":["Published mean hatching dates may be model derived, not individual nest dates",
        "Colony A41->A39 and C69->C66 transitions must be kept as site changes",
        "No 1997/98, 1999/00 or 2010/11 nest observations per catalog",
        "Mean hatching and back-calculated laying must not be double-counted",
        "Do not convert camera settlement dates into laying date without direct ground truth",
        "No warming causal inference and no CMIP6 biological projection"]}
    outdir.mkdir(parents=True,exist_ok=True)
    (outdir/"source_inventory.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"source_doi":DOI,"source_zip_sha256":summary["original_zip_sha256"],
        "files":inventories},ensure_ascii=False,indent=2))
    return summary

def match_ice(source,outdir):
    """Real publisher mean hatching 17-year pair vs original OSI SAF September/Aug-Nov."""
    import datetime,math,statistics
    from collections import defaultdict
    expected_csv_sha="d86d42a581ec8f5bdf123a2073de17469714ce85031914c32b2489afc2187c94"
    ice_blob="4fcea71c2d8b1069b6ad143f6522061ed434daf5"
    with zipfile.ZipFile(source) as z:
        fname=[a for a in z.namelist() if a.lower().endswith(".csv")]
        if len(fname)!=1:raise ValueError("Expected exactly 1 hatching source CSV")
        original=z.read(fname[0])
    if hashlib.sha256(original).hexdigest()!=expected_csv_sha:
        raise ValueError("Source original hatching SHA drift")
    rows=list(csv.reader(io.StringIO(original.decode("utf-8-sig"))))
    heads=[i for i,r in enumerate(rows) if len(r)>=6 and r[0]=="Season" and r[1]=="Species"]
    if len(heads)!=1:raise ValueError("Publisher season/species header not uniquely found")
    original_data=[]
    for r in rows[heads[0]+1:]:
        if not any(x.strip() for x in r):continue
        if len(r)<6:raise ValueError("Source hatching row width drift")
        season=r[0].strip()
        if not(len(season)==7 and season[4]=="_" and season[:4].isdigit() and season[5:].isdigit()):
            raise ValueError("Unexpected source season "+season)
        year=int(season[:4])
        if int(season[5:])!=(year+1)%100:raise ValueError("Source season span invalid")
        raw_sp=r[1].lower().replace("é","e")
        sp="Chinstrap" if "chinstrap" in raw_sp else "Adelie" if "adelie" in raw_sp else None
        if sp is None:raise ValueError("Unknown species "+r[1])
        calendar=datetime.datetime.strptime(r[3].strip(),"%d/%m/%Y").date()
        hatch=float(r[4]);lay=float(r[5])
        if abs((calendar-datetime.date(year,10,1)).days-hatch)>1:
            raise ValueError("Calendar hatching date is inconsistent "+str((year,sp,calendar,hatch)))
        if abs(lay-(hatch-(35 if sp=="Adelie" else 36.4)))>.051:
            raise ValueError("Source back-calculated laying day mismatch")
        original_data.append(dict(year=year,species=sp,hatching_calendar_date=calendar.isoformat(),
          hatching_days_after_Oct1=hatch,derived_laying_days_after_Oct1=lay,
          colony_label=("A41" if year<2003 else "A39") if sp=="Adelie" else "C69",
          source_biological_grain="published species x season model-estimated mean, not 100 independent nest hatching records"))
    if len(original_data)!=34:raise ValueError("Expected 34 original species-seasons, got "+str(len(original_data)))
    paired=defaultdict(dict)
    for row in original_data:
        if row["species"] in paired[row["year"]]:raise ValueError("Duplicate species-year")
        paired[row["year"]][row["species"]]=row
    if len(paired)!=17 or any(set(t)!={"Adelie","Chinstrap"} for t in paired.values()):
        raise ValueError("Expected 17 full species-pair seasons")
    # GOPT original satellite source nearshore 0-100km, distinct from 20km camera winter SIC.
    ice_path=Path(__file__).resolve().parents[2]/"outputs/climate_penguin/macro_monthly_seaice_1991_2020.csv"
    raw=ice_path.read_bytes()
    sha=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if sha!=ice_blob:raise ValueError("Original OSI monthly source SHA drift")
    with ice_path.open(encoding="utf8",newline="") as stream:
        records=list(csv.DictReader(stream))
    if len(records)!=9600:raise ValueError("Original satellite row count changed")
    ice={}
    for r in records:
        if r["site_id"]=="GOPT" and r["inner_km"]=="0":
            if r["complete_month"]!="True":raise ValueError("GOPT month incomplete")
            k=(int(r["year"]),int(r["month"]))
            if k in ice:raise ValueError("Duplicate GOPT monthly ice")
            ice[k]=float(r["sic_mean"])
    def mean(a):return sum(a)/len(a)
    def cor(a,b):
        if len(a)<3:return None
        ma,mb=mean(a),mean(b)
        av=[x-ma for x in a];bv=[y-mb for y in b]
        den=math.sqrt(sum(x*x for x in av)*sum(y*y for y in bv))
        return sum(x*y for x,y in zip(av,bv))/den if den>1e-12 else None
    def slope(a,b):
        ma,mb=mean(a),mean(b)
        den=sum((x-ma)**2 for x in a)
        return sum((x-ma)*(y-mb) for x,y in zip(a,b))/den if den else None
    def detrend(a,years):
        b=slope(years,a);ya=mean(years);ma=mean(a)
        return [y-ma-b*(t-ya) for y,t in zip(a,years)]
    out=[]
    for yr,t in sorted(paired.items()):
        a,c=t["Adelie"],t["Chinstrap"]
        m=[ice[(yr,i)] for i in (8,9,10,11)]
        out.append(dict(year=yr,Adelie_colony=a["colony_label"],Chinstrap_colony=c["colony_label"],
          Adelie_hatching_day_after_Oct1=a["hatching_days_after_Oct1"],
          Chinstrap_hatching_day_after_Oct1=c["hatching_days_after_Oct1"],
          Chinstrap_minus_Adelie_hatching_gap_days=c["hatching_days_after_Oct1"]-a["hatching_days_after_Oct1"],
          Chinstrap_minus_Adelie_laying_gap_days=c["derived_laying_days_after_Oct1"]-a["derived_laying_days_after_Oct1"],
          GOPT_September_ice_pct=m[1],GOPT_October_ice_pct=m[2],GOPT_AugNov_ice_pct=mean(m)))
    if len(out)!=17:raise ValueError("Unexpected 17 paired hatching years")
    year=[r["year"] for r in out]
    metric="Chinstrap_minus_Adelie_hatching_gap_days"
    attrs=("GOPT_September_ice_pct","GOPT_AugNov_ice_pct","GOPT_October_ice_pct")
    contrasts=[]
    for response in (metric,"Adelie_hatching_day_after_Oct1","Chinstrap_hatching_day_after_Oct1"):
        for attr in attrs:
            x=[r[attr] for r in out];y=[r[response] for r in out]
            loo=[cor(x[:i]+x[i+1:],y[:i]+y[i+1:]) for i in range(17)]
            pairs=[(r,s) for r,s in zip(out,out[1:]) if s["year"]==r["year"]+1]
            diffx=[s[attr]-r[attr] for r,s in pairs]
            diffy=[s[response]-r[response] for r,s in pairs]
            shift=[cor(x,y[i:]+y[:i]) for i in range(17)]
            original_r=cor(x,y)
            contrasts.append(dict(response=response,predictor=attr,n_seasons=17,
              pearson_r=original_r,slope_response_days_per_10pp=10*slope(x,y),
              year_detrended_r=cor(detrend(x,year),detrend(y,year)),
              contiguous_year_intervals=len(pairs),first_difference_r=cor(diffx,diffy),
              loo_r_min=min(loo),loo_r_max=max(loo),
              circular_shift_17year_extreme=sum(abs(z)+1e-12>=abs(original_r) for z in shift),
              exact_17_circular_phases=17,
              climate_year_exchangeability_unverified=True))
    summary=dict(status="17_source_original_pair_seasons_ice_match_descriptive_not_causal",
      source_doi=DOI,source_hatching_CSV_sha256=expected_csv_sha,
      source_1991_2020_GOPT_seaice_git_blob=ice_blob,
      source_original_species_seasons=len(original_data),n_paired_hatching_years=len(out),
      years=year,mean_hatching_gap_days=mean([r[metric] for r in out]),
      median_hatching_gap_days=statistics.median(r[metric] for r in out),
      range_hatching_gap_days=[min(r[metric] for r in out),max(r[metric] for r in out)],
      mean_laying_gap_days=mean([r["Chinstrap_minus_Adelie_laying_gap_days"] for r in out]),
      pre2003_adelie_colony_A41_n=sum(r["year"]<2003 for r in out),
      post2003_adelie_colony_A39_n=sum(r["year"]>=2003 for r in out),
      mean_gap_pre2003=mean([r[metric] for r in out if r["year"]<2003]),
      mean_gap_post2003=mean([r[metric] for r in out if r["year"]>=2003]),
      full_17yr_diagnostics=contrasts,
      caveats=["A41 changes to A39 in 2003, temporal gap difference can reflect source-colony switch",
        "The Chinstrap chronology C69/C66 switch in 2016 is beyond this source series",
        "Published mean hatching dates are derived from 100-nest monitoring, not source individual nest dates",
        "Laying dates are deterministic shifts of hatching dates; not independent validation",
        "Ice GOPT 0-100km nearby is not measured October air temperature or 20km camera winter ice",
        "17 years from one island, with missing original years, not independent geographic replication",
        "Exploratory year-detrended and circular shift diagnostics do not identify climate causality",
        "No CMIP6 biological phenology, species competition or nesting count prediction"])
    outdir=Path(outdir)
    def write(path,records):
        with (outdir/path).open("w",encoding="utf8",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    write("original_34_species_seasons.csv",original_data)
    write("paired_17year_hatching_ice.csv",out)
    write("climate_hatching_diagnostics.csv",contrasts)
    (outdir/"hatching_ice_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"n_paired_years":summary["n_paired_hatching_years"],
       "mean_hatching_gap_days":summary["mean_hatching_gap_days"],
       "mean_gap_pre2003":summary["mean_gap_pre2003"],
       "mean_gap_post2003":summary["mean_gap_post2003"],
       "diagnostics":contrasts},ensure_ascii=False,indent=2))
    return summary

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path);p.add_argument("--out",required=True,type=Path)
    a=p.parse_args();run(a.source,a.out);match_ice(a.source,a.out)
