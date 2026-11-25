"""Fixed PGEO standalone productivity, no cross-source abundance multiplication."""
import sys,hashlib,zipfile,json,math
from pathlib import Path
import pandas as pd
import numpy as np
PINS={14935924098:'fbeeffce21a8323f8f9afa75986b6d3cc05d7d66053ee872a43a39d7251b0e06',14934334550:'0264797d82bee62df3b14346428abb4a4994ec01224906c3468afbe99a2c56c4',13669533413:'add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a',14926710177:'b48ad3c97e35bc487ad6ebca955bbbec5478f75359e9f0300296910821a050b8',13829236358:'64a8e9832e254171139d78bb22351d6c9a3acf490356931b2635ed5b108d94b5'}
YEARS=list(range(2004,2011))+list(range(2013,2021))
def read(root,i,member):
    p=root/f'github-actions-artifact-{i}.zip';assert hashlib.sha256(p.read_bytes()).hexdigest()==PINS[i]
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        return pd.read_csv(z.open(member))
def model(d,controls):
    Y=d['breeding_success'].to_numpy(float);P=d['P100_pp'].to_numpy(float)
    X=d[controls].to_numpy(float);X-=X.mean(0);sc=X.std(0)
    assert np.all(sc>0)
    B=np.column_stack([np.ones(len(d)),X/sc]);v=P-P.mean();sd=v.std()
    if sd<=0:return {'status':'BLOCKED_P_VARIATION'}
    A=np.column_stack([B,v/sd]);rank=int(np.linalg.matrix_rank(A));cond=float(np.linalg.cond(A));df=len(Y)-rank
    if rank<A.shape[1] or cond>30 or df<5:return {'status':'BLOCKED_RANK_CONDITION_DF','n':len(d),'rank':rank,'condition':cond,'df':df}
    by=np.linalg.lstsq(B,Y,rcond=None)[0];bp=np.linalg.lstsq(B,P,rcond=None)[0];yr=Y-B@by;pr=P-B@bp;beta=float(pr@yr/(pr@pr));r=yr-beta*pr
    full=np.linalg.lstsq(A,Y,rcond=None)[0]
    assert abs(full[-1]/sd-beta)<1e-10
    return {'status':'DESCRIPTIVE','n':len(d),'rank':rank,'condition':cond,'df':df,'beta_per_pp':beta,'partial_R2':float(1-(r@r)/(yr@yr)),'P_residual_sd_pp':float(pr.std()),'beta_per_residual_sd':float(beta*pr.std())}
def run(root):
    b=read(root,14935924098,'985565_v1_global_seabird_breeding_success.csv');a=read(root,14934334550,'public_source.csv');n=read(root,13669533413,'source_observed_2456.csv');p=read(root,14926710177,'winter_595.csv');m=read(root,13829236358,'original_588_site_1993_2020_actual_SIC_SSS_SST_PC1.csv')
    x=b[(b.site=='Pointe Geologie')&(b.ScientificName_accepted=='Pygoscelis adeliae')].copy();assert len(x)==29 and x.year.is_unique and x.breeding_success.notna().all() and x.n.gt(0).all()
    assert x.loc[x.breeding_success.eq(0),'year'].tolist()==[2013,2016]
    y=n[(n.site_id=='PGEO')&(n.species=='ADPE')];assert len(y)==29 and y.season.is_unique
    old=a[(a.site_id=='PGEO')&(a.common_name=='adelie penguin')&(a.count_type=='nests')];assert len(old)==29 and old.reference.str.contains('barbraud2020population').all() and old.vantage.eq('ground photo').all()
    j=x.merge(y,left_on='year',right_on='season',validate='one_to_one');assert len(j)==25
    q=j[j.year.isin(YEARS)];assert len(q)==12
    ratio=q.n/q.observed_nest_count
    p=p[(p.site_id=='PGEO')&(p.radius_km==100)&(p.season.isin(YEARS))].copy();assert len(p)==15 and p.n_valid_months.eq(5).all() and p.direct_DEEPAA_coastal_polynya_fraction.between(0,1).all();p['P100_pp']=100*p.direct_DEEPAA_coastal_polynya_fraction
    m=m[(m.site_id=='PGEO')&(m.year.isin(YEARS))];assert len(m)==15 and m.original_source_4_GLORYS_months.eq(4).all() and m.original_source_4_OSISAF_months.eq(4).all()
    d=x[['year','breeding_success']].merge(p[['season','P100_pp']],left_on='year',right_on='season',validate='one_to_one').merge(m[['year','mean_source_SIC_pp','mean_GLORYS_thetao_C','mean_GLORYS_salinity']],on='year',validate='one_to_one').sort_values('year');assert d.year.tolist()==YEARS and d.notna().all().all()
    controls={'time':['year'],'time_hydro':['year','mean_source_SIC_pp','mean_GLORYS_thetao_C','mean_GLORYS_salinity']};fits={}
    for k,cols in controls.items():
        f=model(d,cols);loo=[dict(omitted=int(yr),**model(d[d.year!=yr],cols)) for yr in YEARS];v=[r['beta_per_pp'] for r in loo if r['status']=='DESCRIPTIVE'];f['loo']=loo;f['loo_beta_range']=[min(v),max(v)] if v else None;f['omit_both_failure_seasons']=model(d[~d.year.isin([2013,2016])],cols);fits[k]=f
    out={'status':'EXPLORATORY_STANDALONE_PRODUCTIVITY_ONLY','pins':PINS,'denominator_audit':{'BCO_rows':len(x),'MAPPPD_selected_rows':len(y),'common_years':len(j),'equal_denominators_all_common':int(j.n.eq(j.observed_nest_count).sum()),'joint_climate_nest_years':q.year.tolist(),'ratio_min_median_max':[float(ratio.min()),float(ratio.median()),float(ratio.max())]},'year_support':YEARS,'observed_zero_success_years':[2013,2016],'P100_raw_range_pp':[float(d.P100_pp.min()),float(d.P100_pp.max())],'fits':fits,'climate_mediation_or_population_forecast':False,'new_independent_event_lineage':False}
    return out
if __name__=='__main__':
    r=run(Path(sys.argv[1]));Path(sys.argv[2]).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({**r,'fits':{k:{a:b for a,b in v.items() if a!='loo'} for k,v in r['fits'].items()}},indent=2))
