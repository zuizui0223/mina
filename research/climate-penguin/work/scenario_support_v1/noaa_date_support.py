"""Nest monitoring start/censoring and explicit lay records, not settlement dates."""
from pathlib import Path
import hashlib,json
import pandas as pd
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/noaa_date_support_v1'
attendance=pd.read_excel(OUT/'attendance.xlsx',sheet_name='DATA')
repro=pd.read_excel(OUT/'repro.xlsx',sheet_name='DATA')
keys=['YEAR','ROOKERY','SPP','COLONY','CAMERA','NEST']
for d in [attendance,repro]:
    assert d[keys+['DATE']].notna().all().all()
    for c in ['YEAR','ROOKERY','COLONY','CAMERA']:d[c]=d[c].astype(str)
assert set(attendance.MAXN.dropna().unique())<={0,1,2,4,5}
assert not attendance.duplicated(keys+['DATE']).any()
repro[repro.duplicated(keys+['DATE'],keep=False)].to_csv(OUT/'repro_duplicate_keys.csv',index=False)
rows=[]
for key,g in attendance.groupby(keys):
    g=g.sort_values('DATE');first=g.iloc[0]
    positive=g[g.MAXN.isin([1,2])]
    earliest=positive.DATE.min()
    zeros=g[g.MAXN.eq(0)&g.DATE.lt(earliest)]
    row=dict(zip(keys,key));row.update(first_observation=first.DATE,last_observation=g.DATE.max(),
        observed_days=len(g),missing_attendance=int(g.MAXN.isna().sum()),
        first_value=first.MAXN,positive_at_first_observation=bool(first.MAXN in [1,2]),
        first_recorded_positive=earliest,zero_observed_before_first_positive=bool(len(zeros)),
        first_positive_status=('positive_at_monitoring_start' if first.MAXN in [1,2] else ('zero_before_positive' if len(zeros) else 'unknown_or_other_code_at_start')))
    rows.append(row)
nests=pd.DataFrame(rows)
# Only explicit value 1 is interpreted as a confirmation. Value 2 is retained
# separately because it contradicts the README's logical-variable description.
events=repro[repro.LAY.eq(1)][keys+['DATE','LAY','MAXE']].drop_duplicates().copy()
assert not events.duplicated(keys+['DATE']).any()
ambiguous=repro[repro.LAY.notna()&~repro.LAY.isin([0,1])].copy()
lay=events.groupby(keys,as_index=False).agg(first_explicit_lay=('DATE','min'),explicit_lay_rows=('DATE','size'))
nests=nests.merge(lay,on=keys,how='left',validate='one_to_one')
unmatched=lay.merge(nests[keys],on=keys,how='left',indicator=True,validate='one_to_one')
unmatched=unmatched[unmatched['_merge'].eq('left_only')]
unmatched.to_csv(OUT/'lay_nests_without_exact_attendance_match.csv',index=False)
nests.to_csv(OUT/'nest_date_support.csv',index=False)
events.to_csv(OUT/'explicit_lay_events.csv',index=False)
ambiguous.to_csv(OUT/'ambiguous_lay_codes.csv',index=False)
summary=nests.groupby(['YEAR','ROOKERY','SPP'],as_index=False).agg(nest_series=('NEST','size'),
   first_observation=('first_observation','min'),last_observation=('last_observation','max'),
   positive_at_start=('positive_at_first_observation','sum'),zero_before_positive=('zero_observed_before_first_positive','sum'),
   nests_with_explicit_lay=('first_explicit_lay','count'),median_explicit_lay=('first_explicit_lay','median'))
summary.to_csv(OUT/'site_species_season_support.csv',index=False)
assert summary.nest_series.sum()==len(nests)
assert nests.explicit_lay_rows.fillna(0).sum()+unmatched.explicit_lay_rows.sum()==len(events)
receipt={'passed':True,'source':'https://www.ncei.noaa.gov/archive/accession/0171619','version':'1.1',
 'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [OUT/'attendance.xlsx',OUT/'repro.xlsx']},
 'nest_series':len(nests),'site_species_seasons':len(summary),'positive_at_first_observation':int(nests.positive_at_first_observation.sum()),
 'zero_before_first_positive':int(nests.zero_observed_before_first_positive.sum()),'explicit_lay_rows':len(events),
 'nests_with_explicit_lay':int(nests.first_explicit_lay.notna().sum()),'ambiguous_lay_rows':len(ambiguous),
 'lay_nests_without_exact_attendance_match':len(unmatched),'repro_duplicate_key_rows':int(repro.duplicated(keys+['DATE'],keep=False).sum()),
 'earliest_monitoring':str(attendance.DATE.min()),
 'limitations':['nest-level attendance is not colony settlement','first observed positive is left-censored when monitoring starts with attendance',
 'absence of explicit lay confirmation is not failure to lay','LAY=2 conflicts with logical metadata; not recoded to true',
 'independent dates do not establish an offset for the separate Zenodo settlement index']}
(OUT/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2));print(summary[['YEAR','ROOKERY','SPP','nest_series','positive_at_start','nests_with_explicit_lay']].to_string(index=False))
