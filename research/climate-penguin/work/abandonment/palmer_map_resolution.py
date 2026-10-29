"""Map-geometry pixel exclusion, not vegetation inference or plot validation.

A full square pixel of side s contains a disk of radius s/2. If even that disk
cannot fit in a map polygon, no rotation/phase of a full square pixel can fit.
The converse is NOT true. All geometry remains cartographic, not field-verified.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
import litchfield_map_alignment as base

TORG_SHA='89e2af9b2708e8eba05d0a5a46fcb34b6ca1ec763d57883cae91d40fb75aef6f'
TORG_URL='https://www.era.gs/projects/palmer/Map5-TorgersenIsland-v3.pdf'
# Closed perimeter strokes; hatching, contours, symbols and legend excluded.
TORG_PATHS=(12,43,65,76,100,151,178,193,202,222,233,249,281,306,
            325,379,398,409,426,448,469,482,506,519,534,551,563,572)
TORG_PROJ='+proj=lcc +lat_1=-64.76666666666667 +lat_2=-64.8 +lat_0=-64.76666666666667 +lon_0=-64.075 +datum=WGS84 +units=m +no_defs'
LONS={1784:-(64+4/60),1785:-(64+4/60+15/3600),
      1786:-(64+4/60+30/3600),1787:-(64+4/60+45/3600)}
LATS={1802:-(64+46/60+15/3600),1803:-(64+46/60+20/3600),
      1804:-(64+46/60+25/3600),1805:-(64+46/60+30/3600)}

def pixel_gate(poly, side, tolerance=0.001):
    from shapely import maximum_inscribed_circle
    if (poly.geom_type!='Polygon' or poly.is_empty or not poly.is_valid or
        not np.isfinite(side) or side<=0 or tolerance<=0):
        raise ValueError('valid nonempty polygon and positive pixel side required')
    radius=maximum_inscribed_circle(poly,tolerance=tolerance).length
    excluded=radius+tolerance<side/2
    return {'area_m2':float(poly.area),'pixel_side_m':float(side),
            'inscribed_radius_m_approx':float(radius),'algorithm_tolerance_m':tolerance,
            'ruled_out_by_disk':bool(excluded),'native_grid_verified':False,
            'decision':('ruled_out_for_unmixed_square_pixel' if excluded else
                        'not_ruled_out__native_grid_and_groundtruth_required')}

def bezier_value(item,t):
    if item[0]!='c':raise ValueError('Bezier expected')
    p=np.array([tuple(x) for x in item[1:]])
    return (1-t)**3*p[0]+3*(1-t)**2*t*p[1]+3*(1-t)*t*t*p[2]+t**3*p[3]

def curve_y_at_x(item,x):
    lo,hi=0.,1.
    for _ in range(55):
        t=(lo+hi)/2;p=bezier_value(item,t)
        if p[0]<x:lo=t
        else:hi=t
    return float(p[1])

def torgersen(pdf):
    import fitz
    from pyproj import Transformer
    from shapely.geometry import Polygon
    if hashlib.sha256(Path(pdf).read_bytes()).hexdigest()!=TORG_SHA:
        raise ValueError('source SHA mismatch; fixed drawing IDs unsafe')
    doc=fitz.open(pdf);ds=doc[0].get_drawings()
    project=Transformer.from_crs(4326,TORG_PROJ,always_xy=True)
    controls=[]
    for la,lat in LATS.items():
        for lo,lon in LONS.items():
            y=float(ds[la]['items'][0][1].y)
            for _ in range(5):
                x=base.curve_x_at_y(ds[lo]['items'][0],y)
                y=curve_y_at_x(ds[la]['items'][0],x)
            mx,my=project.transform(lon,lat)
            controls.append({'longitude':lon,'latitude':lat,'page_x':x,'page_y':y,'map_x':mx,'map_y':my})
    page=np.array([[r['page_x'],r['page_y']] for r in controls])
    meter=np.array([[r['map_x'],r['map_y']] for r in controls])
    affine,residual=base.fit_affine(page,meter)
    polys=[]
    for ident in TORG_PATHS:
        xy=base.closed_outline(ds[ident]['items']);m=np.c_[xy,np.ones(len(xy))]@affine
        g=Polygon(m)
        if not g.is_valid:raise ValueError(f'invalid polygon {ident}')
        polys.append((ident,g))
    return polys,controls,{'source_url':TORG_URL,'source_sha256':TORG_SHA,
        'map_publication_date':'2008-12-11','source_statement':'USGS orthophoto (2001) and Patterson (2001)',
        'exact_polygon_survey_dates':None,'census_code_crosswalk':False,
        'outline_count':len(polys),'control_points':len(controls),
        'graticule_fit_rmse_m':float(np.sqrt(np.mean(residual**2))),
        'graticule_fit_max_m':float(max(residual)),
        'projection_assumption':TORG_PROJ,
        'field_accuracy_established':False,
        'map_shapes_are_not_23_census_units':True}

def csv_write(path,rows):
    with Path(path).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    from pyproj import Transformer
    from shapely.geometry import shape,mapping
    from shapely.ops import transform
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--litchfield-geojson',type=Path,required=True)
    p.add_argument('--torgersen-pdf',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    lf=json.loads(a.litchfield_geojson.read_text())['features']
    if len(lf)!=10 or {f['properties']['path_index'] for f in lf}!=set(base.OUTLINE_IDS):
        raise ValueError('unexpected Litchfield candidate set')
    for f in lf:
        if f['properties']['geometry_status']!=base.GEOMETRY_STATUS:raise ValueError('geometry status lost')
    tr=Transformer.from_crs(4326,base.PROJ,always_xy=True)
    lp=[(f['properties']['path_index'],transform(tr.transform,shape(f['geometry']))) for f in lf]
    tp,control,meta=torgersen(a.torgersen_pdf)
    rows=[]
    for site,polys in [('LITC',lp),('TORG',tp)]:
        for ident,g in polys:
            for side in [10,30]:rows.append({'site_id':site,'path_index':ident,**pixel_gate(g,side)})
    summary=[]
    for site in ['LITC','TORG']:
        for side in [10,30]:
            q=[r for r in rows if r['site_id']==site and r['pixel_side_m']==side]
            summary.append({'site_id':site,'pixel_side_m':side,'map_outlines':len(q),
                'unmixed_pixel_geometrically_excluded':sum(r['ruled_out_by_disk'] for r in q),
                'not_excluded_but_unvalidated':sum(not r['ruled_out_by_disk'] for r in q),
                'area_m2_min':min(r['area_m2'] for r in q),'area_m2_max':max(r['area_m2'] for r in q),
                'radius_m_max':max(r['inscribed_radius_m_approx'] for r in q)})
    inv=Transformer.from_crs(TORG_PROJ,4326,always_xy=True)
    features=[{'type':'Feature','properties':{'source_path_index':ident,
        'geometry_status':'cartographic_candidate_not_field_verified','source_map_date':'2008-12-11',
        'exact_survey_year':None,'census_code':None,'extinct_or_active':None,
        'area_m2':g.area},'geometry':mapping(transform(inv.transform,g))} for ident,g in tp]
    result={'schema':1,'status':'postexploration_geometric_observation_gate_not_ecological_effect',
        'litchfield_geometry_sha256':hashlib.sha256(a.litchfield_geojson.read_bytes()).hexdigest(),
        'torgersen':meta,'summaries':summary,
        'limits':['Map outlines are generalized and not complete verified historical occupancy.',
          'Disk criterion rules out a full unmixed square pixel; passing it does NOT establish a fitting square.',
          'A native pixel response/PSF can mix surroundings even when its nominal footprint fits.',
          'Cannot infer plant absence, greening, extinction years, independent island replication or nutrient mechanism.',
          'Subpixel or multi-patch aggregation requires a different estimand and independently validated model.']}
    (a.out/'resolution_gate_result.json').write_text(json.dumps(result,indent=2)+'\n')
    (a.out/'torgersen_map_candidates.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features},separators=(',',':'))+'\n')
    csv_write(a.out/'map_pixel_resolution.csv',rows);csv_write(a.out/'torgersen_map_controls.csv',control)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
