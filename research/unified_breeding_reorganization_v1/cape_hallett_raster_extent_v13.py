"""Reproduce V13 geometric extent audit from verified downloaded receipt ZIP.
No pixels decoded, no cell positions inferred, no animal–plant fit.
"""
from pathlib import Path
from hashlib import sha256
import sys,json,zipfile
from pyproj import Transformer,Geod
from shapely.geometry import Polygon,Point
def audit(path):
    assert sha256(path.read_bytes()).hexdigest()=='e3880ab79bb8d0f36502a1ef3386ec3c971af63c1b740eeb4addd83799a2c97c'
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        raw=z.read('receipt.json')
    assert sha256(raw).hexdigest()=='19ca72f7100fc4d7b59ee4b5714645b98b80fcd24c6c5da48cda11a633958ffc'
    d=json.loads(raw);assert d['status']=='PUBLIC_GEOTIFF_METADATA_ACQUIRED'
    assert len(d['requests'])==90 and all(x['http']==206 for x in d['requests']) and d['bytes_received']==2949120
    T=Transformer.from_crs(4326,32759,always_xy=True)
    G=Geod(ellps='WGS84')
    # Literal ASPA 106 (2021) Table 3 zone and original plant metadata (V12).
    coords={'NE':(-(72+19/60+11.219/3600),170+14/60+4.012/3600),'NW':(-(72+19/60+10.43/3600),170+13/60+58.341/3600),'SW':(-(72+19/60+14.479/3600),170+13/60+51.901/3600),'SE':(-(72+19/60+15.299/3600),170+13/60+57.338/3600)}
    meta={'NW':(-(72+19/60+11.5/3600),170+14/60+2.56/3600),'SE':(-(72+19/60+14.0/3600),170+13/60+57.54/3600),'SW':(-(72+19/60+13.7/3600),170+13/60+55.52/3600),'NE':(-(72+19/60+11.42/3600),170+14/60+24.36/3600)}
    zone=Polygon([T.transform(coords[k][1],coords[k][0]) for k in ['NE','NW','SW','SE']])
    plot=Polygon([T.transform(meta[k][1],meta[k][0]) for k in ['NE','NW','SW','SE']])
    assert zone.is_valid and plot.is_valid
    p=d['first_page'];rows,cols,bands=p['shape'];sx,sy,_=p['geotags']['33550']
    i,j,k,lon,lat,z=p['geotags']['33922']
    assert (i,j,k)==(0,0,0) and p['geotiff_metadata']['GeographicTypeGeoKey']==4326 and p['geotiff_metadata']['GTRasterTypeGeoKey']==1
    west,north=lon,lat;east,south=lon+cols*sx,lat-rows*sy
    # Corner-transformed envelope in UTM, not alpha/valid observation footprint.
    raster=Polygon([T.transform(x,y) for x,y in [(west,north),(east,north),(east,south),(west,south)]])
    midlon,midlat=(west+east)/2,(north+south)/2
    out={'status':'PUBLIC_RASTER_ENVELOPE_VERIFIED_CELL_CROSSWALK_UNRESOLVED',
         'raster_dimensions_m':[G.inv(west,midlat,east,midlat)[2],G.inv(midlon,north,midlon,south)[2]],
         'pixel_size_mm_at_center':[G.inv(midlon,midlat,midlon+sx,midlat)[2]*1000,G.inv(midlon,midlat,midlon,midlat-sy)[2]*1000],
         'raster_envelope_area_m2':raster.area,
         'comparisons':{},'literal_NE_outside_envelope_m':raster.distance(Point(T.transform(meta['NE'][1],meta['NE'][0]))),
         'valid_pixel_footprint_verified':False,'grid_crosswalk_verified':False,'new_biological_effect_estimated':False}
    for name,poly in [('official_restricted_zone',zone),('literal_conflicting_plot',plot)]:
        overlap=raster.intersection(poly).area
        out['comparisons'][name]={'source_area_m2':poly.area,'intersection_m2':overlap,'intersection_fraction':overlap/poly.area,'covered':raster.covers(poly)}
    return out
if __name__=='__main__':
    print(json.dumps(audit(Path(sys.argv[1])),indent=2))
