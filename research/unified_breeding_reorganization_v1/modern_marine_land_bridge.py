"""V6 original-derived common modern roster; no effect estimation."""
import csv, hashlib, io, json, math, sys, zipfile
from collections import Counter, defaultdict
from pathlib import Path
PINS={13669533413:'add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a',13829236358:'64a8e9832e254171139d78bb22351d6c9a3acf490356931b2635ed5b108d94b5',14926710177:'b48ad3c97e35bc487ad6ebca955bbbec5478f75359e9f0300296910821a050b8'}
Y=(2017,2018,2019,2020); SP=('ADPE','CHPE','GEPE'); VAR=('SIC_pp','SSS','SST_C','P100_pp','P25_pp')
def read(root,i,member):
    b=(root/f'github-actions-artifact-{i}.zip').read_bytes();assert hashlib.sha256(b).hexdigest()==PINS[i]
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        assert z.testzip() is None
        return list(csv.DictReader(io.StringIO(z.read(member).decode('utf-8-sig'))))
def unique(rows,keys):
    d={tuple(r[k] for k in keys):r for r in rows};assert len(d)==len(rows);return d
def close(a,b):return abs(float(a)-float(b))<1e-6
def method(r):
    m=r['original_survey_method'].strip().lower()
    return m if m not in ('','unknown','na','nan','none','unspecified') else None
