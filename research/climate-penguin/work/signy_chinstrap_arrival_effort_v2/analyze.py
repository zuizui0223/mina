"""BAS source-pinned Signy chinstrap arrival-count effort and censoring audit.

The ORIGINAL measurement is counts of birds at arrival survey events, not
direct first arrival dates. Do not equate first survey or weighted sample median
with population arrival phenology or an inter-species temporal niche gap.
"""
from __future__ import annotations
import argparse,collections,csv,datetime,hashlib,io,json,math,statistics,zipfile
from pathlib import Path

SOURCE_DOI="10.5285/64a8291f-8c23-4e5d-9085-c36c8d83b09a"
CSV_SHA256="b8fd11b8ad1d34b2ff85838cbacac746d516efd51418df5b0fe183d1303ab239"
YEARS=(1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2011,2015,2016,2017,2018)
def median_weighted(entries):
 arr=sorted((d,w) for d,w in entries if w>0)
 if not arr:return None
 total=sum(v for _,v in arr)
 now=0.
 for d,w in arr:
  now+=w
  if now>=total/2:return d
 return arr[-1][0]
def csvwrite(p,rows):
 if not rows:raise ValueError("No output rows")
 with Path(p).open("w",encoding="utf8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def run(original,out):
 original=Path(original)
 with zipfile.ZipFile(original) as z:
  files=[x for x in z.namelist() if x.lower().endswith(".csv")]
  if len(files)!=1:raise ValueError("Original one-CSV archive expectation drift")
  raw=z.read(files[0])
 if hashlib.sha256(raw).hexdigest()!=CSV_SHA256:raise ValueError("Original BAS arrival CSV SHA256 changed")
 with io.StringIO(raw.decode("utf-8-sig")) as h:
  rows=list(csv.DictReader(h))
 if len(rows)!=168 or list(rows[0])!=["DATE","NO_BIRDS","COMMENTS"]:
  raise ValueError("168-row source schema changed")
 grouped=collections.defaultdict(list);audit=collections.Counter()
 for i,row in enumerate(rows):
  try:
   date=datetime.date.fromisoformat(row["DATE"])
   v=float(row["NO_BIRDS"])
  except (ValueError,TypeError) as e:
   raise ValueError("Unexpected original dated count at "+str(i)) from e
  if not math.isfinite(v) or v<0 or not v.is_integer():
   raise ValueError("Invalid original count value at "+str(i))
  if date.year not in YEARS:raise ValueError("New source calendar year")
  grouped[date.year].append((date,int(v),str(row["COMMENTS"] or "").strip()))
 if tuple(sorted(grouped))!=YEARS:raise ValueError("Year support changed")
 result=[]
 for year,samples in sorted(grouped.items()):
  samples.sort()
  dates=[x[0] for x in samples]
  counts=[x[1] for x in samples]
  if len(dates)!=len(set(dates)):raise ValueError("Two surveys with same calendar day, require field-level audit")
  first,last=dates[0],dates[-1]
  pos=[(d,c) for d,c,_ in samples if c>0]
  weighted=median_weighted(pos)
  sumcount=sum(counts)
  gap=[(b-a).days for a,b in zip(dates,dates[1:])]
  result.append(dict(year=year,n_survey_dates=len(dates),first_date=first.isoformat(),
   last_date=last.isoformat(),first_survey_doy=first.timetuple().tm_yday,
   last_survey_doy=last.timetuple().tm_yday,span_calendar_days=(last-first).days,
   sum_reported_count=sumcount,number_zero_count_dates=sum(c==0 for c in counts),
   median_bird_count_per_session=statistics.median(counts),
   mean_bird_count_per_session=statistics.mean(counts),
   weighted_median_observed_count_date=weighted.isoformat() if weighted else "",
   weighted_median_observed_count_doy=weighted.timetuple().tm_yday if weighted else None,
   weighted_median_minus_first_survey_days=(weighted-first).days if weighted else None,
   max_observed_session_gap_days=max(gap) if gap else 0,
   median_observed_session_gap_days=statistics.median(gap) if gap else None,
   n_nonempty_comments=sum(bool(s) and s.lower() not in ("na","n/a") for _,_,s in samples),
   count_series_is_incomplete_and_left_censored=True))
 n3=sum(x["n_survey_dates"]>=3 for x in result)
 n4=sum(x["n_survey_dates"]>=4 for x in result)
 n5=sum(x["n_survey_dates"]>=5 for x in result)
 support=dict(source_doi=SOURCE_DOI,source_inner_csv_sha256=CSV_SHA256,
  years=list(YEARS),n_original_count_rows=len(rows),n_calendar_years=len(result),
  n_years_at_least_3_surveys=n3,n_years_at_least_4_surveys=n4,n_years_at_least_5_surveys=n5,
  survey_start_doy_range=[min(x["first_survey_doy"] for x in result),max(x["first_survey_doy"] for x in result)],
  session_count_range=[min(x["n_survey_dates"] for x in result),max(x["n_survey_dates"] for x in result)],
  survey_span_days_range=[min(x["span_calendar_days"] for x in result),max(x["span_calendar_days"] for x in result)],
  median_positive_count_date_is_observation_window_conditional=True,
  no_true_arrival_phenology_inference=True,
  no_adelie_arrival_time_measurement=True,
  station_arrival_and_selection_bias_uncontrolled=True,
  notes=["This publisher dataset has 17 actual calendar years, not uninterrupted 1996-2020 source-year coverage",
    "Counts measure birds sampled at survey times and cannot directly recover unsampled arrivals",
    "Repeated sessions within a year are NOT separate environmental years",
    "Median of observed counts is conditional on date coverage and station arrival",
    "Do not model it as two-species phenology, breeding date, or settlement gap",
    "The field survey start date and maximum gap are preserved to diagnose observation-window bias"])
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 csvwrite(out/"original_arrival_count_year_effort.csv",result)
 (out/"summary.json").write_text(json.dumps(support,indent=2,ensure_ascii=False)+"\n")
 print(json.dumps(support,ensure_ascii=False,indent=2))
 return support
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--original-zip",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True);a=p.parse_args()
 run(a.original_zip,a.out)
