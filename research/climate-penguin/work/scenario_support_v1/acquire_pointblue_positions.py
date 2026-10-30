"""Resume bounded public HTTP ranges, validating every block before reuse."""
from pathlib import Path
import argparse, concurrent.futures, hashlib, json, shutil, time, threading
from datetime import datetime, timezone
import requests

parser=argparse.ArgumentParser();parser.add_argument('--cache',type=Path,required=True);args=parser.parse_args()
cache=args.cache.resolve();cache.mkdir(parents=True,exist_ok=True)
out=Path(__file__).resolve().parents[2]/'outputs/pointblue_full_positions_v1';out.mkdir(exist_ok=True)
api='https://xa1dj38zu1.execute-api.us-east-2.amazonaws.com/'
key='AllData/Schmidt_etal_2023_PNAS/data/gdr_locs_final_500_all_yr_v2021-06-03.csv'
listing=requests.get(api,params={'path':key.rsplit('/',1)[0]+'/'},timeout=30);listing.raise_for_status()
url=next(f['url'] for f in listing.json()['files'] if f['key']==key)
url_created=time.monotonic();url_lock=threading.Lock()
def current_url():
    global url,url_created
    with url_lock:
        # Official browser URLs expire after 300 seconds; refresh before expiry.
        if time.monotonic()-url_created>180:
            fresh=requests.get(api,params={'path':key.rsplit('/',1)[0]+'/'},timeout=30);fresh.raise_for_status()
            url=next(f['url'] for f in fresh.json()['files'] if f['key']==key)
            url_created=time.monotonic()
        return url
r=requests.get(url,headers={'Range':'bytes=0-4095'},timeout=30)
assert r.status_code==206
size=int(r.headers['Content-Range'].split('/')[-1]);etag=r.headers['ETag']
assert size==4900817011 and etag=='"e17b3e77e266cb16dc4ae286179652fa-585"'
blocksize=32*1024*1024
assert shutil.disk_usage(cache).free>size+1024**3, 'Insufficient free workspace storage'
starttime=time.monotonic()

def fetch(start):
    end=min(start+blocksize-1,size-1);name=f'{start:012d}-{end:012d}.bin'
    target=cache/name;receipt=cache/(name+'.json')
    if target.exists() and receipt.exists():
        saved=json.loads(receipt.read_text())
        if saved['etag']==etag and target.stat().st_size==end-start+1 and hashlib.sha256(target.read_bytes()).hexdigest()==saved['sha256']:
            return saved
    for attempt in range(3):
        try:
            response=requests.get(current_url(),headers={'Range':f'bytes={start}-{end}'},timeout=(30,60),stream=True)
            assert response.status_code==206, f'HTTP {response.status_code}'
            assert response.headers.get('ETag')==etag
            assert response.headers['Content-Range']==f'bytes {start}-{end}/{size}'
            temp=cache/(name+'.pending');h=hashlib.sha256();count=0
            with temp.open('wb') as f:
                for chunk in response.iter_content(1024*1024):
                    count+=len(chunk);assert count<=end-start+1;h.update(chunk);f.write(chunk)
            response.close();assert count==end-start+1
            temp.replace(target)
            saved=dict(key=key,file=name,start=start,end=end,bytes=count,etag=etag,sha256=h.hexdigest())
            receipt.write_text(json.dumps(saved,indent=2)+'\n');return saved
        except Exception as exc:
            if attempt==2: raise RuntimeError(f'Range {start}-{end} failed: {type(exc).__name__}') from None
    raise AssertionError('unreachable')

results=[];failures=[];starts=list(range(0,size,blocksize))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
    futures={ex.submit(fetch,start):start for start in starts}
    for future in concurrent.futures.as_completed(futures):
        try:results.append(future.result())
        except Exception as exc: failures.append(dict(start=futures[future],error=str(exc)))
        progress=dict(completed_blocks=len(results),total_blocks=len(starts),bytes_verified=sum(x['bytes'] for x in results),
                      object_bytes=size,failed_blocks=len(failures),elapsed_seconds=round(time.monotonic()-starttime,1))
        (out/'progress.json').write_text(json.dumps(progress,indent=2)+'\n')
        if len(results)%8==0:print(json.dumps(progress),flush=True)
results.sort(key=lambda x:x['start'])
manifest=dict(status='complete' if not failures and len(results)==len(starts) else 'incomplete',
              key=key,etag=etag,object_bytes=size,blocks=results,failures=failures,
              accessed_utc=datetime.now(timezone.utc).isoformat(),signed_urls_saved=False,
              source_data_redistributed=False)
if manifest['status']=='complete':
    assert results[0]['start']==0 and results[-1]['end']==size-1
    assert all(b['start']==a['end']+1 for a,b in zip(results,results[1:]))
    assert sum(x['bytes'] for x in results)==size
(out/'acquisition_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'status':manifest['status'],**progress}),flush=True)
if failures:raise SystemExit(1)