def main(root):
    aa=read(root,13669533413,'panantarctic_595_site_inventory.csv');nn=read(root,13669533413,'source_observed_2456.csv');hh=read(root,13829236358,'original_588_site_1993_2020_actual_SIC_SSS_SST_PC1.csv');vv=read(root,13829236358,'original_modern_static_positive_terrestrial_marine_colocation.csv');pp=read(root,14926710177,'winter_595.csv')
    assert tuple(map(len,(aa,nn,hh,vv,pp)))==(595,2456,16464,167,21420)
    atlas={k[0]:v for k,v in unique(aa,['site_id']).items()};N=unique(nn,['site_id','species','season']);H=unique(hh,['site_id','year']);V={k[0]:v for k,v in unique(vv,['site_id']).items()};P=unique(pp,['site_id','radius_km','season'])
    def validate(r,lat,lon):
        a=atlas[r['site_id']];assert r['source_region']==a['source_region'] and close(r[lat],a['latitude']) and close(r[lon],a['longitude']),r['site_id']
    for r in nn:validate(r,'latitude','longitude')
    for r in hh:validate(r,'latitude','longitude')
    for r in pp:validate(r,'colony_lat','colony_lon')
    for k,v in V.items():
        assert k in atlas and v['source_region']==atlas[k]['source_region'] and float(v['original_mapped_union_terrestrial_area_2km_m2'])>0 and v['original_land_static_source_window']=='2017-2023 composite'
    def count(k,s,y):return N.get((k,s,str(y)))
    def phys(k,y):
        h=H.get((k,str(y)));p=[P.get((k,str(r),str(y))) for r in (100,25)]
        if not h or any(x is None for x in p):return None
        if h['original_source_4_GLORYS_months']!='4' or h['original_source_4_OSISAF_months']!='4' or any(x['n_valid_months'] not in ('5','5.0') for x in p):return None
        z=[float(h[k]) for k in ('mean_source_SIC_pp','mean_GLORYS_salinity','mean_GLORYS_thetao_C')]+[100*float(x['direct_DEEPAA_coastal_polynya_fraction']) for x in p]
        assert all(map(math.isfinite,z)) and all(0<=q<=100 for q in [z[0],z[3],z[4]])
        return dict(zip(VAR,z))
    def support(keys,years):
        return {'n_sites':len(keys),'sites':keys,'regions':dict(Counter(atlas[k]['source_region'] for k in keys)),'blocks250':len({atlas[k]['polar_250km_fixed_grid_block'] for k in keys}),'wet_cells':len({(H[k,str(years[0])]['GLORYS_cell_y'],H[k,str(years[0])]['GLORYS_cell_x']) for k in keys})}
    def calc(keys,s,years,land):
        z=support(keys,years);z['count_rows']=len(keys)*len(years);z['positive_map_sites']=sum(k in V for k in keys)
        if len(keys)<3 or len(z['regions'])<2:
            z['status']='SUPPORT_ONLY';return z
        a={y:[float(count(k,s,y)['observed_nest_count']) for k in keys] for y in years}
        for y,v in a.items():
            assert all(x>=0 and math.isfinite(x) for x in v) and all((x!=0 or count(k,s,y)['observed_zero_is_actual_source_count'].lower()=='true') for k,x in zip(keys,v))
        if any(sum(x)<=0 for x in a.values()):z['status']='ZERO_TOTAL_STOP';return z
        w={y:[x/sum(v) for x in v] for y,v in a.items()};variables=list(VAR)+(['log1p_modern_mapped_area'] if land else [])
        def ex(k,y,j):return math.log1p(float(V[k]['original_mapped_union_terrestrial_area_2km_m2'])) if j=='log1p_modern_mapped_area' else phys(k,y)[j]
        annual={}
        for y in years:
            h=sum(q*q for q in w[y]);annual[str(y)]={'count_sum':sum(a[y]),'H':h,'Neff':1/h,'weighted_context':{j:sum(q*ex(k,y,j) for k,q in zip(keys,w[y])) for j in variables}}
        y0,y1=years[0],years[-1];d=[b-a0 for a0,b in zip(a[y0],a[y1])];g=sum(max(x,0) for x in d);l=sum(max(-x,0) for x in d);assert abs(g-l-(sum(a[y1])-sum(a[y0])))<1e-7
        v0,v1=w[y0],w[y1];tv=.5*sum(abs(b-a0) for a0,b in zip(v0,v1));decomp={}
        for j in variables:
            x0=[ex(k,y0,j) for k in keys];x1=[ex(k,y1,j) for k in keys];local=sum((p+q)/2*(b-a0) for p,q,a0,b in zip(v0,v1,x0,x1));rw=sum((a0+b)/2*(q-p) for p,q,a0,b in zip(v0,v1,x0,x1));total=annual[str(y1)]['weighted_context'][j]-annual[str(y0)]['weighted_context'][j];assert abs(local+rw-total)<1e-9
            decomp[j]={'local':local,'redistribution':rw,'total':total}
        z.update(status='DESCRIPTIVE_ACCOUNTING',annual=annual,deltaH=annual[str(y1)]['H']-annual[str(y0)]['H'],TV=tv,C=2*min(g,l)/(sum(a[y0])+sum(a[y1])),decomposition=decomp);return z
    out={'status':'EXECUTED_MODERN_COMMON_SUPPORT','source_pins':PINS,'source_rows':dict(zip(('atlas','counts','hydro','positive_map','polynya'),map(len,(aa,nn,hh,vv,pp)))),'species':{},'pair_support':{}}
    for s in SP:
        out['species'][s]={}
        for label,ys in [('four_year',Y),('endpoint',(Y[0],Y[-1]))]:
            raw=[k for k in sorted(atlas) if all(count(k,s,y) for y in ys)]
            same=[k for k in raw if None not in (ms:={method(count(k,s,y)) for y in ys}) and len(ms)==1]
            full=[k for k in same if all(phys(k,y) for y in ys)];land=[k for k in full if k in V]
            out['species'][s][label]={'raw_complete_sites':len(raw),'same_known_method_sites':len(same),'physical':calc(full,s,ys,False),'physical_and_positive_modern_map':calc(land,s,ys,True)}
    for s,t in [('ADPE','CHPE'),('ADPE','GEPE'),('CHPE','GEPE')]:
        q=[(k,y) for k in sorted(atlas) for y in Y if count(k,s,y) and count(k,t,y) and method(count(k,s,y)) is not None and method(count(k,s,y))==method(count(k,t,y)) and phys(k,y)]
        def pair_summary(q):return {'site_seasons':len(q),'sites':len({k for k,y in q}),'regions':dict(Counter(atlas[k]['source_region'] for k,y in q)),'blocks250':len({atlas[k]['polar_250km_fixed_grid_block'] for k,y in q})}
        out['pair_support'][s+'__'+t]={'physical':pair_summary(q),'positive_modern_map':pair_summary([(k,y) for k,y in q if k in V])}
    out['limits']='Static positive map context, not vegetation response or actual use. Four-year and endpoint subsets nested; same source reused; no independent geography or ecological coefficient, actual survey dates/footprints may differ, no interaction or forecast.'
    return out
if __name__=='__main__':
    o=main(Path(sys.argv[1]));Path(sys.argv[2]).write_text(json.dumps(o,indent=2)+'\n');print(json.dumps({s:{k:{'raw':v['raw_complete_sites'],'same_method':v['same_known_method_sites'],'physical':{a:b for a,b in v['physical'].items() if a in ('n_sites','regions','blocks250','status','deltaH','TV','C','decomposition')},'land':{a:b for a,b in v['physical_and_positive_modern_map'].items() if a in ('n_sites','regions','blocks250','status','deltaH','TV','C','decomposition')}} for k,v in q.items()} for s,q in o['species'].items()},indent=2));print(json.dumps(o['pair_support'],indent=2))
