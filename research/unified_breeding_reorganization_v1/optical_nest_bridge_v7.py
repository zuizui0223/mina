"""Pinned same-season optical/count support and descriptive reweighting, V7.
Usage: python optical_nest_bridge_v7.py ARTIFACT_DIRECTORY RESULT.json
"""
import argparse, hashlib, io, json, math, zipfile
from pathlib import Path
import numpy as np
import pandas as pd

PINS={13669533413:'add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a',14328755565:'dfbbe281e50e7d802c43f69255c02878a4c49c14185804acb7e15048189af205',14539723210:'702ab3eeff9ed953c19a9e696492ba9bf5cddce204d40a9c7d9b1234d98f9f96'}
MASKS='ADAR:124 ANDR:101 ARMS:48 ARTH:124 AVIA:123 BATT:124 BEAG:94 BEAU:125 BERK:92 BIEN:124 BONG:115 BRAS:95 BRAT:127 CHAL:124 CHAP:124 CHUN:124 CMID:80 COCK:94 COTT:124 CSOU:124 CURZ:124 DALR:95 DAVI:124 DENI:124 DEVI:127 DOWN:124 DUKE:124 EDEN:95 EDWI:125 EMPE:123 FORB:124 FRNC:79 GING:126 GNEY:124 HASW:104 HBAY:124 HERO:95 HOLL:124 HOPE:95 INEX:125 JULE:124 KIRB:124 KIRT:62 LAGO:123 LAUF:113 LEWI:120 LONG:127 LSAY:125 MACK:124 MAHE:105 MALL:124 MAWS:126 MBIS:60 MIDG:124 NEIS:112 NORF:125 ODBE:124 PAUL:127 PGEO:124 PHIL:84 PIGE:124 PISL:124 PLAT:94 PMAR:124 POSS:124 PROC:124 RAUE:127 ROOK:126 RRRI:125 SCUL:124 SHEE:60 SHEI:125 SHLY:124 SIMS:111 SVEN:124 TAYH:87 TRYN:127 UFSI:124 VESN:127 VESS:127 VORT:94 WAIT:96 WATT:124 WHTY:124 WOPT:125'
KEY=['site_id','season']
FIELDS={'optical_delta15N_permil':'predicted_d15N_season_day_equal','winter_P100_pp':'P100_pp','summer_SSS':'GLORYS_NovFeb_salinity','summer_SIC_pp':'SIC_pp','image_day_centered':'mean_doy_centered','image_day_sq':'mean_doy_sq'}
def read(root,i,member,pin=None):
    raw=(root/f'github-actions-artifact-{i}.zip').read_bytes();assert hashlib.sha256(raw).hexdigest()==PINS[i]
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        assert z.testzip() is None;b=z.read(member)
    if pin:assert hashlib.sha256(b).hexdigest()==pin
    return pd.read_csv(io.BytesIO(b))
def keys(d):return set(map(tuple,d[KEY].values.tolist()))
def state(a,b):
    n=a.sum();m=b.sum();assert n>0 and m>0
    p=a/n;q=b/m;d=b-a;G=np.maximum(d,0).sum();L=np.maximum(-d,0).sum()
    assert np.isclose(G-L,m-n)
    return dict(N0=int(n),N1=int(m),H0=float(p@p),H1=float(q@q),Neff0=float(1/(p@p)),Neff1=float(1/(q@q)),TV=float(abs(q-p).sum()/2),C=float(2*min(G,L)/(m+n))),p,q
def decomp(a,b,x,y):
    s,p,q=state(a,b);local=float(((p+q)/2)@(y-x));rw=float(((x+y)/2)@(q-p));t=float(q@y-p@x)
    assert abs(t-local-rw)<1e-10
    return dict(early=float(p@x),late=float(q@y),total=t,local=local,reweighting=rw,equal_site_change=float(np.mean(y-x)))
