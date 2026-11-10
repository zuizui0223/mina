"""Audit independently published winter tracks without inferring return events."""
from pathlib import Path
import zipfile,json,hashlib
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/chinstrap_winter_v1'
with zipfile.ZipFile(OUT/'source.zip') as z:
    d=pd.read_csv(z.open('S1 Data/tracks.csv'),dtype={'LOC_CLASS':str,'PTT':str})
    extra=[c for c in d if c.startswith('Unnamed:')]
    assert d[extra].isna().all().all()
    d=d.drop(columns=extra)
    (OUT/'source_readme.txt').write_bytes(z.read('S1 Data/READ ME.txt'))
    (OUT/'source_nest_counts.csv').write_bytes(z.read('S1 Data/abund.csv'))
assert d[['PTT','LOC_DATE','LATITUDE','LONGITUDE','STAGE','COLONY']].notna().all().all()
d['time']=pd.to_datetime(d.LOC_DATE,format='%m/%d/%Y %H:%M')
assert d.LATITUDE.between(-90,90).all() and d.LONGITUDE.between(-180,180).all()
d['month']=d.time.dt.month;d['year']=d.time.dt.year
d['quality_1_to_3']=d.LOC_CLASS.isin(['1','2','3'])
d['date']=d.time.dt.date.astype(str)
assert d.groupby('PTT').COLONY.nunique().eq(1).all()
assert d.groupby('PTT').STAGE.nunique().eq(1).all()
monthly=d.groupby(['year','month','COLONY','STAGE'],as_index=False).agg(rows=('PTT','size'),tags=('PTT','nunique'),days=('date','nunique'),quality_1_to_3_rows=('quality_1_to_3','sum'))
monthly.to_csv(OUT/'monthly_support.csv',index=False)
individual=d.groupby(['PTT','COLONY','STAGE'],as_index=False).agg(first=('time','min'),last=('time','max'),rows=('time','size'),days=('date','nunique'))
for label,months in [('september',[9]),('october',[10]),('september_october',[9,10])]:
    a=d[d.month.isin(months)]
    sizes=a.groupby('PTT').size();hq=a[a.quality_1_to_3].groupby('PTT').size()
    individual[label+'_rows']=individual.PTT.map(sizes).fillna(0).astype(int)
    individual[label+'_quality_rows']=individual.PTT.map(hq).fillna(0).astype(int)
individual.to_csv(OUT/'individual_support.csv',index=False)
d.to_csv(OUT/'tracks_normalized.csv.gz',index=False,compression='gzip')
summary={'source':'https://doi.org/10.1371/journal.pone.0226207.s008',
 'download_url':'https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0226207.s008&type=supplementary',
 'source_sha256':hashlib.sha256((OUT/'source.zip').read_bytes()).hexdigest(),
 'rows':len(d),'tags':d.PTT.nunique(),'first':str(d.time.min()),'last':str(d.time.max()),
 'full_duplicate_rows':int(d.duplicated(['PTT','LOC_DATE','LOC_CLASS','LATITUDE','LONGITUDE','STAGE','COLONY']).sum()),
 'duplicate_tag_times':int(d.duplicated(['PTT','time']).sum()),
 'september_october_rows':int(d.month.isin([9,10]).sum()),
 'september_october_tags':d[d.month.isin([9,10])].PTT.nunique(),
 'september_october_quality_rows':int((d.month.isin([9,10])&d.quality_1_to_3).sum()),
 'september_october_adult_tags':d[d.month.isin([9,10])&d.STAGE.eq('adult')].PTT.nunique(),
 'timezone':'not declared by source readme; parsed as naive source timestamps, no UTC assertion',
 'limitations':['deployment surviving into September is not proof of observed return','juveniles cannot be classified as returning breeders','raw Argos positions require error filtering/state-space treatment','one year and three colonies cannot identify a continent-wide transport mechanism']}
assert monthly.rows.sum()==len(d) and individual.rows.sum()==len(d)
(OUT/'validation.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2));print(monthly[monthly.month.isin([9,10])].to_string(index=False))
