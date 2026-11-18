"""Audit published arrival candidates and, when available, location end gaps."""
from pathlib import Path
import argparse,hashlib,json
import pandas as pd

p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);a=p.parse_args()
out=Path(__file__).resolve().parents[2]/'outputs/pointblue_full_positions_v1'
d=pd.read_csv(a.source);assert len(d)==208 and not d.duplicated(['bird_fn','season']).any()
for c in ['arrived','retrieve_date','deploy_date']:d[c]=pd.to_datetime(d[c],errors='raise',utc=True)
d['calendar_year']=d.arrived.dt.year;d['available']=d.arrived.notna()
d['lag_calculated']=(d.retrieve_date-d.arrived).dt.total_seconds()/86400
finite=d[['lag_calculated','retr_lag']].notna().all(axis=1)
assert d.loc[finite,'lag_calculated'].eq(d.loc[finite,'retr_lag']).all()
summary=d.groupby(['br_col','season']).agg(rows=('bird_fn','size'),arrival_values=('available','sum'),
    unique_birds=('bird_fn','nunique'),earliest_candidate=('arrived','min'),latest_candidate=('arrived','max')).reset_index()
summary.to_csv(out/'arrival_support.csv',index=False)
result=dict(rows=len(d),arrival_values=int(d.available.sum()),missing_arrivals=int((~d.available).sum()),
            finite_retrieval_lags_checked=int(finite.sum()),
            negative_retrieval_lags=int(d.lag_calculated.lt(0).sum()),
            arrival_year_not_season_plus_one=int((d.available & d.calendar_year.ne(d.season+1)).sum()),
            colony_seasons_with_arrivals=int(summary.arrival_values.gt(0).sum()),
            arrival_at_retrieval=int(d.lag_calculated.eq(0).sum()),
            source_sha256=hashlib.sha256(a.source.read_bytes()).hexdigest(),
            limitations=['Published candidate dates, not confirmed independent field observations',
                        'Six colony-seasons at most; rows cannot supply 169 independent regional environment contrasts',
                        'Arrival has date-only resolution; gaps use calendar dates with position timestamps expressed in UTC, not elapsed travel time'])
tripfile=out/'trip_support.csv'
if tripfile.exists():
    t=pd.read_csv(tripfile);t=t[t.reference_match.ne('right_only')].copy()
    j=d.merge(t[['bird_fn','season','first_time','last_time','runs','late_selected_rows']],on=['bird_fn','season'],how='outer',validate='one_to_one',indicator=True)
    result['table_key_matches']={str(k):int(v) for k,v in j['_merge'].value_counts().items()}
    j['last_time']=pd.to_datetime(j.last_time,utc=True)
    j['calendar_days_after_last_position']=(j.arrived.dt.normalize()-j.last_time.dt.normalize()).dt.days
    j[['bird_fn','season','br_col','_merge','runs','late_selected_rows','calendar_days_after_last_position']].to_csv(out/'arrival_position_gaps.csv',index=False)
    values=j.calendar_days_after_last_position.dropna()
    result.update(paired_arrival_last_position=len(values),median_days_after_last_position=float(values.median()),
                  arrivals_more_than_seven_days_after_last_position=int(values.gt(7).sum()))
    result['trip_support_sha256']=hashlib.sha256(tripfile.read_bytes()).hexdigest()
(out/'arrival_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));print(summary.to_string(index=False))
