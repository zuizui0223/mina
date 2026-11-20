"""Audit public diet inventory; no environmental outcomes used to choose records.
Run: python audit_inventory.py --workbook /path/Penguin_Diet_Dataset-v2.xlsx
Dependencies: pandas, openpyxl. Download source is recorded in summary.json.
"""
import argparse, hashlib, json
from pathlib import Path
import pandas as pd
p=argparse.ArgumentParser();p.add_argument('--workbook',type=Path,required=True);a=p.parse_args()
out=Path(__file__).resolve().parent
x=pd.read_excel(a.workbook,sheet_name='Dat_entry')
ad=x[x.Code_predator.eq('Pygo_ade')].copy()
s=ad[ad.Code_method.eq(3)].copy()
s['valid_mass']=pd.to_numeric(s['WEIGHT(%)'],errors='coerce').between(0,100)
rows=[]
for url,g in s.groupby('URL'):
 rows.append(dict(source_url=url,prey_rows=len(g),coordinates=len(g[['Latitude','Longitude']].drop_duplicates()),mass_rows=int(g.valid_mass.sum()),start_year_min=g.Start_year.min(),end_year_max=g.End_year.max(),start_year_labels=';'.join(str(int(v)) for v in sorted(g.Start_year.dropna().unique())),latitude=g.Latitude.iloc[0],longitude=g.Longitude.iloc[0],post2003_start_label=bool(g.Start_year.ge(2003).any())))
pd.DataFrame(rows).to_csv(out/'stomach_source_inventory.csv',index=False,lineterminator='\n')
summary=dict(source='https://digital.csic.es/bitstream/10261/399953/1/Penguin_Diet_Dataset-v2.xlsx',sha256=hashlib.sha256(a.workbook.read_bytes()).hexdigest(),adelie_prey_rows=len(ad),adelie_sources=ad.URL.nunique(),adelie_coordinates=len(ad[['Latitude','Longitude']].drop_duplicates()),stomach_prey_rows=len(s),stomach_sources=s.URL.nunique(),stomach_coordinates=len(s[['Latitude','Longitude']].drop_duplicates()),valid_mass_rows=int(s.valid_mass.sum()),post2003_label_sources=s.loc[s.Start_year.ge(2003),'URL'].nunique(),post2003_label_mass_rows=int(s.loc[s.Start_year.ge(2003),'valid_mass'].sum()))
# Tables transcribed from Hope Table 1 and Stranger Table 1; references in report.
records=[]
for y,k in [(2014,99.89),(2015,99.64),(2017,99.99),(2018,99.69)]:
 records.append(dict(locality='Hope',source_year_label=y,season_start_year=y,season_end_year=y+1,krill_mass_percent=k,source='10.5038/2074-1235.51.1.1520',statistic='reported_M_percent',provenance='primary_table_new_transcription'))
for y,k in [(2003,99.94),(2004,99.97),(2005,99.98),(2006,99.88),(2008,99.99),(2009,99.92),(2010,99.91),(2011,99.83),(2012,99.98),(2013,99.78),(2014,99.82),(2015,99.86)]:
 records.append(dict(locality='Stranger',source_year_label=y,season_start_year=y-1,season_end_year=y,krill_mass_percent=k,source='10.1007/s00300-017-2191-3',statistic='reported_M_percent',provenance='primary_table_new_transcription'))
root=out.parents[1]
palmer=pd.read_csv(root/'work/palmer_signy_diet_external_v1/sources/pickett2018_palmer_diet_species_season.csv')
for r in palmer[palmer.species.eq('Adelie')].itertuples():
 records.append(dict(locality='Palmer',source_year_label=r.source_year_label,season_start_year=r.season_start_year,season_end_year=r.season_end_year,krill_mass_percent=r.e_superba_mean_pct,source=r.source_doi,statistic='mean_sample_wet_mass_percent',provenance='existing_repo_primary_table_extraction'))
t=pd.DataFrame(records);t['preceding_winter_in_2003_2022']=t.season_start_year.between(2003,2022)
t.to_csv(out/'primary_table_seasons.csv',index=False,lineterminator='\n')
summary['table_localities']=t.locality.nunique();summary['table_site_seasons']=len(t);summary['table_seasons_preceding_winter_2003_2022']=int(t.preceding_winter_in_2003_2022.sum())
(out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
assert not t.duplicated(['locality','season_start_year']).any()
assert t.krill_mass_percent.between(0,100).all()
assert t.season_end_year.sub(t.season_start_year).eq(1).all()
print(json.dumps(summary,indent=2))
