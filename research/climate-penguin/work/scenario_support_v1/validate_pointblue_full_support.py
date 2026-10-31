"""Byte-line count and complete sampled run checks independent of chunk summary."""
from pathlib import Path
import argparse,io,json
import pandas as pd

p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,required=True);p.add_argument('--probe-cache',type=Path,required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[2]/'outputs';out=root/'pointblue_full_positions_v1'
manifest=json.loads((out/'acquisition_manifest.json').read_text());receipt=json.loads((out/'audit_validation.json').read_text())
linebreaks=0;last=None
for block in manifest['blocks']:
    b=(a.cache/block['file']).read_bytes();linebreaks+=b.count(b'\n');last=b[-1:]
rows=linebreaks-1+(last!=b'\n');assert rows==receipt['rows']
runs=pd.read_csv(out/'run_support.csv.gz');assert runs.all_rows.sum()==rows
assert receipt['revisited_run_groups']==0, 'Sampled complete-run checks require contiguous groups'
probe=json.loads((root/'pointblue_location_probe_v1/manifest.json').read_text());checks=[]
for f in probe['files']:
    if 'start' not in f:continue
    lines=(a.probe_cache/f['cache_file']).read_bytes().splitlines()[1:]
    if f['end']<probe['location_object_bytes']-1:lines=lines[:-1]
    d=pd.read_csv(io.BytesIO(b'\n'.join([','.join(probe['header']).encode()]+lines)))
    groups=list(d.groupby(['bird_fn','season','run'],sort=False))
    for key,g in [groups[1],groups[-2]]:
        r=runs[(runs.bird_fn==key[0])&(runs.season==key[1])&(runs.run==key[2])]
        assert len(r)==1
        t=pd.to_datetime(g.time1,utc=True);late=t.dt.month.isin([9,10]);early=t.dt.month.isin([4,5])
        assert r.all_rows.item()==len(g)
        assert r.late_rows.item()==late.sum() and r.early_rows.item()==early.sum()
        assert pd.Timestamp(r.first_time.item())==t.min() and pd.Timestamp(r.last_time.item())==t.max()
        checks.append(dict(bird_fn=key[0],season=key[1],run=key[2],rows=len(g)))
pd.DataFrame(checks).to_csv(out/'independent_run_checks.csv',index=False)
result=dict(passed=True,all_source_rows_by_newlines=rows,complete_sampled_runs=len(checks),
            scope='Full row count and 10 internal complete-run counts/time bounds; not all-coordinate or biological validation')
(out/'independent_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
