"""Rebuild the legacy nest-count panel from public MAPPPD v5 CSV; support only.
Usage: python mapppd_v5_reconcile.py v5.zip legacy.zip marine.zip result.json
"""
import argparse, hashlib, json, zipfile
from pathlib import Path
import pandas as pd

PINS={'v5':'0264797d82bee62df3b14346428abb4a4994ec01224906c3468afbe99a2c56c4',
      'legacy':'add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a',
      'marine':'64a8e9832e254171139d78bb22351d6c9a3acf490356931b2635ed5b108d94b5'}
CSV_PIN='d169c409cf278b137d6df35fbeb9ab3409bdea15f41c39bcaec549a4d4dbca89'
SPECIES={'adelie penguin':'ADPE','chinstrap penguin':'CHPE','gentoo penguin':'GEPE',
         'emperor penguin':'EMPE','king penguin':'KIPE','macaroni penguin':'MCPE'}
FOCAL={'ADPE','CHPE','GEPE'}
KEY=['site_id','species','season']
SERIES=KEY[:2]
def load(path,kind):
    if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=PINS[kind]:raise ValueError('archive digest drift '+kind)
    z=zipfile.ZipFile(path)
    if z.testzip() is not None:raise ValueError('archive CRC '+kind)
    return z

def run(v5,legacy,marine):
    with load(v5,'v5') as z:
        assert hashlib.sha256(z.read('public_source.csv')).hexdigest()==CSV_PIN
        x=pd.read_csv(z.open('public_source.csv'))
    with load(legacy,'legacy') as z:
        o=pd.read_csv(z.open('source_observed_2456.csv'))
        s=pd.read_csv(z.open('panantarctic_595_site_inventory.csv'))
    with load(marine,'marine') as z:
        m=pd.read_csv(z.open('original_588_site_1993_2020_actual_SIC_SSS_SST_PC1.csv'))
    assert (len(x),x.site_id.nunique(),x.reference.nunique(),x.duplicated().sum())==(5487,729,183,0)
    assert len(o)==2456 and not o.duplicated(KEY).any() and len(s)==595 and s.site_id.is_unique
    assert len(m)==16464 and m.groupby('site_id').year.nunique().eq(28).all() and m.site_id.nunique()==588
    assert set(m.year)==set(range(1993,2021))
    x['species']=x.common_name.map(SPECIES);assert x.species.notna().all()
    x['season']=x.season_starting
    x['method']=x.vantage.fillna('unknown')
    nests=x[x.count_type=='nests'];v=nests[nests.penguin_count.notna()].copy()
    assert v.penguin_count.ge(0).all() and (v.penguin_count%1==0).all()
    assert len(v)==4032
    g=v.groupby(KEY).agg(n=('penguin_count','size'),nu=('penguin_count','nunique'),nknown=('vantage','nunique'),nm=('method','nunique'),count=('penguin_count','first'),method=('method','first'),nsource=('reference','nunique'),source=('reference','first')).reset_index()
    agree=g[g.nu==1];focal=agree[agree.species.isin(FOCAL)]
    # Reproduce the prior rule: first require numeric agreement and one known
    # method per site-species-season; then choose the most frequent method over
    # all seasons (lexical tie-break). The rule is not a claim of observation independence.
    known=focal[(focal.nknown==1)&(focal.nm==1)&(focal.method!='unknown')].copy()
    rank=known.groupby(SERIES+['method']).size().reset_index(name='n_seasons').sort_values(SERIES+['n_seasons','method'],ascending=[True,True,False,True])
    chosen=known.merge(rank.drop_duplicates(SERIES)[SERIES+['method']],on=SERIES+['method'],validate='many_to_one')
    assert (len(g),len(agree),len(focal),len(known),len(chosen))==(3399,2999,2861,2724,2456)
    match=o.merge(chosen,on=KEY,how='outer',validate='one_to_one',indicator=True)
    assert match._merge.eq('both').all()
    assert match.observed_nest_count.eq(match['count']).all() and match.original_survey_method.eq(match.method).all()
    extra=known.merge(o[KEY],on=KEY,how='left',indicator=True).query('_merge=="left_only"')
    old_series=set(map(tuple,o[SERIES].drop_duplicates().values))
    assert set(map(tuple,extra[SERIES].values))<=old_series and len(extra)==268
    def qualify(frame,same_ref=False):
        k=SERIES+['method']+(['source'] if same_ref else [])
        h=frame[frame.season.between(1993,2010)].groupby(k).season.agg(['size'])
        e=frame[frame.season.between(2011,2020)].groupby(k).season.agg(['size','min','max'])
        t=h.join(e,how='inner',lsuffix='_h',rsuffix='_e').reset_index()
        t=t[(t.size_h>=2)&(t.size_e>=2)&(t['max']-t['min']>=5)]
        ss=t[SERIES].drop_duplicates();c=ss[ss.site_id.isin(m.site_id)].merge(s[['site_id','source_region']],on='site_id',validate='many_to_one')
        primary=c[c.groupby(['species','source_region']).site_id.transform('size')>=3]
        return dict(method_or_reference_candidates=len(t),series=len(ss),climate_series=len(c),primary_series=len(primary),primary_sites=primary.site_id.nunique(),primary_regions=sorted(primary.source_region.unique()),strata=[{'species':sp,'region':reg,'n':len(a)} for (sp,reg),a in c.groupby(['species','source_region'])]),set(map(tuple,t[SERIES+['method']].values))
    base,keys=qualify(o.rename(columns={'original_survey_method':'method'}));allm,keys2=qualify(known);strict,_=qualify(known[known.nsource==1],True)
    assert keys==keys2 and (base['series'],base['climate_series'],base['primary_series'])==(59,53,51)
    # Direct independent check of season-vs-calendar key alignment against old selected rows.
    def match_time(t):
        p=v[v.species.isin(FOCAL)].copy();p['join_year']=p[t]
        j=o.merge(p,left_on=KEY,right_on=SERIES+['join_year'],how='left')
        yes=j.observed_nest_count.eq(j.penguin_count)&j.original_survey_method.eq(j.method)
        return int(j.loc[yes,['site_id','species','season_x']].drop_duplicates().shape[0])
    return {'status':'EXACT_LEGACY_REPRODUCTION_NO_NEW_ELIGIBLE_SERIES','input_zip_sha256':PINS,'v5_csv_sha256':CSV_PIN,
       'source':{'all_records':len(x),'all_sites':x.site_id.nunique(),'references':x.reference.nunique(),'all_nest_rows':len(nests),'numeric_nest_rows':len(v),'focal_numeric_nest_rows':int(v.species.isin(FOCAL).sum()),'focal_numeric_nest_sites':v[v.species.isin(FOCAL)].site_id.nunique(),'missing_nest_count_rows':int(nests.penguin_count.isna().sum()),'all_numeric_nest_site_species_seasons':len(g),'conflicting_count_groups':int((g.nu>1).sum()),'unambiguous_count_groups':len(agree),'focal_agree_groups':len(focal),'one_known_method_focal_groups':len(known),'legacy_rebuilt_rows':len(chosen),'legacy_exact_keys_counts_methods':len(match),'exact_match_season_start':match_time('season_starting'),'exact_match_calendar_year':match_time('year')},
       'excluded_alternative_methods':{'n_rows':len(extra),'sites':extra.site_id.nunique(),'new_site_species':0,'by_species':extra.species.value_counts().to_dict(),'seasons_since_2021':extra[extra.season>=2021].season.value_counts().sort_index().to_dict()},
       'support':{'legacy':base,'all_known_methods_separate':allm,'same_reference_and_method':strict,'same_eligible_site_species_method_keys':keys==keys2},
       'source_boundary':'Same v5 release as earlier API audit; all legacy rows recovered, not an independent observation archive. Alternate methods do not increase the eligible roster. Same-reference support is descriptive, not proof of independence. Missing counts never zero; no ecological refit.'}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('v5');ap.add_argument('legacy');ap.add_argument('marine');ap.add_argument('out',type=Path);a=ap.parse_args();r=run(a.v5,a.legacy,a.marine);a.out.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n');print(json.dumps(r,indent=2,ensure_ascii=False))
