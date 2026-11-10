"""Georeference published map outlines to diagnose registered-point misalignment.

Map-derived outlines are historical candidates, NOT survey-verified colony
polygons, census IDs, or a vegetation response. No reflectance is selected.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import numpy as np

SOURCE_SHA='4df88154c34fbb41b278e6d0543b37caad7c2dcaa080c57392aa9d4ce1a256a2'
SOURCE_URL='https://www.era.gs/projects/palmer/Map7-LitchfieldIsland-v3.pdf'
GEOMETRY_STATUS='map_derived_historical_candidate_not_survey_verified'
# Hand-identified outline paths, visually checked against the source map legend.
# Other thin diagonal paths are clipped hatching, not additional polygons.
OUTLINE_IDS=(87,93,100,107,118,128,140,151,160,171)
LON_PATHS={2400:-(64+6/60+20/3600),2399:-(64+6/60),
           2398:-(64+5/60+40/3600),2397:-(64+5/60+20/3600),2396:-(64+5/60)}
LAT_PATHS={2401:-(64+46/60),2402:-(64+46/60+10/3600),2403:-(64+46/60+20/3600)}
# Source reports local USGS LIT1 datum on WGS84 ellipsoid. Using WGS84 geographic
# coordinates is a diagnostic assumption; it is NOT a solved local datum shift.
PROJ='+proj=lcc +lat_1=-64.76666666666667 +lat_2=-64.8 +lat_0=-64.76666666666667 +lon_0=-64.1 +datum=WGS84 +units=m +no_defs'

def verify_source(path: Path) -> None:
    if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=SOURCE_SHA:
        raise ValueError('source SHA differs; drawing IDs cannot be reused')

def fit_affine(page_xy, metric_xy):
    a=np.asarray(page_xy,dtype=float);b=np.asarray(metric_xy,dtype=float)
    if a.shape!=b.shape or a.ndim!=2 or a.shape[1]!=2:
        raise ValueError('paired 2D coordinates required')
    x=np.column_stack([a,np.ones(len(a))])
    if len(a)<3 or not np.isfinite(x).all() or not np.isfinite(b).all() or np.linalg.matrix_rank(x)<3:
        raise ValueError('noncollinear finite control points required')
    c=np.linalg.lstsq(x,b,rcond=None)[0]
    return c,np.linalg.norm(x@c-b,axis=1)

def closed_outline(items):
    vertices=[]
    for it in items:
        if it[0]!='l':raise ValueError('outline is not a line chain')
        p,q=np.asarray(it[1],float),np.asarray(it[2],float)
        if vertices and not np.allclose(vertices[-1],p,atol=1e-3,rtol=0):
            raise ValueError('discontinuous outline')
        if not vertices:vertices.append(p)
        vertices.append(q)
    if len(vertices)<4 or not np.allclose(vertices[0],vertices[-1],atol=1e-3,rtol=0):
        raise ValueError('open hatch/path cannot be a footprint')
    return np.asarray(vertices)

def curve_x_at_y(item,y):
    if item[0]!='c':raise ValueError('expected source graticule Bezier')
    pts=np.array([tuple(v) for v in item[1:]])
    lo,hi=0.,1.
    for _ in range(60):
        t=(lo+hi)/2
        p=(1-t)**3*pts[0]+3*(1-t)**2*t*pts[1]+3*(1-t)*t*t*pts[2]+t**3*pts[3]
        if p[1]>y:lo=t
        else:hi=t
    return float(p[0])

def write_csv(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def analyze(pdf:Path,out:Path):
    import fitz
    from pyproj import Transformer
    from shapely.geometry import Polygon,Point,mapping
    from shapely.ops import unary_union
    verify_source(pdf);out.mkdir(parents=True,exist_ok=True)
    doc=fitz.open(pdf);page=doc[0];draws=page.get_drawings()
    to_map=Transformer.from_crs(4326,PROJ,always_xy=True)
    to_geo=Transformer.from_crs(PROJ,4326,always_xy=True)
    to_polar=Transformer.from_crs(4326,3031,always_xy=True)
    from_polar=Transformer.from_crs(3031,PROJ,always_xy=True)
    controls=[]
    for lat_id,lat in LAT_PATHS.items():
        y=float(draws[lat_id]['items'][0][1].y)
        for lon_id,lon in LON_PATHS.items():
            x=curve_x_at_y(draws[lon_id]['items'][0],y);mx,my=to_map.transform(lon,lat)
            controls.append(dict(longitude=lon,latitude=lat,page_x=x,page_y=y,map_x=mx,map_y=my))
    px=np.array([[c['page_x'],c['page_y']] for c in controls]);mx=np.array([[c['map_x'],c['map_y']] for c in controls])
    affine,residual=fit_affine(px,mx)
    loo=[]
    for i in range(len(px)):
        keep=np.arange(len(px))!=i;c,_=fit_affine(px[keep],mx[keep])
        loo.append(float(np.linalg.norm(np.r_[px[i],1]@c-mx[i])))
    polys=[];features=[];summary=[]
    for i in OUTLINE_IDS:
        coords=closed_outline(draws[i]['items'])
        metric=np.column_stack([coords,np.ones(len(coords))])@affine
        poly=Polygon(metric)
        if not poly.is_valid or poly.area<=0:raise ValueError(f'invalid map path {i}')
        polys.append(poly)
        ll=np.column_stack(to_geo.transform(metric[:,0],metric[:,1]));lon,lat=to_geo.transform(poly.centroid.x,poly.centroid.y)
        attrs={'path_index':i,'source_map_date':'2009-02-06','geometry_status':GEOMETRY_STATUS,
               'census_code':None,'exact_observation_year':None,'derived_area_m2':poly.area}
        features.append({'type':'Feature','properties':attrs,'geometry':mapping(Polygon(ll))})
        summary.append({'path_index':i,'centroid_lon':lon,'centroid_lat':lat,'map_area_m2':poly.area})
    union=unary_union(polys);center=to_map.transform(-64.0919,-64.7708)
    polar=to_polar.transform(-64.0919,-64.7708)
    probes=[];selected={9,11,15,16,20,22,23}
    for j,(dx,dy) in enumerate((x,y) for x in (-80,-40,0,40,80) for y in (-80,-40,0,40,80)):
        x,y=from_polar.transform(polar[0]+dx,polar[1]+dy)
        lon,lat=to_geo.transform(x,y);p=Point(x,y)
        probes.append({'grid_position':j,'offset_x_m':dx,'offset_y_m':dy,'longitude':lon,'latitude':lat,
                       'selected_spectral_pair':j in selected,'inside_map_outline':union.covers(p),
                       'nearest_map_outline_m':p.distance(union)})
    boundary=Polygon([from_polar.transform(polar[0]+dx,polar[1]+dy) for dx,dy in [(-80,-80),(-80,80),(80,80),(80,-80)]])
    r={'schema':1,'source_url':SOURCE_URL,'source_pdf_sha256':SOURCE_SHA,'source_map_date':'2009-02-06',
       'source_run':40872056244,'source_artifact':12895339559,
       'geometry_status':GEOMETRY_STATUS,'map_projection':PROJ,'outlines':len(polys),
       'drawings_total':len(draws),'control_intersections':len(controls),
       'affine_page_to_map':affine.tolist(),'graticule_fit_rmse_m':float(np.sqrt(np.mean(residual**2))),
       'graticule_fit_max_m':float(max(residual)),'graticule_leave_one_control_max_m':max(loo),
       'derived_outline_area_total_m2':union.area,'derived_outline_area_min_m2':min(p.area for p in polys),
       'derived_outline_area_max_m2':max(p.area for p in polys),
       'registration_point_lon_lat':[-64.0919,-64.7708],
       'registration_point_distance_to_nearest_map_outline_m':Point(center).distance(union),
       'probe_grid_inside_mapped_outlines':sum(p['inside_map_outline'] for p in probes),
       'probe_grid_nearest_outline_min_m':min(p['nearest_map_outline_m'] for p in probes),
       'probe_grid_nearest_outline_max_m':max(p['nearest_map_outline_m'] for p in probes),
       'spectral_selected_positions':sorted(selected),
       'spectral_selected_inside_mapped_outlines':sum(p['inside_map_outline'] for p in probes if p['selected_spectral_pair']),
       'spectral_selected_nearest_outline_min_m':min(p['nearest_map_outline_m'] for p in probes if p['selected_spectral_pair']),
       'grid_envelope_distance_to_outline_m':boundary.distance(union),
       'grid_envelope_intersection_area_m2':boundary.intersection(union).area,
       'field_georeferencing_accuracy_established':False,'census_code_crosswalk_established':False,
       'vegetation_effect_estimated':False,
       'limits':['Fit residuals measure internal graticule consistency, NOT field-position accuracy.',
                 'WGS84 geographic coordinates versus source local USGS LIT1 datum: unsolved datum offset.',
                 'Published cartographic footprint outlines are generalized; exact survey dates and census-code linkage absent.',
                 'Ten drawn shapes are not ten independent colonies or ten census units.',
                 'Probe points are outside the mapped shapes; no claim about complete unmapped historical occupancy.',
                 'Neither NDVI sign nor green pixels selected the source or these map outlines.']}
    # Independent linear lon/lat fit is a secondary arithmetic check only.
    llfit=np.linalg.lstsq(np.column_stack([px,np.ones(len(px))]),
                         np.array([[c['longitude'],c['latitude']] for c in controls]),rcond=None)[0]
    center_page=(np.array(center)-affine[2])@np.linalg.inv(affine[:2])
    lonlat=np.r_[center_page,1]@llfit
    r['independent_lonlat_affine_registration_check_m']=float(np.linalg.norm(np.array(to_map.transform(*lonlat))-center))
    r['pixel_interpretation']={'Landsat_pixel_area_m2':900,
        'minimum_outline_fraction_of_one_Landsat_pixel_area':r['derived_outline_area_min_m2']/900,
        'maximum_outline_fraction_of_one_Landsat_pixel_area':r['derived_outline_area_max_m2']/900,
        'area_fraction_is_not_observable_unmixed_pixel_count':True}
    r['source_archive_sha256']='974190c687b7e4493c3b8d33d2e80d11cc6c5849c39ab86654272177a52adcc7'
    (out/'map_alignment_result.json').write_text(json.dumps(r,indent=2)+'\n')
    (out/'litchfield_map_derived_candidates.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features},separators=(',',':'))+'\n')
    write_csv(out/'map_graticule_controls.csv',controls);write_csv(out/'map_derived_outlines.csv',summary);write_csv(out/'original_probe_alignment.csv',probes)
    print(json.dumps(r,indent=2))
    return r

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--pdf',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();analyze(a.pdf,a.out)
