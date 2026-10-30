"""Stream all range blocks and summarize ensemble support without pseudo-replication."""
from pathlib import Path
import argparse,hashlib,io,json,time
import numpy as np
import pandas as pd

class Blocks(io.RawIOBase):
    def __init__(self, paths):self.paths=iter(paths);self.current=None
    def readable(self):return True
    def readinto(self, buffer):
        view=memoryview(buffer);filled=0
        while filled<len(view):
            if self.current is None:
                try:self.current=next(self.paths).open('rb')
                except StopIteration:break
            n=self.current.readinto(view[filled:])
            if n:filled+=n
            else:self.current.close();self.current=None
        return filled
    def close(self):
        if self.current:self.current.close()
        super().close()

p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,required=True);p.add_argument('--deployment',type=Path,required=True);p.add_argument('--reference',type=Path,required=True);args=p.parse_args()
out=Path(__file__).resolve().parents[2]/'outputs/pointblue_full_positions_v1'
manifest=json.loads((out/'acquisition_manifest.json').read_text());assert manifest['status']=='complete'
blocks=manifest['blocks'];assert sum(b['bytes'] for b in blocks)==manifest['object_bytes']
for b in blocks:
    path=args.cache/b['file'];assert path.stat().st_size==b['bytes']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==b['sha256']
print('All block hashes verified',flush=True)
summaries=[];total=bad_geo=bad_interval=duplicate_rows=nonmonotonic=unexpected_year=0
keys=['bird_fn','season','run'];previous_key=None;previous_time=None;previous_end=None;seen_groups=set();revisited=0
start=time.monotonic()
with io.BufferedReader(Blocks([args.cache/b['file'] for b in blocks]),buffer_size=1024*1024) as stream:
    for number,d in enumerate(pd.read_csv(stream,chunksize=250000)):
        t=pd.to_datetime(d.time1,utc=True,errors='raise');end=pd.to_datetime(d.time2,utc=True,errors='raise')
        assert d[['bird_fn','season','run','inserted','filterLand']].notna().all().all()
        assert set(d.inserted.unique()).issubset({True,False}) and set(d.filterLand.unique()).issubset({True,False})
        geo=np.isfinite(d.lon)&np.isfinite(d.lat)&d.lon.between(-180,360)&d.lat.between(-90,90)
        bad_geo+=int((~geo).sum());bad_interval+=int((end<=t).sum());total+=len(d)
        unexpected_year+=int(t.dt.year.ne(d.season+1).sum())
        late=t.dt.month.isin([9,10]);early=t.dt.month.isin([4,5])
        outside=~t.dt.dayofyear.between(229,269)&~t.dt.dayofyear.between(86,109)
        d['all_rows']=1;d['early_rows']=early.astype(int);d['late_rows']=late.astype(int)
        # Diagnostic masks, not a validated position-quality rule.
        d['late_noninserted']= (late & ~d.inserted).astype(int)
        d['late_outside_equinox_noninserted']=(late & outside & ~d.inserted & geo & (end>t)).astype(int)
        d['late_filterLand_true']=(late & d.filterLand).astype(int)
        d['inserted_rows']=d.inserted.astype(int);d['filterLand_true_rows']=d.filterLand.astype(int)
        d['first_time']=t;d['last_time']=t
        duplicate_rows+=int(d.duplicated(keys+['time1','time2']).sum())
        same=d[keys].eq(d[keys].shift()).all(axis=1)
        nonmonotonic+=int((same & (t<t.shift())).sum())
        first=tuple(d.iloc[0][keys]);last=tuple(d.iloc[-1][keys])
        if previous_key==first:
            nonmonotonic+=int(t.iloc[0]<previous_time)
            duplicate_rows+=int(t.iloc[0]==previous_time and end.iloc[0]==previous_end)
        transitions=d.loc[~same,keys]
        for pos,key in enumerate(transitions.itertuples(index=False,name=None)):
            if pos==0 and key==previous_key:continue
            if key in seen_groups:revisited+=1
            seen_groups.add(key)
        previous_key=last;previous_time=t.iloc[-1];previous_end=end.iloc[-1]
        counts=['all_rows','early_rows','late_rows','late_noninserted','late_outside_equinox_noninserted','late_filterLand_true','inserted_rows','filterLand_true_rows']
        agg={c:'sum' for c in counts};agg.update(first_time='min',last_time='max')
        summaries.append(d.groupby(keys).agg(agg).reset_index())
        if number%10==0:
            progress=dict(chunks=number+1,rows=total,elapsed_seconds=round(time.monotonic()-start,1))
            (out/'audit_progress.json').write_text(json.dumps(progress,indent=2)+'\n');print(json.dumps(progress),flush=True)