def run(root):
    o=read(root,14328755565,'matched_860_original_isotope_ocean_ice_site_seasons.csv','a5dea7bfcbc15e81ea5b30152bc610c9748d638f21d864a23b21c2e1807a8827')
    w=read(root,14539723210,'source_original_860_site_seasons_true_DEEPAA100km_no_optical_Y.csv','86688fd1f5cf1e069305f3ddf47e50cb1323989eb3c12850cc95ba1c3be89ea7')
    geo=read(root,14539723210,'source_original_88_site_polynya_25km_100km_native_grid_geography.csv','15c97e04d7b3881ec027511ad7562375c9925d287cf71e87934ff88175ec8187').query('radius_km==100')
    n=read(root,13669533413,'source_observed_2456.csv');atlas=read(root,13669533413,'panantarctic_595_site_inventory.csv')
    assert len(o)==len(w)==860 and len(n)==2456 and len(atlas)==595 and len(geo)==88
    expected={(k,2004+i) for kv in MASKS.split() for k,v in [kv.split(':')] for i in range(7) if int(v)&(1<<i)}
    assert len(expected)==439 and len({k for k,y in expected})==85
    assert not o.duplicated(KEY).any() and not w.duplicated(KEY).any() and keys(o)==keys(w)
    z=o.merge(w,on=KEY,validate='one_to_one',suffixes=('','_winter'));assert z.source_region.eq(z.source_region_winter).all()
    z=z[z.season.between(2004,2010)&z.source_is_actual_observed_complete_five_month_winter.eq(True)&z.source_winter_JunOct_months_with_real_marine_denominator.eq(5)].copy();assert keys(z)==expected
    z['P100_pp']=z.direct_DEEPAA_coastal_polynya_fraction*100;z['SIC_pp']=z.author_SIC_150km_NovFeb_center_approx_fraction*100
    assert z[list(FIELDS.values())].notna().all().all()
    assert not n.duplicated(['site_id','species','season']).any();n=n.query("species=='ADPE'").copy()
    j=z.merge(n,on=KEY,validate='one_to_one',suffixes=('','_count'));assert j.source_region.eq(j.source_region_count).all()
    assert j.observed_nest_count.ge(0).all() and (j.observed_nest_count%1==0).all()
    assert j.original_survey_method.notna().all() and (~j.original_survey_method.str.lower().isin(['unknown','na',''])).all()
    j=j.merge(atlas[['site_id','source_region','latitude','longitude','polar_250km_fixed_grid_block']],on='site_id',validate='many_to_one',suffixes=('','_atlas'))
    j=j.merge(geo[['site_id','source_region','colony_lat','colony_lon']],on='site_id',validate='many_to_one',suffixes=('','_geo'))
    assert j.source_region.eq(j.source_region_atlas).all() and j.source_region.eq(j.source_region_geo).all()
    assert np.allclose(j.latitude,j.latitude_atlas,atol=1e-8,rtol=0) and np.allclose(j.longitude,j.longitude_atlas,atol=1e-8,rtol=0)
    rad=np.radians;lat,lon,a,b=map(rad,[j.latitude,j.longitude,j.colony_lat,j.colony_lon]);dist=2*6371.0088*np.arcsin(np.sqrt(np.clip(np.sin((lat-a)/2)**2+np.cos(lat)*np.cos(a)*np.sin((lon-b)/2)**2,0,1)))
    assert dist.le(2).all()
    j['wet_cell']=j.source_wet_grid_y.astype(str)+':'+j.source_wet_grid_x.astype(str)
    annual=[{'season':y,'optical_rows':int((z.season==y).sum()),'matched_rows':len(j[j.season==y]),'regions':j[j.season==y].source_region.nunique(),'blocks':j[j.season==y].polar_250km_fixed_grid_block.nunique()} for y in range(2004,2011)]
    complete=[k for k,q in j.groupby('site_id') if len(q)==7 and q.original_survey_method.nunique()==1]
    result={'status':'EXECUTED_DESCRIPTIVE_SAME_SEASON_BRIDGE','pins':PINS,'optical_rows':len(z),'optical_sites':z.site_id.nunique(),'matched_rows':len(j),'matched_sites':j.site_id.nunique(),'matched_regions':j.source_region.nunique(),'matched_blocks':j.polar_250km_fixed_grid_block.nunique(),'max_coordinate_distance_km':float(dist.max()),'annual_support':annual,'complete_seven_season_sites':complete,'windows':[]}
    for y0,y1 in [(y,y+1) for y in range(2004,2010)]+[(2004,2010)]:
        a=j[j.season==y0];b=j[j.season==y1];v=a.merge(b,on='site_id',suffixes=('0','1'),validate='one_to_one');before=len(v);v=v[v.original_survey_method0.eq(v.original_survey_method1)].sort_values('site_id');assert v.source_region0.eq(v.source_region1).all();r=dict(start=y0,end=y1,sites_before_method=before,sites=len(v),regions=v.source_region0.nunique(),blocks=v.polar_250km_fixed_grid_block0.nunique(),wet_cells=len(set(v.wet_cell0)|set(v.wet_cell1)),site_ids=v.site_id.tolist(),region_names=sorted(v.source_region0.unique()))
        if len(v)<3 or r['regions']<2 or v.observed_nest_count0.sum()<=0 or v.observed_nest_count1.sum()<=0:r['status']='STOP_INSUFFICIENT_SUPPORT'
        else:
            r['status']='DESCRIPTIVE_ACCOUNTING_ONLY';a=v.observed_nest_count0.to_numpy();b=v.observed_nest_count1.to_numpy();r['composition']=state(a,b)[0];r['exposures']={k:decomp(a,b,v[c+'0'].to_numpy(),v[c+'1'].to_numpy()) for k,c in FIELDS.items()};r['leave_region_out']={}
            for reg in r['region_names']:
                q=v[v.source_region0!=reg];a=q.observed_nest_count0.to_numpy();b=q.observed_nest_count1.to_numpy()
                if len(q)>=2 and a.sum()>0 and b.sum()>0:r['leave_region_out'][reg]={k:decomp(a,b,q[c+'0'].to_numpy(),q[c+'1'].to_numpy()) for k,c in FIELDS.items()}
        result['windows'].append(r)
    result['limitations']='Nominal site-season match; raw optical proxy is not actual diet or nutrient flux. No common image/census footprint or date; no calibrated sampling model or causal effect. Sparse overlapping rosters, no regression or generalization.'
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.write_text(json.dumps(run(a.root),indent=2,allow_nan=False)+'\n')
