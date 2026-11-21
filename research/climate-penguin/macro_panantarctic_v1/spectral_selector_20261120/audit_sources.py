"""Response-blind exact-acquisition C2 L2 availability audit (no isotope input)."""
import argparse
import hashlib
import json
import re
import time
from pathlib import Path
import pandas as pd
import requests

URL = 'https://earth-search.aws.element84.com/v1/search'
PAT = re.compile(r'LE07_L1(?:GT|TP|GS)_(\d{6})_(\d{8})_\d{8}_(02)_(T[12])')

def candidates(product):
    match = PAT.fullmatch(product)
    if not match:
        raise ValueError(product)
    pathrow, date, collection, tier = match.groups()
    return [f'LE07_{level}_{pathrow}_{date}_{collection}_{tier}' for level in ('L2SR','L2SP')]

def main(out):
    d = pd.read_csv(out/'source_positive_records.csv')
    products = sorted(d['Landsat.Product.Identifier.L1'].unique())
    expected = {p:candidates(p) for p in products}
    ids = sorted({i for values in expected.values() for i in values})
    cache = out/'metadata_cache'; cache.mkdir(exist_ok=True)
    items = {}
    for start in range(0,len(ids),80):
        batch = ids[start:start+80]
        key = hashlib.sha256(json.dumps(batch).encode()).hexdigest()[:16]
        dest = cache/f'{key}.json'
        if dest.exists():
            found = json.loads(dest.read_text())
        else:
            body = {'collections':['landsat-c2-l2'],'ids':batch,'limit':100}
            found = []
            url = URL
            while True:
                for attempt in range(4):
                    try:
                        r = requests.post(url,json=body,timeout=50);r.raise_for_status()
                        result = r.json();break
                    except (requests.RequestException,ValueError):
                        if attempt==3:raise
                        time.sleep(2**attempt)
                found.extend(result['features'])
                nxt = next((x for x in result.get('links',[]) if x['rel']=='next'),None)
                if nxt is None:break
                if nxt.get('method')!='POST':raise ValueError('Unexpected pagination')
                url,body = nxt['href'],nxt['body']
            if any(x['id'] not in batch for x in found):raise ValueError('Unrequested item')
            dest.write_text(json.dumps(found),encoding='utf-8',newline='\n')
        for x in found:items[x['id']]=x
        print(f'{min(start+80,len(ids))}/{len(ids)} candidate IDs; {len(items)} items',flush=True)
    records=[]
    for p, alternatives in expected.items():
        hits=[items[i] for i in alternatives if i in items]
        ok=len(hits)==1
        assets=hits[0]['assets'] if ok else {}
        required={'blue','green','red','nir08','swir16','swir22','qa_pixel','qa_radsat'}
        records.append({'original_product':p,'n_l2_matches':len(hits),
          'scene_id':hits[0]['id'] if ok else '',
          'required_assets_present':ok and required.issubset(assets),
          'status':'UNIQUE_L2_METADATA' if ok and required.issubset(assets) else 'NO_UNIQUE_COMPLETE_L2_METADATA'})
    matches=pd.DataFrame(records)
    matches.to_csv(out/'scene_matches.csv',index=False,lineterminator='\n')
    merged=d.merge(matches,left_on='Landsat.Product.Identifier.L1',right_on='original_product',validate='many_to_one')
    support=[]
    for stage, subset in [('source',merged),('unique_complete_l2_metadata',merged[merged.status.eq('UNIQUE_L2_METADATA')])]:
        for phase,s in subset.groupby('phase'):
            support.append(dict(stage=stage,phase=phase,positive_rows=len(s),sites=s.site_id.nunique(),
              regions=s.region.nunique(),seasons=s.season.nunique(),scenes=s.original_product.nunique(),
              minimum_season=int(s.season.min()),maximum_season=int(s.season.max())))
    pd.DataFrame(support).to_csv(out/'support.csv',index=False,lineterminator='\n')
    merged.groupby(['phase','region','season']).agg(positive_rows=('site_id','size'),sites=('site_id','nunique')).reset_index().to_csv(out/'source_region_season_support.csv',index=False,lineterminator='\n')
    print(pd.DataFrame(support).to_string(index=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path(__file__).parent)
    main(p.parse_args().out)
