"""Re-read saved byte ranges and audit deployment links; not full-track QC."""
from pathlib import Path
import argparse,hashlib,io,json
import pandas as pd

p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,required=True);p.add_argument('--reference',type=Path,required=True);a=p.parse_args()
out=Path(__file__).resolve().parents[2]/'outputs/pointblue_location_probe_v1'
manifest=json.loads((out/'manifest.json').read_text());rows=[]
for f in manifest['files']:
    b=(a.cache/f['cache_file']).read_bytes()
    assert len(b)==f['bytes'] and hashlib.sha256(b).hexdigest()==f['sha256']
    if 'start' not in f:continue
    lines=b.splitlines()[1:]
    if f['end']<manifest['location_object_bytes']-1:lines=lines[:-1]
    frame=pd.read_csv(io.BytesIO(b'\n'.join([','.join(manifest['header']).encode()]+lines)))
    t=pd.to_datetime(frame.time1,utc=True);late=frame[t.dt.month.isin([9,10,11])].copy()
    for (bird,season),g in late.groupby(['bird_fn','season']):
        dates=pd.to_datetime(g.time1,utc=True)
        use=g[(~dates.dt.dayofyear.between(229,269)) & g.inserted.eq(False)]
        rows.append(dict(sample=f['cache_file'],bird_fn=bird,season=season,rows=len(g),
                         distinct_time_intervals=len(g[['time1','time2']].drop_duplicates()),
                         runs=g.run.nunique(),minimum_latitude=g.lat.min(),maximum_latitude=g.lat.max(),
                         noninserted_rows_outside_published_equinox_exclusion=len(use),
                         distinct_intervals_outside_published_equinox_exclusion=len(use[['time1','time2']].drop_duplicates())))
pd.DataFrame(rows).to_csv(out/'sampled_late_season_support.csv',index=False)
d=pd.read_csv(a.cache/'croz_royds_gdr_depl_all_v2021-08-27.csv');complete=d[d.data.eq('c')].copy()
assert not complete.duplicated(['bird_fn','season']).any()
complete.groupby(['season','br_col']).agg(deployments=('bird_fn','size'),birds=('bird_fn','nunique')).reset_index().to_csv(out/'deployment_support.csv',index=False)
reference=pd.read_csv(a.reference)[['bird_fn','year.f']].drop_duplicates()
complete['year.f']=complete.season+1
j=reference.merge(complete[['bird_fn','year.f','br_col']],on=['bird_fn','year.f'],how='left',indicator=True,validate='one_to_one')
j.to_csv(out/'published_reference_links.csv',index=False)
r=dict(passed=True,cached_files_verified=len(manifest['files']),range_samples=len(rows),
       deployment_rows=len(d),complete_metadata_rows=len(complete),complete_metadata_birds=complete.bird_fn.nunique(),
       published_reference_trips=len(reference),matched_complete_deployments=int(j._merge.eq('both').sum()),
       unmatched_reference_trips=int(j._merge.eq('left_only').sum()),
       reference_sha256=hashlib.sha256(a.reference.read_bytes()).hexdigest(),
       full_position_file_checked=False,source_code_comment_counts_not_assumed=True,
       limits=['Byte samples are not representative or independent observations',
               'Complete flag does not prove available quality-controlled return locations',
               'Same research system overlaps published reference; not independent replication'])
(out/'validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r));print(pd.DataFrame(rows).to_string(index=False))
