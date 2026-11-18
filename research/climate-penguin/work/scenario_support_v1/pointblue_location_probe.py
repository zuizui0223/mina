"""Bounded public range reads; no private API or signed URL persisted."""
from pathlib import Path
import argparse, csv, hashlib, io, json
from datetime import datetime, timezone
import pandas as pd
import requests

parser=argparse.ArgumentParser();parser.add_argument('--cache',type=Path,required=True);args=parser.parse_args()
args.cache.mkdir(parents=True,exist_ok=True)
out=Path(__file__).resolve().parents[2]/'outputs/pointblue_location_probe_v1';out.mkdir(exist_ok=True)
api='https://xa1dj38zu1.execute-api.us-east-2.amazonaws.com/'
records=[];inventory=[];files={}
for prefix in ['AllData/','AllData/Schmidt_etal_2023_PNAS/data/','AllData/Schmidt_etal_2023_PNAS/code/']:
    response=requests.get(api,params={'path':prefix},timeout=30);response.raise_for_status();d=response.json()
    inventory.append(dict(path=prefix,directories=d['directories'],file_keys=[f['key'] for f in d['files']]))
    files.update({f['key']:f['url'] for f in d['files']})
key='AllData/Schmidt_etal_2023_PNAS/data/gdr_locs_final_500_all_yr_v2021-06-03.csv'
url=files[key]
head=requests.get(url,headers={'Range':'bytes=0-4095'},timeout=30)
assert head.status_code==206, 'Server must honor range; do not download whole object'
total=int(head.headers['Content-Range'].split('/')[-1]);etag=head.headers.get('ETag')
header=head.content.splitlines()[0].decode();columns=next(csv.reader([header]))
assert columns==['bird_fn','season','time1','time2','lon','lat','inserted','filterLand','run']
window=1024*1024
samples=[]
for i,start in enumerate([0,total//4,total//2,3*total//4,total-window]):
    end=min(start+window-1,total-1)
    r=requests.get(url,headers={'Range':f'bytes={start}-{end}'},timeout=30)
    assert r.status_code==206 and r.headers.get('ETag')==etag
    assert r.headers['Content-Range']==f'bytes {start}-{end}/{total}' and len(r.content)==end-start+1
    name=f'location_range_{i}.csv.part';(args.cache/name).write_bytes(r.content)
    lines=r.content.splitlines()
    if start==0: lines=lines[1:]
    else: lines=lines[1:]  # discard possibly partial leading record
    if end<total-1:lines=lines[:-1]
    frame=pd.read_csv(io.BytesIO(('\n'.join([header]+[x.decode() for x in lines])).encode()))
    time=pd.to_datetime(frame.time1,utc=True,errors='raise')
    late=frame[time.dt.month.isin([9,10,11])]
    samples.append(dict(sample=i,start=start,end=end,parsed_rows=len(frame),birds=frame.bird_fn.nunique(),
                        first_time=str(time.min()),last_time=str(time.max()),
                        september_november_rows=len(late),september_november_birds=late.bird_fn.nunique(),
                        seasons='|'.join(map(str,sorted(frame.season.unique()))),runs='|'.join(map(str,sorted(frame.run.unique())))))
    records.append(dict(key=key,cache_file=name,bytes=len(r.content),start=start,end=end,sha256=hashlib.sha256(r.content).hexdigest()))
for key in ['AllData/ReadMe.txt','AllData/PointBlue_Data_Sharing_Policy.pdf',
            'AllData/Schmidt_etal_2023_PNAS/data/croz_royds_gdr_depl_all_v2021-08-27.csv',
            'AllData/Schmidt_etal_2023_PNAS/code/README.md',
            'AllData/Schmidt_etal_2023_PNAS/code/create_molt_locs500.R',
            'AllData/Schmidt_etal_2023_PNAS/code/map_all_nonbreed_locs.R']:
    r=requests.get(files[key],stream=True,timeout=30);r.raise_for_status()
    if int(r.headers.get('Content-Length',0))>5*1024*1024: r.close();raise ValueError('Metadata file unexpectedly large')
    payload=b''
    for chunk in r.iter_content(65536):
        payload+=chunk
        if len(payload)>5*1024*1024:r.close();raise ValueError('Metadata cap exceeded')
    name=Path(key).name;(args.cache/name).write_bytes(payload)
    records.append(dict(key=key,cache_file=name,bytes=len(payload),sha256=hashlib.sha256(payload).hexdigest()))
pd.DataFrame(samples).to_csv(out/'range_support.csv',index=False)
(out/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
receipt=dict(accessed_utc=datetime.now(timezone.utc).isoformat(),official_entry='https://data.pointblue.org/apps/penguin_science/',
             directory_api=api,location_object_bytes=total,etag=etag,header=columns,files=records,
             scope='Five byte-range samples only; not complete tracks, unique sample size, or representative coverage',
             signed_urls_saved=False,source_data_redistributed=False)
(out/'manifest.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(pd.DataFrame(samples).to_string(index=False));print('location_object_bytes',total)
