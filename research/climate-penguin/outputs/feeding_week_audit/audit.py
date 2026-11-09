"""Run in the outer mina workspace with cached BAS sources and the previous high-ice audit."""
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO, StringIO
import csv, hashlib, json, re
import requests
import pymupdf
import numpy as np
import pandas as pd
from pyproj import Geod

out=Path('outputs/feeding_week_audit')
out.mkdir(exist_ok=True)
raw=Path('work/feeding_week')
raw.mkdir(exist_ok=True)
urls={'myctobase.zip':'https://ipt.biodiversity.aq/archive.do?r=myctobase',
      'bernard.pdf':'https://ars.els-cdn.com/content/image/1-s2.0-S0967063716303545-mmc1.pdf',
      'sup.docx':'https://pmc-oa-opendata.s3.amazonaws.com/PMC6202752.1/ECE3-8-9764-s001.docx'}
manifest={}
for name,url in urls.items():
    file=raw/name
    if not file.exists():
        resp=requests.get(url,timeout=60);resp.raise_for_status();file.write_bytes(resp.content)
    manifest[name]={'url':url,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
(out/'sources.json').write_text(json.dumps(manifest,indent=2))
net=pd.read_csv('outputs/high_ice_diet_prey/matching_hauls.csv')
net['haul_timestamp']=pd.to_datetime(net.DATE,format='%d/%m/%Y')
with ZipFile('work/highice_prey/krillbase.zip') as wrapper:
    with ZipFile(BytesIO(wrapper.read(wrapper.namelist()[0]))) as z:
        depths=pd.read_csv(z.open('krillbase_data.csv'),encoding='cp1252')[['STATION','TOP_SAMPLING_DEPTH_M','BOTTOM_SAMPLING_DEPTH_M']]
net=net.merge(depths,on='STATION',validate='many_to_one')
with ZipFile(raw/'myctobase.zip') as z:
    def read_table(name):
        return pd.DataFrame(list(csv.DictReader(StringIO(z.read(name).decode('utf8')),delimiter='\t',quoting=csv.QUOTE_NONE)))
    event=read_table('event.txt');occ=read_table('occurrence.txt')
for key in ['decimalLongitude','decimalLatitude']:
    event[key]=pd.to_numeric(event[key],errors='coerce')
geo=Geod(ellps='WGS84')
def distance(xs,ys,x,y):
    return geo.inv(xs,ys,np.full(len(xs),x),np.full(len(xs),y))[2]/1000
windows=[('Signy',2006,'2007-01-25','2007-01-25',-45.5863,-60.7309),('Signy',2007,'2008-01-20','2008-01-20',-45.5863,-60.7309),('Palmer',2013,'2014-01-30','2014-02-12',-63.7775,-64.8114)]
summary=[];tables=[];fish=[]
for site,yr,start,end,x,y in windows:
    lo,hi=pd.Timestamp(start),pd.Timestamp(end)
    h=net.query('region==@site and year==@yr').copy();h['colony_proxy_km']=distance(h.LONGITUDE,h.LATITUDE,x,y);h=h[h.colony_proxy_km<=100].copy()
    h['offset_days']=np.maximum((lo-h.haul_timestamp).dt.days,(h.haul_timestamp-hi).dt.days).clip(lower=0);tables.append(h)
    f=event.copy();f['km']=distance(f.decimalLongitude,f.decimalLatitude,x,y)
    f=f[(f.km<=100)&f.eventDate.between((lo-pd.Timedelta(days=3)).strftime('%Y-%m-%d'),(hi+pd.Timedelta(days=3)).strftime('%Y-%m-%d'))]
    for row in f.itertuples():
        n=h.assign(station_km=distance(h.LONGITUDE,h.LATITUDE,row.decimalLongitude,row.decimalLatitude)).sort_values('station_km').iloc[0]
        species=occ[occ.eventID.eq(row.eventID)]
        for animal in species.itertuples():
            fish.append(dict(event=row.eventID,recorded_date=row.eventDate,km= row.km,net_max_m=row.maximumDepthInMeters,taxon=animal.scientificName,count=animal.individualCount,quantity=animal.organismQuantity,unit=animal.organismQuantityType,matched_krill_station=n.STATION,krill_date=n.DATE,km_between=n.station_km,krill_m2=n.STANDARDISED_KRILL_UNDER_1M2,week_usable=False))
    summary.append(dict(site=site,start_year=yr,from_date=start,to_date=end,date_basis='BAS stomach day' if site=='Signy' else 'Fig S1 study interval; approx +/-1 day',season_hauls=len(h),inside=sum(h.offset_days==0),within3=sum(h.offset_days<=3),within7=sum(h.offset_days<=7),raw_fish_events_plus3=len(f),complete_spacetime_depth_joins=0))
pd.DataFrame(fish).to_csv(out/'disputed_fish_records.csv',index=False)
pd.concat(tables).to_csv(out/'net_time_distance_depth.csv',index=False)
pd.DataFrame(summary).to_csv(out/'window_support.csv',index=False)
# Bernard supplement Table 3 is a table of percentages of observed aggregations.
with pymupdf.open(raw/'bernard.pdf') as pdf:
    txt=pdf[2].get_text(sort=True)
entries=re.findall(r'2013-2014\s+(\d+/\d+/14)\s+(SD|D)\s+(\d+)\s+(\d+)\s+(\d+)',txt)
a=pd.DataFrame(entries,columns=['date','tide','type_I_pct','type_II_pct','type_III_pct']);assert len(a)==11
a['date']=pd.to_datetime(a.date,format='%m/%d/%y');a['in_diet_period']=a.date.between('2014-01-30','2014-02-12')
a['in_tagging_period']=a.date.between('2014-01-29','2014-02-02');a.to_csv(out/'palmer_acoustic_days.csv',index=False)
with ZipFile('outputs/niche_multiscale_v1/source/Gentoo.zip') as z:
    d=pd.read_csv(z.open(next(n for n in z.namelist() if n.endswith('_diet_summary.csv'))))
d=d[d.DATE.isin([w[2] for w in windows[:2]])].copy()
d['fish_share']=d.FISH_MASS_g/(d.FISH_MASS_g+d.CRUSTACEAN_MASS_g);assert d.fish_share.between(0,1).all()
d.groupby('DATE').agg(n=('fish_share','size'),fish_positive=('FISH_MASS_g',lambda v:int((v>0).sum())),majority_fish=('fish_share',lambda v:int((v>.5).sum())),mean_fish_share=('fish_share','mean'),median_fish_share=('fish_share','median')).to_csv(out/'signy_stomach_days.csv')
print(pd.DataFrame(summary).to_string(index=False));print(pd.read_csv(out/'signy_stomach_days.csv').to_string(index=False));print(a[a.in_diet_period])