runs=pd.concat(summaries).groupby(keys).agg(agg).reset_index()
runs.to_csv(out/'run_support.csv.gz',index=False)
trip=runs.groupby(['bird_fn','season']).agg(runs=('run','nunique'),minimum_run=('run','min'),maximum_run=('run','max'),
    ensemble_rows=('all_rows','sum'),early_ensemble_rows=('early_rows','sum'),late_ensemble_rows=('late_rows','sum'),
    late_noninserted_rows=('late_noninserted','sum'),late_selected_rows=('late_outside_equinox_noninserted','sum'),
    first_time=('first_time','min'),last_time=('last_time','max')).reset_index()
support=runs.assign(has_late=runs.late_rows.gt(0),has_selected_late=runs.late_outside_equinox_noninserted.gt(0)).groupby(['bird_fn','season'])[['has_late','has_selected_late']].sum().reset_index()
trip=trip.merge(support,on=['bird_fn','season'],validate='one_to_one')
dep=pd.read_csv(args.deployment);dep=dep[dep.bird_fn.notna()].copy()
assert not dep.duplicated(['bird_fn','season']).any(), 'Ambiguous deployment identity'
trip=trip.merge(dep[['bird_fn','season','br_col','data']],on=['bird_fn','season'],how='left',validate='one_to_one',indicator='deployment_match')
trip['year.f']=trip.season+1
reference=pd.read_csv(args.reference)[['bird_fn','year.f']].drop_duplicates().assign(in_published_reference=True)
trip=trip.merge(reference,on=['bird_fn','year.f'],how='outer',validate='one_to_one',indicator='reference_match')
trip.to_csv(out/'trip_support.csv',index=False)
trip.groupby(['season','br_col']).agg(trips=('bird_fn','size'),late=('late_ensemble_rows',lambda x:int((x>0).sum())),
    selected_late=('late_selected_rows',lambda x:int((x>0).sum()))).reset_index().to_csv(out/'colony_season_support.csv',index=False)
result=dict(status='full_file_support_audited_not_route_validation',object_bytes=manifest['object_bytes'],rows=total,
    location_bird_years=len(runs[['bird_fn','season']].drop_duplicates()),location_birds=runs.bird_fn.nunique(),
    run_groups=len(runs),invalid_geographic_rows=bad_geo,nonpositive_interval_rows=bad_interval,
    time1_year_not_season_plus_one=unexpected_year,
    within_chunk_or_adjacent_duplicate_keys=duplicate_rows,nonmonotonic_within_group_transitions=nonmonotonic,
    revisited_run_groups=revisited,source_rows_are_ensemble_samples=True,
    raw_data_redistributed=False,elapsed_seconds=round(time.monotonic()-start,1),
    reference_sha256=hashlib.sha256(args.reference.read_bytes()).hexdigest(),deployment_sha256=hashlib.sha256(args.deployment.read_bytes()).hexdigest(),
    limits=['No independent biological observations implied by ensemble row counts',
            'Duplicates counted within chunks and at adjacent boundaries; nonlocal cross-chunk duplicates not exhaustively searched',
            'filterLand is a median-path land-intersection flag per separate source-code audit; counted, not automatically excluded',
            'Equinox/inserted masks are support diagnostics, not validated return or quality classification'])
(out/'audit_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
