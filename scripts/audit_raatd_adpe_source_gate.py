#!/usr/bin/env python3
"""Inspect published RAATD filtered data for seasonal Adélie tracking support.
This is a *source gate*, not an ecological hypothesis test or model fit.
"""
from __future__ import annotations
import argparse, collections, hashlib, io, json, re, zipfile
from pathlib import Path
import pandas as pd
EXPECTED_MD5='168e5b9b5c4ed20bb84dd00145acb0a5'
def digest(p):
    h=hashlib.md5()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(4<<20),b''): h.update(c)
    return h.hexdigest()
def choose_time(df):
    names=list(df.columns)
    options=sorted([c for c in names if re.search(r'date|timestamp|datetime|^time$|datetime|dtime',c,re.I)],
                   key=lambda c:(0 if c.lower() in {'date','datetime','timestamp','date_time','date_utc'} else 1,c))
    tests=[]
    for c in options:
        try:
            s=pd.to_datetime(df[c],errors='coerce',utc=True)
            fraction=float(s.notna().mean())
            good=s.dropna()
            yr=float(((good.dt.year>=1985)&(good.dt.year<=2026)).mean()) if len(good) else 0
            tests.append(dict(column=c,parse_fraction=fraction,range_year_fraction=yr,examples=[str(x) for x in df[c].dropna().head(2)]))
            if fraction>=.80 and yr>=.99:return c,s,tests
        except Exception as e:tests.append(dict(column=c,error=str(e)[:150]))
    return None,None,tests
def main(archive,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    actual=digest(archive)
    if actual!=EXPECTED_MD5:raise ValueError(f'STOP: RAATD md5 mismatch {actual}')
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise ValueError('STOP: ZIP CRC invalid')
        names=z.namelist()
        candidates=[n for n in names if n.lower().endswith('.csv') and re.search(r'adpe|adelie|ad.lie',n,re.I)]
        if not candidates:raise ValueError('STOP: no ADPE CSV found; see archive listing')
        if len(candidates)!=1:raise ValueError(f'STOP: ambiguous multiple ADPE CSVs: {candidates}')
        file=candidates[0]
        df=pd.read_csv(z.open(file),low_memory=False)
        dtcol,dt,checks=choose_time(df)
        report={
            'data_source':'https://zenodo.org/records/3722948',
            'original_zip':'SCAR_EGBAMM_RAATD-filtered-noTMB.zip',
            'validated_md5':actual,'archive_total_members':len(names),
            'source_csv':file, 'raw_positions_count':len(df),
            'raw_columns':df.columns.tolist(),
            'time_parse_candidates':checks,
            'first_two_rows_preview':df.head(2).where(df.head(2).notna(),None).astype(str).to_dict(orient='records'),
            'id_like_columns':[c for c in df if re.search(r'id|tag|bird|deploy|track|site|study|colony',c,re.I)],
            'month_2004_2010':[],
            'season_2004_2010':[],
            'cautions':['Filtered locations include state-space interpolation; neither fixes nor 520 animals are independent colony-years',
                        'Actual winter track positions are required to compare with contemporaneous winter polynya maps',
                        'Summer tracks cannot be presented as inside June–October winter polynyas',
                        'Check colony coordinates/metadata and repeated deployment identity before ecological hypothesis freezing']
        }
        if dtcol is not None:
            ds=df.assign(_track_time=dt)
            good=ds.loc[ds._track_time.notna()].copy()
            good['_year']=good._track_time.dt.year.astype(int)
            good['_month']=good._track_time.dt.month.astype(int)
            report['time_column']=dtcol
            report['time_coverage']={'first':good._track_time.min().isoformat(),'last':good._track_time.max().isoformat()}
            m=good.groupby(['_year','_month']).size().rename('n_fixes').reset_index()
            m.columns=['year','month','n_fixes']
            m.to_csv(out/'adpe_all_year_month_fix_counts.csv',index=False)
            report['month_2004_2010']=m.loc[m.year.between(2004,2010)].to_dict(orient='records')
            good['_winter_year']=good['_year']
            good['_breeding_season_start']=good['_year'].where(good['_month']>=11,good['_year']-1)
            def seasonal(which,dates):
                ss=good.loc[dates & good._winter_year.between(2004,2010)].copy()
                return {'label':which,'n_filtered_fixes':len(ss),
                        'n_calendar_years':int(ss._winter_year.nunique()),
                        'calendar_years':ss._winter_year.value_counts().sort_index().to_dict()}
            report['season_2004_2010']=[
                seasonal('concurrent Jun-Oct winter track fixes',good._month.between(6,10)),
                {'label':'following Nov-Feb breeder track fixes','n_filtered_fixes':int(good.loc[
                        good._breeding_season_start.between(2004,2010) &
                        good._month.isin([11,12,1,2])].shape[0]),
                'n_breeding_seasons':int(good.loc[good._breeding_season_start.between(2004,2010)&
                    good._month.isin([11,12,1,2]),'_breeding_season_start'].nunique())}
            ]
            common=['individual_id','id','animal_id','deployment_id','deploy_id','track_id','tag_id','id_individual','id_track']
            col=next((c for c in common if c in df.columns),None)
            if col:
                report['tracking_id_column_candidate']=col
                report['distinct_values_in_ID_candidate']=int(good[col].nunique(dropna=True))
                report['distinct_values_in_candidate_by_winter_and_summer']={
                    'Jun-Oct2004-2010':int(good.loc[good._year.between(2004,2010)&good._month.between(6,10),col].nunique()),
                    'Nov-Feb2004-2010start':int(good.loc[good._breeding_season_start.between(2004,2010)&good._month.isin([11,12,1,2]),col].nunique())}
            else:report['tracking_id_column_candidate']=None
            matrix=good.loc[good._year.between(2004,2010)].groupby(['_year','_month']).size().reset_index(name='n_filtered_fixes')
            matrix.to_csv(out/'adpe_2004_2010_month_fix_counts.csv',index=False)
        else:report['status']='NEEDS_DATE_SCHEMA_REVIEW'
    (out/'raatd_adpe_source_gate.json').write_text(json.dumps(report,indent=2,default=str)+'\n')
    print(json.dumps({'status':'AUDITED_RAATD_CSV','file':file,'rows':len(df),
                      'time':report.get('time_column'),
                      'season_2004_2010':report.get('season_2004_2010')},default=str))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('archive');ap.add_argument('output');a=ap.parse_args()
    main(a.archive,a.output)
