"""Source support only, no count magnitudes or ecological fit.
Usage: python syowa_source_gate.py mapppd.zip marine.zip output.json
"""
import hashlib,json,math,re,sys,zipfile
from pathlib import Path
from itertools import combinations
import pandas as pd
PINS=('0264797d82bee62df3b14346428abb4a4994ec01224906c3468afbe99a2c56c4','64a8e9832e254171139d78bb22351d6c9a3acf490356931b2635ed5b108d94b5')
# Explicit name candidates from NIPR AMB1001 official monitoring roster; not proof of footprint equivalence.
SITES={'MAME':('まめ島',-69.0252,39.47823),'ONGU':('オングルカルベン',-69.0171,39.42498),'BENT':('弁天島',-69.0404,39.24244),'RUMP':('ルンパ',-69.1447,39.39478),'SIGA':('シガーレン',-69.1691,39.43687),'MIZU':('水くぐり浦',-69.1977,39.61371),'HUKU':('袋浦',-69.2127,39.62942),'YTRE':('イットレホブデホルメン',-69.2099,39.44497),'TORI':('鳥の巣湾',-69.4932,39.56156),'NOKK':('ネッケルホルマネ',-69.3828,39.4668)}
def read(p,pin,member):
    assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==pin
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        return pd.read_csv(z.open(member))
def distance(p,q):
    a,b,c,d=map(math.radians,(*p,*q));h=math.sin((a-c)/2)**2+math.cos(a)*math.cos(c)*math.sin((b-d)/2)**2
    return 2*6371.0088*math.asin(math.sqrt(max(0,min(1,h))))
def run(v5,marine):
    d=read(v5,PINS[0],'public_source.csv');m=read(marine,PINS[1],'original_588_site_1993_2020_actual_SIC_SSS_SST_PC1.csv')
    assert len(d)==5487 and len(m)==16464 and m.site_id.nunique()==588
    q=d[d.site_id.isin(SITES)&d.common_name.eq('adelie penguin')].copy();assert q.site_id.nunique()==10
    q['citekey']=q.reference.str.extract(r'id="([^"]+)"')
    out=[]
    for sid,(name,lat,lon) in SITES.items():
        x=q[q.site_id.eq(sid)];p=x[['site_name','latitude_epsg_4326','longitude_epsg_4326']].drop_duplicates();assert len(p)==1
        r=p.iloc[0];gap=distance((lat,lon),(r.latitude_epsg_4326,r.longitude_epsg_4326));a=x[x.count_type.eq('adults')];n=x[x.count_type.eq('nests')];t=a[a.month.eq(11)&a.day.between(10,20)];cm=m[m.site_id.eq(sid)]
        out.append({'site_id':sid,'official_name':name,'mapppd_name':r.site_name,'coordinate_gap_km':gap,'counts_by_type':{k:int(v) for k,v in x.count_type.value_counts().items()},'adult_last_season':int(a.season_starting.max()),'known_nov10_20_adult_rows':len(t),'nest_seasons':sorted(map(int,n.season_starting.unique())),'marine_coverage_years':int(cm.year.nunique()),'marine_wet_cells':int(cm[['GLORYS_cell_y','GLORYS_cell_x']].drop_duplicates().shape[0]),'marine_blocks':sorted(cm.source_250km_block.unique())})
    a=q[q.count_type.eq('adults')];k=a[a.citekey.eq('kato2006increase')]
    support={}
    for field in ('adults','nests'):
        a=q[q.count_type.eq(field)&q.penguin_count.notna()];h=a[a.season_starting.between(1993,2010)];e=a[a.season_starting.between(2011,2020)]
        support[field]={'history_rows':len(h),'evaluation_rows':len(e),'evaluation_sites':int(e.site_id.nunique())}
    return {'status':'SOURCE_REQUEST_REQUIRED_NO_NEW_OUTCOME_PANEL','input_archive_sha256':list(PINS),'official_roster_url':'https://www.nipr.ac.jp/antarctic/science-plan10/kihon-biology01.html','counts_by_type':{k:int(v) for k,v in q.count_type.value_counts().items()},'n_rows':len(q),'sites':out,'max_official_site_distance_km':max(distance(x[1:],y[1:]) for x,y in combinations(SITES.values(),2)),'historical_evaluation_support':support,'kato_2006_adult_rows':len(k),'kato_2006_missing_month':int(k.month.isna().sum()),'adult_records_end':int(q[q.count_type.eq('adults')].season_starting.max()),'ecological_fit':False,'independent_events_certified':False}
if __name__=='__main__':Path(sys.argv[3]).write_text(json.dumps(run(*sys.argv[1:3]),ensure_ascii=False,indent=2)+'\n')
