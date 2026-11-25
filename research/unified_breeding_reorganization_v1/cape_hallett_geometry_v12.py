"""Authoritative geometry comparison; no inferred plot coordinates or nest locations."""
import json
from pathlib import Path
import numpy as np
from pyproj import Transformer
from shapely.geometry import Polygon, Point, box
T=Transformer.from_crs(4326,32759,always_xy=True)
coords={'NE':(-(72+19/60+11.219/3600),170+14/60+4.012/3600),'NW':(-(72+19/60+10.43/3600),170+13/60+58.341/3600),'SW':(-(72+19/60+14.479/3600),170+13/60+51.901/3600),'SE':(-(72+19/60+15.299/3600),170+13/60+57.338/3600)}
meta={'NW':(-(72+19/60+11.5/3600),170+14/60+2.56/3600),'SE':(-(72+19/60+14.0/3600),170+13/60+57.54/3600),'SW':(-(72+19/60+13.7/3600),170+13/60+55.52/3600),'NE':(-(72+19/60+11.42/3600),170+14/60+24.36/3600)}
q={k:np.array(T.transform(lon,lat)) for k,(lat,lon) in coords.items()};v={k:np.array(T.transform(lon,lat)) for k,(lat,lon) in meta.items()}
zone=Polygon([q[k] for k in ['NE','NW','SW','SE']]);plot=Polygon([v[k] for k in ['NE','NW','SW','SE']])
assert zone.is_valid and plot.is_valid
mark=np.array(T.transform(170+14/60+2.55/3600,-(72+19/60+11.37/3600)))
out={'status':'AUTHORITATIVE_ZONE_CONFIRMED_PLOT_GEOREFERENCE_UNRESOLVED','official_plan':'https://documents.ats.aq/recatt/att680_e.pdf','table':'Restricted Zone Table 3','original_plot_doi':'10.7488/ds/3417','crs':'EPSG:32759','official_zone_area_m2':zone.area,'literal_metadata_polygon_area_m2':plot.area,'grid_area_m2':3458,'intersection_m2':zone.intersection(plot).area,'literal_outside_zone_m2':plot.difference(zone).area,'official_side_lengths_m':{a+'_'+b:float(np.linalg.norm(q[b]-q[a])) for a,b in [('NE','NW'),('NW','SW'),('SW','SE'),('SE','NE')]},'metadata_corner_checks':{k:{'in_zone':zone.covers(Point(v[k])),'outside_distance_m':zone.distance(Point(v[k])),'distance_from_official_NE_marker_m':float(np.linalg.norm(mark-v[k]))} for k in v},'zone_inside_published_UAV_bbox':box(472940,1974587,474305,1975656).covers(zone),'plot_crosswalk_valid':False,'actual_UAV_common_footprint_valid':False,'limits':'Published corner labels conflict; no inferred correction, no new plot polygon or nest coordinates exported. Nominal zone is not observation support.'}
if __name__=='__main__':
    import sys
    Path(sys.argv[1]).write_text(json.dumps(out,indent=2)+'\n')
    print('GEOMETRY_RESULT='+json.dumps(out,separators=(',',':')))
