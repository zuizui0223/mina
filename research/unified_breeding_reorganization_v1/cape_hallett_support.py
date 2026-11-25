"""Source-grain and observation QA only; no plant-animal coefficient."""
import sys, json, zipfile, hashlib, io, re
from pathlib import Path
import pandas as pd
import numpy as np
from pyproj import Transformer
from shapely.geometry import Polygon, box
PINS={15043329180:'63c4f2d2c2c3163db723fff3250778f2544c4fe5a8251e57304ee7d486392755',13669533413:'add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a',14934334550:'0264797d82bee62df3b14346428abb4a4994ec01224906c3468afbe99a2c56c4'}
MEMBER_PINS={'Plot data for McNemar test.csv':'08af8778cc47daddca306a3bcee175ca86aa1f0febb63ec5a05eff8ec4732f6a','ground truthing.csv':'fec2a1124335ee6cdfcb742efc68d18b439e3e1d2e1fd98b8971b1fa31ee697e','Metadata.docx':'371c2c518d60cddc30dab4b143a8d4d7ff30850bf642c78e5fb4bf20d0826e4d'}
def read(root,i):
    raw=(root/f'github-actions-artifact-{i}.zip').read_bytes();assert hashlib.sha256(raw).hexdigest()==PINS[i]
    z=zipfile.ZipFile(io.BytesIO(raw));assert z.testzip() is None;return z
def run(root):
    with read(root,15043329180) as z:
        assert all(hashlib.sha256(z.read(k)).hexdigest()==v for k,v in MEMBER_PINS.items())
        rec=json.loads(z.read('source_receipt.json'));assert rec['status']=='VEGETATION_CSV_ACQUIRED_SCHEMA_REVIEW_REQUIRED'
        rights=[x['value'] for x in rec['metadata']['dc.rights']]
        x=pd.read_csv(z.open('Plot data for McNemar test.csv'),encoding='cp1252',usecols=range(8));x.columns=x.columns.str.strip()
        gt=pd.read_csv(z.open('ground truthing.csv'),header=None,skiprows=1,encoding='utf-8-sig')
    years=[1962,2004,2018];classes=['moss','algae','lichen'];uid='quadrat number'
    assert len(x)==10374 and sorted(x.year.unique())==years and x.groupby('year')[uid].nunique().eq(3458).all()
    assert not x.duplicated([uid,'year']).any() and not x.duplicated(['x','y','year']).any() and x.groupby(uid)[['x','y']].nunique().eq(1).all().all()
    assert all(x[c].isna().equals(x['moss'].isna()) for c in classes)
    assert all(set(x[c].dropna().unique())<=set('nsph') for c in classes)
    w=x.assign(valid=x.moss.notna()).pivot(index=uid,columns='year',values='valid')
    validation={}
    for c,i in zip(classes,[0,5,10]):
        g=gt.iloc[:,i:i+4].dropna().copy();g.columns=['x','y','actual','pred'];assert len(g)==174 and not g.duplicated(['x','y']).any()
        assert set(g.actual.unique())<=set('nsph') and set(g.pred.unique())<=set('nsph')
        pos=g.actual.ne('n');det=g.pred.ne('n');tab=pd.crosstab(g.actual,g.pred).reindex(index=list('nsph'),columns=list('nsph'),fill_value=0)
        validation[c]={'n':len(g),'classes':'nsph','actual_by_predicted':tab.to_numpy().tolist(),'exact_class_agreement':int(g.actual.eq(g.pred).sum()),'presence_agreement':int(pos.eq(det).sum()),'actual_present':int(pos.sum()),'true_positive':int((pos&det).sum()),'actual_absent':int((~pos).sum()),'true_negative':int((~pos&~det).sum())}
    with read(root,13669533413) as z:n=pd.read_csv(z.open('source_observed_2456.csv'))
    a=n[n.site_id.eq('CHAL')&n.species.eq('ADPE')];assert len(a)==18 and a.original_survey_method.eq('aerial').all()
    with read(root,14934334550) as z:
        raw=z.read('public_source.csv');assert hashlib.sha256(raw).hexdigest()=='d169c409cf278b137d6df35fbeb9ab3409bdea15f41c39bcaec549a4d4dbca89'
        v=pd.read_csv(io.BytesIO(raw))
    b=v[v.site_id.eq('CHAL')&v.count_type.eq('nests')&v.common_name.eq('adelie penguin')&v.penguin_count.notna()]
    uav_years=[2018,2021,2022,2023,2024,2025]
    # Metadata.docx verbatim corner coordinates, not a surveyed polygon crosswalk.
    lonlat={'NW':(170+14/60+2.56/3600,-(72+19/60+11.5/3600)),'SE':(170+13/60+57.54/3600,-(72+19/60+14/3600)),'SW':(170+13/60+55.52/3600,-(72+19/60+13.7/3600)),'NE':(170+14/60+24.36/3600,-(72+19/60+11.42/3600))}
    tr=Transformer.from_crs(4326,32759,always_xy=True);q={k:tr.transform(*p) for k,p in lonlat.items()};poly=Polygon([q[k] for k in ['NW','NE','SE','SW']]);bb=box(472940,1974587,474305,1975656)
    result={'status':'VEGETATION_SOURCE_VERIFIED_LOCAL_ANIMAL_LINK_UNRESOLVED','source_pins':PINS,'member_pins':MEMBER_PINS,'rights':rights,'vegetation':{'n_rows':len(x),'n_unique_grids':3458,'valid_by_year':{str(k):int(v) for k,v in w.sum().items()},'all_three_valid':int(w.all(axis=1).sum()),'pair_valid':{f'{a}-{b}':int((w[a]&w[b]).sum()) for a,b in [(1962,2004),(2004,2018),(1962,2018)]},'blank_is_missing_not_absence':True},'classification_QA':validation,'count_support':{'strict_count_years':a.season.astype(int).tolist(),'raw_v5_nest_rows':len(b),'raw_v5_nest_seasons':sorted(b.season_starting.unique().tolist()),'strict_vegetation_overlap':sorted(set(a.season)&set(years)),'raw_vegetation_overlap':sorted(set(b.season_starting)&set(years)),'raw_2018_count_records':[{'count':float(r.penguin_count),'method':r.vantage,'reference_id':re.search(r'id="([^"]+)"',r.reference).group(1)} for r in b[b.season_starting.eq(2018)].itertuples()],'strict_UAV_overlap':sorted(set(a.season)&set(uav_years)),'vegetation_UAV_overlap':sorted(set(years)&set(uav_years))},'geometry':{'published_bbox_EPSG32759':[472940,1974587,474305,1975656],'metadata_corners_lonlat':lonlat,'transformed_corners':q,'literal_corner_polygon_area_m2':poly.area,'literal_corner_polygon_in_published_bbox':bb.covers(poly),'literal_side_lengths_m':{a+'_'+b:float(np.linalg.norm(np.array(q[a])-q[b])) for a,b in [('NW','NE'),('NE','SE'),('SE','SW'),('SW','NW')]},'source_plot_grid_area_m2':3458,'verified_image_footprint':False,'verified_plot_georeference':False},'limits':['The literal corners enclose a polygon inconsistent with the described 120x30m local grid; do not use them for cell geolocation. Bounding rectangle is not valid imagery support.','Ground truth classifications are original author comparison, not independent UAV validation.','Exact same-season colony totals do not supply grid-level animal use; 2018 raw counts disagree. No missing-to-zero or averaging incompatible counts.','No joint plant-animal temporal coefficient, no causal claim.']}
    return result
if __name__=='__main__':
    result=run(Path(sys.argv[1]));Path(sys.argv[2]).write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
