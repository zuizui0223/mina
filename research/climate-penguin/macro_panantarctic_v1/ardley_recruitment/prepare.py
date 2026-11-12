from pathlib import Path
import sys,hashlib
import pymupdf,pandas as pd,numpy as np
R=Path(__file__).resolve().parent
pdf=Path(sys.argv[1]);assert hashlib.sha256(pdf.read_bytes()).hexdigest()=="6c1afd95badb37bed09c7ab7cfe40749c6f381c50947e206d35c4d74fd1082c6"
doc=pymupdf.open(pdf);fig6=doc[45].get_drawings();fig10=doc[53].get_drawings()
def points(draw,indices,xlast,step,tick1,val1,tick2,val2):
    out={}
    for i in indices:
        p=draw[i];assert p['type']=='fs'
        x,y=(p['rect'].tl+p['rect'].br)/2
        endyear=2015+(x-xlast)/step
        assert abs(endyear-round(endyear))<.02
        y1,y2=draw[tick1]['rect'].y0,draw[tick2]['rect'].y0
        out[round(endyear)-1]=val1+(y-y1)*(val2-val1)/(y2-y1)
    return out
records=[]
for sp,idx,lo,hi,v1,v2 in [('GEPE',61,14,24,1500,6500),('ADPE',148,105,111,250,1750)]:
 n=points(fig6,range(idx,idx+35),337.85,5.9265,lo,v1,hi,v2)
 if sp=='ADPE':f=points(fig10,range(100,126),355.76,6.1986,73,.5,75,1.5)
 else:f=points(fig10,[i for i,a in enumerate(fig10) if a["type"]=="fs" and 478<a["rect"].y0<648],355.3,6.357,14,.5,16,1.5)
 for yr in sorted(n):
    records.append(dict(source='UBA_figure',species=sp,year=yr,nests=n[yr],output=f.get(yr,np.nan),chicks=n[yr]*f.get(yr,np.nan)))
t=pd.read_csv(sys.argv[2]).query("site_id=='ARDL' and species_id in ['ADPE','GEPE']")
assert len(t)==20 and t.citekey.nunique()==1
t.to_csv(R/'exact_source.csv',index=False)
for v in t.itertuples():records.append(dict(source='MAPPPD',species=v.species_id,year=v.season_start,nests=v.nest_count,output=v.recorded_chicks_per_nest,chicks=v.chick_count))
d=pd.DataFrame(records).merge(pd.read_csv(R.parent/'ardley_reuse/annual_overlap.csv')[['year','ice','sst']],on='year',how='left')
d.to_csv(R/'panel.csv',index=False)
print(d.query('year==2014').to_string(index=False))
