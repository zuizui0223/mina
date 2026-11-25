"""Descriptive published period means: ATCM 46 ASPA128 Table 1. Not annual raw data."""
import csv,hashlib,itertools,json,sys,zipfile
from pathlib import Path
from fractions import Fraction
import pandas as pd
ROOT=Path(sys.argv[1]); OUT=Path(sys.argv[2]);OUT.mkdir(parents=True,exist_ok=True)
SOURCE='https://documents.ats.aq/recatt/att773_e.pdf'
PERIODS=[(1978,1981),(1992,1996),(2009,2012),(2014,2017),(2019,2022)]
# Literal published means; do not expand into annual values. Original table says four-year means but second label spans five calendar start-year labels.
TABLE={'ADPE':{'LLAN':[10859,6073,2454,2853,2231],'PTHO':[11899,9886,4578,4740,3196]},'GEPE':{'LLAN':[2174,1765,4646,6162,8083],'PTHO':[715,267,90,76,0]}}
TOTALS={'ADPE':[22758,15959,7032,7593,5427],'GEPE':[2889,2032,4736,6238,8083]}
for sp,z in TABLE.items(): assert [sum(v[i] for v in z.values()) for i in range(5)]==TOTALS[sp]
def calc(sp,i,j):
 z=TABLE[sp]; d=[v[j]-v[i] for v in z.values()]; L=sum(max(-x,0) for x in d);G=sum(max(x,0) for x in d)
 return {'site_delta':dict(zip(z,d)),'loss':L,'gain':G,'net':G-L,'capped_compensation':float(Fraction(min(L,G),L)) if L else None,'uncapped_gain_loss':G/L if L else None,'total_start':TOTALS[sp][i],'total_end':TOTALS[sp][j],'total_pct':100*(TOTALS[sp][j]/TOTALS[sp][i]-1)}
def comparison(i,j):
 return {'start':PERIODS[i],'end':PERIODS[j],**{sp:calc(sp,i,j) for sp in TABLE}}
endpoint=comparison(0,4); successive=[comparison(i,i+1) for i in range(4)];paired=[r for r in successive if all(r[sp]['loss']>0 for sp in TABLE)]
assert len(paired)==3
assert all(r['ADPE']['capped_compensation']==0 for r in paired)
assert sum(r['GEPE']['capped_compensation']>0 for r in paired)==2
# Source lineage audit: compare coverage only, no unsupported calendar convention or exact annual averaging.
p=ROOT/'github-actions-artifact-14934334550.zip'; assert hashlib.sha256(p.read_bytes()).hexdigest()=='0264797d82bee62df3b14346428abb4a4994ec01224906c3468afbe99a2c56c4'
with zipfile.ZipFile(p) as z:
 assert z.testzip() is None
 assert hashlib.sha256(z.read('public_source.csv')).hexdigest()=='d169c409cf278b137d6df35fbeb9ab3409bdea15f41c39bcaec549a4d4dbca89'
 x=pd.read_csv(z.open('public_source.csv'))
assert len(x)==5487
x=x[x.site_id.isin(['LLAN','PTHO'])&x.count_type.eq('nests')&x.common_name.isin(['adelie penguin','gentoo penguin'])&x.penguin_count.notna()].copy();x['species']=x.common_name.map({'adelie penguin':'ADPE','gentoo penguin':'GEPE'});x['cite']=x.reference.str.extract(r'id="([^\"]+)"');assert len(x)==154
coverage=[]
for sp,site in itertools.product(TABLE,['LLAN','PTHO']):
 q=x[(x.species==sp)&(x.site_id==site)]
 coverage.append({'species':sp,'site':site,'raw_rows':len(q),'last_season':int(q.season_starting.max()),'period_support':[{'period':[a,b],'original_seasons':sorted(map(int,q.loc[q.season_starting.between(a,b),'season_starting'].unique())),'source_references':sorted(q.loc[q.season_starting.between(a,b),'cite'].dropna().unique().tolist())} for a,b in PERIODS]})
assert all(not r['period_support'][-1]['original_seasons'] for r in coverage)
result={'status':'PUBLISHED_PERIOD_MEAN_ACCOUNTING_NOT_INDEPENDENT_ANNUAL_REPLICATION','source':SOURCE,'table':'Table 1, ATCM 46 revised ASPA 128 plan, published period means','verification':'Web-extracted text checked for table totals; PDF screenshot cache miss and local download DNS failure, no visual verification or source PDF hash; do not claim original annual acquisition.','periods':PERIODS,'counts':TABLE,'endpoint':endpoint,'successive':successive,'paired_loss_windows':len(paired),'paired_equal_window_mean':{sp:sum(r[sp]['capped_compensation'] for r in paired)/len(paired) for sp in TABLE},'paired_loss_weighted':{sp:sum(min(r[sp]['loss'],r[sp]['gain']) for r in paired)/sum(r[sp]['loss'] for r in paired) for sp in TABLE},'mapppd_lineage_coverage':coverage,'latest_period_no_raw_rows_in_v5':True,'limitations':['Different time grain than frozen annual comparison; descriptive follow-up, not a rescue test.','Published means, not actual same-season raw observations; 1992–96 label spans five start years despite four-year caption, actual sampled years unknown.','Earlier period sources overlap MAPPPD; later 2019–22 means are absent as annual rows in v5 but event provenance and sampling effort unverified.','Point Thomas zero is a reported period average, not necessarily extinction year; no inference of individual migration, immigration, competition or causal climate effect.','Only one two-site area; net change in means not total birds or species-wide rate. No annual polynya fit.']}
(OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
