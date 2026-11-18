"""Join public net hauls to breeding seasons. Run with --inputs pointing to climate-penguin/outputs."""
import argparse, hashlib, io, itertools, json
from pathlib import Path
from zipfile import ZipFile
import numpy as np
import pandas as pd
from pyproj import Geod
import requests

def build(root,out):
    out.mkdir(parents=True,exist_ok=True)
    url='https://ramadda.data.bas.ac.uk/repository/entry/show?entryid=8b00a915-94e3-4a04-a903-dd4956346439&output=zip.tree'
    response=requests.get(url,timeout=90);response.raise_for_status()
    with ZipFile(io.BytesIO(response.content)) as wrapper:
        with ZipFile(io.BytesIO(wrapper.read(wrapper.namelist()[0]))) as archive:
            payload=archive.read('krillbase_data.csv')
    hauls=pd.read_csv(io.BytesIO(payload),encoding='cp1252')
    diet=root/'palmer_signy_diet_external_v1'
    obs=pd.read_csv(diet/'annual_pair_comparison.csv')
    hauls['day']=pd.to_datetime(hauls.DATE,format='%d/%m/%Y',errors='coerce')
    hauls['year']=hauls.day.dt.year-1
    raw='NUMBER_OF_KRILL_UNDER_1M2';std='STANDARDISED_KRILL_UNDER_1M2'
    hauls=hauls[hauls.RECORD_TYPE.eq('haul') & hauls.DATE_ACCURACY.isin(['D','M']) & hauls.day.dt.month.isin([1,2]) & hauls[std].ge(0)].copy()
    coord={'Signy':(-60.7309,-45.5863),'Palmer':((-64.8114-64.7708)/2,(-63.7775-64.0919)/2)}
    sources=[]; data=[]; diagnostics=[]
    for region,(lat,lon) in coord.items():
        d=obs[obs.region.eq(region)].copy()
        h=hauls[hauls.year.isin(d.year)].copy()
        h['region']=region;h['km']=Geod(ellps='WGS84').inv(h.LONGITUDE,h.LATITUDE,np.full(len(h),lon),np.full(len(h),lat))[2]/1000
        sources.append(h[h.km<=150][['region','year','STATION','DATE','DATE_ACCURACY','NET_TYPE','LATITUDE','LONGITUDE','km',raw,std,'CAVEATS']])
        for radius in (50,100,150):
            g=h[h.km<=radius].groupby('year')
            o=d.merge(g.agg(hauls=(std,'size'),krill_mean=(std,'mean'),krill_median=(std,'median'),raw_mean=(raw,'mean'),nearest_km=('km','min'),gear_types=('NET_TYPE','nunique')),on='year',how='left')
            o['radius']=radius;o['high65']=o.sic_aug_nov>=65;o['gap_pp']=100*o.distance;o['hauls']=o.hauls.fillna(0).astype(int);data.append(o)
            v=o[o.hauls>0]
            for pred in ['sic_aug_nov','krill_mean','krill_median']:
                if len(v)<3 or v[pred].nunique()<2:continue
                x=v[pred].to_numpy();y=v.gap_pp.to_numpy();r=np.corrcoef(x,y)[0,1]
                perm=np.array([np.corrcoef(x,py)[0,1] for py in itertools.permutations(y)]) if len(x)<=7 else []
                diagnostics.append(dict(region=region,radius=radius,n=len(x),predictor=pred,r=r,p_permutation=np.mean(np.abs(perm)>=abs(r)-1e-12) if len(perm) else np.nan))
    joined=pd.concat(data);joined.to_csv(out/'season_support.csv',index=False)
    pd.concat(sources).to_csv(out/'matching_hauls.csv',index=False);pd.DataFrame(diagnostics).to_csv(out/'associations.csv',index=False)
    high=joined.query('radius==100 and high65');assert set(zip(high.region,high.year))=={('Signy',2006),('Signy',2007),('Palmer',2013)}
    assert len(joined)==45 and not joined.duplicated(['region','radius','year']).any()
    # Same exposure and response window as diet. Historical and future annual SIC
    # are equal-weight across four months, and across the two Palmer proxies.
    env=pd.read_csv(root/'climate_penguin/macro_monthly_seaice_1991_2020.csv')
    cmip=root/'cmip6_projection_v1'; scenario=[]
    for region,sites in [('Signy',['GOPT']),('Palmer',['BISC','LITC'])]:
        base=env[env.site_id.isin(sites)&env.year.between(1995,2014)&env.month.between(8,11)&env.inner_km.eq(0)]
        assert len(base)==80*len(sites) and base.sic_mean.notna().all()
        locs=base.location_id.unique();ref=base.sic_mean.mean()
        d=obs[obs.region.eq(region)];coef=np.polyfit(d.sic_aug_nov,100*d.distance,1)[0]
        for historical in cmip.glob('monthly_*_siconc_historical.csv.gz'):
            def mean(path,lo,hi):
                a=pd.read_csv(path);a=a[a.location_id.isin(locs)&a.year.between(lo,hi)&a.month.between(8,11)]
                assert len(a)==len(locs)*80 and not a.duplicated(['location_id','year','month']).any() and a.value.notna().all()
                return a.value.mean()
            mh=mean(historical,1995,2014)
            for exp in ['ssp245','ssp585']:
                for lo,hi in [(2041,2060),(2081,2100)]:
                    mf=mean(historical.with_name(historical.name.replace('historical',exp)),lo,hi)
                    adjusted=ref+mf-mh;ok=d.sic_aug_nov.min()<=adjusted<=d.sic_aug_nov.max() and d.sic_aug_nov.min()<=ref<=d.sic_aug_nov.max()
                    scenario.append(dict(region=region,model_member=historical.name.split('_siconc')[0][8:],experiment=exp,period=f'{lo}-{hi}',reference=ref,model_historical=mh,delta_sic=mf-mh,adjusted_sic=adjusted,in_domain=ok,conditional_gap_change_pp=coef*(mf-mh) if ok else np.nan))
    pd.DataFrame(scenario).to_csv(out/'climate_sensitivity.csv',index=False)
    (out/'source.json').write_text(json.dumps(dict(url=url,data_sha256=hashlib.sha256(payload).hexdigest(),n_source_rows=len(pd.read_csv(io.BytesIO(payload),encoding='cp1252')),diet_sha256=hashlib.sha256((diet/'annual_pair_comparison.csv').read_bytes()).hexdigest()),indent=2))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--inputs',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);a=parser.parse_args();build(a.inputs,a.out)
