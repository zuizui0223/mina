"""Support-only replay on the fixed 2017–2020 window, no response estimates."""
import csv, hashlib, io, json, sys, zipfile
from collections import Counter, defaultdict
from pathlib import Path
from modern_marine_land_bridge import read, unique, method, Y, SP
V5_PIN='0264797d82bee62df3b14346428abb4a4994ec01224906c3468afbe99a2c56c4'
CSV_PIN='d169c409cf278b137d6df35fbeb9ab3409bdea15f41c39bcaec549a4d4dbca89'
NAMES={'adelie penguin':'ADPE','chinstrap penguin':'CHPE','gentoo penguin':'GEPE'}
def run(root):
    raw=(root/'github-actions-artifact-14934334550.zip').read_bytes();assert hashlib.sha256(raw).hexdigest()==V5_PIN
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        assert z.testzip() is None
        b=z.read('public_source.csv');assert hashlib.sha256(b).hexdigest()==CSV_PIN
    x=list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'))));assert len(x)==5487
    groups=defaultdict(list)
    for r in x:
        if r['count_type']!='nests' or not r['penguin_count'].strip() or r['common_name'] not in NAMES:continue
        n=float(r['penguin_count']);assert n>=0 and n.is_integer()
        groups[(r['site_id'],NAMES[r['common_name']],int(r['season_starting']))].append((int(n),r['vantage'].strip().lower()))
    known={}
    for k,g in groups.items():
        if len(set(g))==1 and g[0][1] not in ('','unknown','na','nan','none','unspecified'):known[k]=g[0]
    assert len(known)==2724
    ranked=defaultdict(Counter)
    for (k,s,y),(n,m) in known.items():ranked[k,s][m]+=1
    chosen={k:sorted(v,key=lambda m:(-v[m],m))[0] for k,v in ranked.items()}
    legacy={k:v for k,v in known.items() if v[1]==chosen[k[:2]]}
    nn=read(root,13669533413,'source_observed_2456.csv')
    original={(r['site_id'],r['species'],int(r['season'])):(int(float(r['observed_nest_count'])),method(r)) for r in nn}
    assert len(legacy)==2456 and legacy==original
    aa=read(root,13669533413,'panantarctic_595_site_inventory.csv');atlas={r['site_id']:r for r in aa}
    hh=read(root,13829236358,'original_588_site_1993_2020_actual_SIC_SSS_SST_PC1.csv');H=unique(hh,['site_id','year'])
    vv=read(root,13829236358,'original_modern_static_positive_terrestrial_marine_colocation.csv');V={r['site_id'] for r in vv}
    pp=read(root,14926710177,'winter_595.csv');P=unique(pp,['site_id','radius_km','season'])
    assert (len(aa),len(hh),len(vv),len(pp))==(595,16464,167,21420)
    def complete(k,y):
        h=H.get((k,str(y)));p=[P.get((k,str(r),str(y))) for r in (100,25)]
        return bool(h and h['original_source_4_GLORYS_months']=='4' and h['original_source_4_OSISAF_months']=='4' and all(t and t['n_valid_months'] in ('5','5.0') and t['direct_DEEPAA_coastal_polynya_fraction']!='' for t in p))
    def summary(keys):return {'sites':keys,'n_sites':len(keys),'regions':dict(Counter(atlas[k]['source_region'] for k in keys)),'blocks250':len({atlas[k]['polar_250km_fixed_grid_block'] for k in keys})}
    out={'status':'V5_METHOD_SUPPORT_ONLY','v5_zip_sha256':V5_PIN,'v5_csv_sha256':CSV_PIN,'legacy_reproduced':len(legacy),'all_known_methods':len(known),'additional_rows':len(known)-len(legacy),'species':{},'pair_support':{}}
    for s in SP:
        out['species'][s]={}
        for label,ys in [('four_year',Y),('endpoint',(Y[0],Y[-1]))]:
            raw=[k for k in sorted(atlas) if all((k,s,y) in known for y in ys)]
            same=[k for k in raw if len({known[k,s,y][1] for y in ys})==1]
            full=[k for k in same if all(complete(k,y) for y in ys)];land=[k for k in full if k in V]
            out['species'][s][label]={'raw_complete_sites':len(raw),'same_known_method_sites':len(same),'physical':summary(full),'physical_and_positive_modern_map':summary(land)}
    for s,t in [('ADPE','CHPE'),('ADPE','GEPE'),('CHPE','GEPE')]:
        q=[(k,y) for k in sorted(atlas) for y in Y if (k,s,y) in known and (k,t,y) in known and known[k,s,y][1]==known[k,t,y][1] and complete(k,y)]
        out['pair_support'][s+'__'+t]={'physical_site_seasons':len(q),'positive_map_site_seasons':sum(k in V for k,y in q),'positive_map_sites':len({k for k,y in q if k in V}),'positive_map_blocks250':len({atlas[k]['polar_250km_fixed_grid_block'] for k,y in q if k in V})}
    out['limits']='Same MAPPPD v5 source, alternative-method support not independent. No response coefficients, no confirmed interaction or plant dynamics.'
    return out
if __name__=='__main__':
    r=run(Path(sys.argv[1]));Path(sys.argv[2]).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
