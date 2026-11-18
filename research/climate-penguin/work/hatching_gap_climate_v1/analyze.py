"""Source-audited hatching gaps; one-island exploratory inference, not forecasts.

Run with --workspace pointing to the outer mina workspace. Outputs and downloaded
source snapshots stay outside the checkout; no source nests are republished.
"""
from pathlib import Path
import argparse, csv, hashlib, io, json, re, zipfile
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from scipy.stats import linregress
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

SIGNY = 'https://ramadda.data.bas.ac.uk/repository/entry/show?entryid=274b49bd-40a4-4e5d-bd5f-69a1ba09d403&output=zip.tree'
TEMP = 'https://legacy.bas.ac.uk/met/READER/surface/Orcadas.All.temperature.html'
SHA = 'd86d42a581ec8f5bdf123a2073de17469714ce85031914c32b2489afc2187c94'

def run(workspace):
    out=workspace/'outputs/hatching_gap_climate_v1'; source=out/'source'
    source.mkdir(parents=True,exist_ok=True)
    repo=Path(__file__).resolve().parents[4]
    climate=repo/'research/climate-penguin/outputs/climate_penguin/macro_monthly_seaice_1991_2020.csv'
    provenance=[]
    for name,url in [('signy_hatching.zip',SIGNY),('Orcadas.All.temperature.html',TEMP)]:
        path=source/name
        if not path.exists():
            r=requests.get(url,timeout=90);r.raise_for_status();path.write_bytes(r.content)
        provenance.append(dict(file=name,url=url,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    with zipfile.ZipFile(source/'signy_hatching.zip') as z:
        raw=z.read([n for n in z.namelist() if n.endswith('.csv')][0])
    assert hashlib.sha256(raw).hexdigest()==SHA
    rows=list(csv.reader(io.StringIO(raw.decode('utf-8-sig'))))
    start=next(i for i,r in enumerate(rows) if r[:2]==['Season','Species'])
    a=[]
    for r in rows[start+1:]:
        if not any(x.strip() for x in r):continue
        year=int(r[0][:4]);date=pd.to_datetime(r[3],format='%d/%m/%Y')
        a.append(dict(year=year,species='Adelie' if 'Adelie' in r[1] else 'Chinstrap',
                      date=date,source_day=float(r[4]),day=(date-pd.Timestamp(year,10,1)).days))
    long=pd.DataFrame(a);assert len(long)==34
    assert not long.duplicated(['year','species']).any()
    d=long.pivot(index='year',columns='species',values='day').reset_index()
    d['gap']=d.Chinstrap-d.Adelie
    published=long.pivot(index='year',columns='species',values='source_day')
    assert np.array_equal(d.gap,published.Chinstrap-published.Adelie)
    # Calendar arithmetic avoids a one-day source day-index convention in some years.
    long['source_minus_calendar_day']=long.source_day-long.day
    long.to_csv(out/'signy_source_date_audit.csv',index=False,lineterminator="\n")
    source_text=BeautifulSoup((source/'Orcadas.All.temperature.html').read_bytes(),'html.parser').get_text(' ',strip=True)
    coverage_pct={}
    for match in re.finditer(r'\b((?:19|20)\d{2})\b(.*?)(?=\b(?:19|20)\d{2}\b|$)',source_text):
        values=re.findall(r'(-?\d+\.\d+)\s*\(\s*(\d+)\)',match[2])
        if len(values)==12:coverage_pct[int(match[1])]=float(values[9][1])
    text=re.sub(r'\(\s*\d+\)', '',source_text)
    annual={}
    for match in re.finditer(r'\b((?:19|20)\d{2})\b(.*?)(?=\b(?:19|20)\d{2}\b|$)',text):
        year=int(match[1]);tokens=match[2].split()
        if len(tokens)>=12 and all(re.fullmatch(r'-?\d+\.\d+|-',t) for t in tokens[:12]):
            annual[year]=[np.nan if t=='-' else float(t) for t in tokens[:12]]
    assert annual[1996][9]==-1.0 and annual[2003][9]==-1.1
    d['temp_oct']=d.year.map(lambda y:annual[y][9])
    d['temp_oct_source_coverage_pct']=d.year.map(coverage_pct)
    ice=pd.read_csv(climate);g=ice[(ice.site_id=='GOPT') & (ice.inner_km==0)]
    assert not g.duplicated(['year','month']).any()
    assert g.complete_month.all()
    for label,months in [('ice10',[8,9,10,11]),('ice_sep10',[9]),('ice_oct10',[10])]:
        means=g[g.month.isin(months)].groupby('year').sic_mean.mean()/10
        assert g[g.month.isin(months)].groupby('year').size().eq(len(months)).all()
        d[label]=d.year.map(means)
    assert len(d)==17 and not d.isna().any().any()
    d['year_c']=d.year-d.year.mean();d['post2003']=(d.year>=2003).astype(int)
    d['Adelie_colony']=np.where(d.year<2003,'A41','A39');d['Chinstrap_colony']='C69'
    d.to_csv(out/'signy_17_seasons.csv',index=False,lineterminator="\n")
    provenance.append(dict(file=str(climate),sha256=hashlib.sha256(climate.read_bytes()).hexdigest()))

    # Freeze main comparison: paired gap ~ October station temperature + Aug-Nov ice.
    # HC3 uncertainty is small-sample heteroskedasticity robust, not time dependence robust.
    results=[]
    specs={'temperature_only':['temp_oct'],'ice_only':['ice10'],
           'joint_primary':['temp_oct','ice10'],
           'joint_year':['temp_oct','ice10','year_c'],
           'joint_colony':['temp_oct','ice10','post2003'],
           'joint_year_colony':['temp_oct','ice10','year_c','post2003'],
           'September_ice_temperature':['temp_oct','ice_sep10'],
           'October_ice_temperature':['temp_oct','ice_oct10']}
    def fit(frame,response,cols):
        return sm.OLS(frame[response],sm.add_constant(frame[cols],has_constant='add')).fit()
    for response in ['gap','Adelie','Chinstrap']:
        for name,cols in specs.items():
            model=fit(d,response,cols);rob=model.get_robustcov_results(cov_type='HC3',use_t=True)
            for j,term in enumerate(model.params.index):
                if term=='const':continue
                results.append(dict(response=response,model=name,term=term,n=len(d),
                    estimate=model.params[term],ci_low=rob.conf_int()[j,0],ci_high=rob.conf_int()[j,1],
                    p_hc3=rob.pvalues[j],p_ols=model.pvalues[term],r_squared=model.rsquared,
                    uncertainty='HC3 t; no serial-dependence correction'))
    r=pd.DataFrame(results);r['q_bh_primary_gap_2']=np.nan
    mask=r.response.eq('gap') & r.model.eq('joint_primary')
    r.loc[mask,'q_bh_primary_gap_2']=multipletests(r.loc[mask,'p_hc3'],method='fdr_bh')[1]
    r.to_csv(out/'model_coefficients.csv',index=False,lineterminator="\n")

    sens=[]
    for name,frame,cols in [('October_station_coverage_at_least_90pct',d[d.temp_oct_source_coverage_pct>=90],['temp_oct','ice10']),
                           ('post2003_only',d[d.year>=2003],['temp_oct','ice10']),
                           ('pre2003_only',d[d.year<2003],['temp_oct','ice10'])]:
        model=fit(frame,'gap',cols);rob=model.get_robustcov_results(cov_type='HC3',use_t=True)
        for j,term in enumerate(model.params.index):
            if term!='const':sens.append(dict(analysis=name,term=term,n=len(frame),estimate=model.params[term],ci_low=rob.conf_int()[j,0],ci_high=rob.conf_int()[j,1]))
    diff=d[['year','temp_oct','ice10','gap','post2003']].diff()
    diff=diff.loc[(diff.year==1)&(diff.post2003==0)]
    for name,cols in [('consecutive_differences_no_colony_switch',['temp_oct','ice10'])]:
        model=fit(diff,'gap',cols);rob=model.get_robustcov_results(cov_type='HC3',use_t=True)
        for j,term in enumerate(model.params.index):
            if term!='const':sens.append(dict(analysis=name,term=term,n=len(diff),estimate=model.params[term],ci_low=rob.conf_int()[j,0],ci_high=rob.conf_int()[j,1]))
    pd.DataFrame(sens).to_csv(out/'sensitivity_coefficients.csv',index=False,lineterminator="\n")
    loo=[]
    for i in range(len(d)):
        m=fit(d.drop(index=i),'gap',['temp_oct','ice10'])
        loo.append(dict(omitted_year=int(d.iloc[i].year),temp_oct=m.params.temp_oct,ice10=m.params.ice10))
    pd.DataFrame(loo).to_csv(out/'leave_year_out_coefficients.csv',index=False,lineterminator="\n")
    # Forward hindcasts are diagnostics, as source data/variables were previously explored.
    predictions=[]
    pred_specs={'historical_mean':[],'year_only':['year_c'],'temperature':['temp_oct'],
                'ice':['ice10'],'temperature_ice':['temp_oct','ice10'],
                'year_temperature_ice':['year_c','temp_oct','ice10']}
    for response in ['gap','Adelie','Chinstrap']:
        for i in range(8,len(d)):
            train=d.iloc[:i];test=d.iloc[[i]]
            for name,cols in pred_specs.items():
                pred=train[response].mean() if not cols else float(fit(train,response,cols).predict(sm.add_constant(test[cols],has_constant='add')).iloc[0])
                predictions.append(dict(response=response,year=int(test.year.iloc[0]),n_train=len(train),model=name,observed=float(test[response].iloc[0]),predicted=pred))
    pred=pd.DataFrame(predictions);pred['error']=pred.predicted-pred.observed
    pred.to_csv(out/'forward_predictions.csv',index=False,lineterminator="\n")
    scores=pred.groupby(['response','model']).agg(n=('error','size'),mae=('error',lambda v:np.abs(v).mean()),rmse=('error',lambda v:np.sqrt(np.mean(v**2)))).reset_index()
    scores.to_csv(out/'forward_scores.csv',index=False,lineterminator="\n")

    # NOAA confirmed event observations: retain photo vs ground differences and nest IDs.
    noaa=workspace/'work/climate_penguin/phenology/noaa/0171619/1.1/data/1-data'
    photo=pd.read_csv(noaa/'repro v1-1-DATA.csv')
    keys=['YEAR','ROOKERY','SPP','COLONY','CAMERA','NEST']
    flag=photo[photo.HATCH.eq(1)].copy();flag['DATE']=pd.to_datetime(flag.DATE,format='%m/%d/%Y')
    nest=flag.groupby(keys,dropna=False).DATE.min().reset_index().rename(columns={'YEAR':'season','DATE':'date'})
    nest['method']='photo_confirmed_first_hatch'
    ground=pd.read_csv(noaa/'validation v1-1-DATA.csv')
    ground=ground[ground.C1HATCH.notna()].copy()
    ground['date']=pd.to_datetime(ground.C1HATCH,format='%m/%d/%Y')
    ground=ground.rename(columns={'SEASON':'season'});ground['method']='ground_first_chick'
    cols=['season','ROOKERY','SPP','COLONY','CAMERA','NEST','date','method']
    nest=pd.concat([nest[cols],ground[cols]],ignore_index=True)
    nest['year']=nest.season.str[:4].astype(int)
    nest['day']=[(r.date-pd.Timestamp(r.year,10,1)).days for r in nest.itertuples()]
    nest['species']=nest.SPP.map({1:'Adelie',2:'Gentoo',3:'Chinstrap'})
    assert not nest.duplicated(['method','season','ROOKERY','SPP','COLONY','CAMERA','NEST']).any()
    support=nest.groupby(['method','ROOKERY','year','species']).agg(n_nests=('day','size'),mean_day=('day','mean'),median_day=('day','median'),n_colonies=('COLONY','nunique')).reset_index()
    support.to_csv(out/'noaa_hatching_support.csv',index=False,lineterminator="\n")
    pairs=[]
    for (method,site,year),group in support.groupby(['method','ROOKERY','year']):
        for a,b in [('Adelie','Chinstrap'),('Adelie','Gentoo'),('Gentoo','Chinstrap')]:
            g1=group[group.species==a];g2=group[group.species==b]
            if len(g1) and len(g2):
                aa=g1.iloc[0];bb=g2.iloc[0]
                pairs.append(dict(method=method,site=site,year=year,species_A=a,species_B=b,n_A=int(aa.n_nests),n_B=int(bb.n_nests),mean_gap_B_minus_A=bb.mean_day-aa.mean_day,median_gap_B_minus_A=bb.median_day-aa.median_day))
    pairs=pd.DataFrame(pairs);pairs.to_csv(out/'noaa_same_site_year_pairs.csv',index=False,lineterminator="\n")
    # Do not stack camera and validation nests as independent observations.
    photo_all=photo[keys].drop_duplicates()
    coverage=photo.groupby(['YEAR','ROOKERY','SPP']).agg(n_source_rows=('DATE','size')).reset_index()
    coverage['n_nests']=coverage.apply(lambda r:len(photo_all[(photo_all.YEAR==r.YEAR)&(photo_all.ROOKERY==r.ROOKERY)&(photo_all.SPP==r.SPP)]),axis=1)
    coverage.to_csv(out/'noaa_all_source_coverage.csv',index=False,lineterminator="\n")
    for name in ['repro v1-1-DATA.csv','validation v1-1-DATA.csv']:
        provenance.append(dict(file=name,url='https://www.ncei.noaa.gov/archive/accession/0171619/1.1',sha256=hashlib.sha256((noaa/name).read_bytes()).hexdigest()))
    # Independent scalar verification of the paired gap and simple slopes.
    checks={'signy_34_rows_17_pairs':len(long)==34 and len(d)==17,
            'calendar_gap_matches_published_gap':bool(np.array_equal(d.gap,published.Chinstrap-published.Adelie)),
            'noaa_photo_77_events_74_nests':len(flag)==77 and int((nest.method=='photo_confirmed_first_hatch').sum())==74,
            'primary_two_tests':int(mask.sum())==2}
    for x in ['temp_oct','ice10']:
        independent=linregress(d[x],d.gap).slope
        checks['independent_slope_'+x]=bool(np.isclose(independent,fit(d,'gap',[x]).params[x]))
    assert all(checks.values())
    summary=dict(signy_n_sites=1,signy_n_seasons=len(d),signy_years=d.year.tolist(),
        mean_gap_days=float(d.gap.mean()),gap_range=[float(d.gap.min()),float(d.gap.max())],
        noaa_pair_sites=int(pairs.site.nunique()),noaa_method_pair_rows=len(pairs),
        noaa_unique_site_pair_years=len(pairs.drop_duplicates(['site','year','species_A','species_B'])),
        temp_ice_r=float(d.temp_oct.corr(d.ice10)),
        primary_results=r.loc[mask].to_dict('records'),checks=checks,provenance=provenance,
        scope='Existing local NOAA archive plus public Signy annual hatching, not all global available data',
        inference='Exploratory; one island; HC3 not serial correction; no equivalence test or causal warming attribution; no future biological forecast',
        method='Signy model-estimated 50%-nest hatching date; NOAA mean first confirmed nest hatch, kept separate')
    (out/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8',newline='\n')
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    print(scores.to_string(index=False));print(pairs.to_string(index=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',type=Path,required=True)
    run(p.parse_args().workspace)
