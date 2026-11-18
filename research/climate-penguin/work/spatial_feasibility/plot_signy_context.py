from pathlib import Path
import geopandas as gpd,pandas as pd,matplotlib.pyplot as plt
from matplotlib.patches import Patch
p=Path('outputs/spatial_feasibility')
d=pd.read_csv(p/'signy_gps_crosswalk.csv');g=gpd.GeoDataFrame(d,geometry=gpd.points_from_xy(d.longitude,d.latitude),crs=4326).to_crs(32723)
v=gpd.read_file('work/comparison_audit/vegetation/map/PlantarcticaVegetationMap.shp').to_crs(32723)
fig,axes=plt.subplots(2,3,figsize=(13,8));colors={'Vegetation':'#4b9b69','Lichen':'#c9a04b','Snow Algae':'#c96999'}
for ax,(name,pts) in zip(axes.flat,g.groupby('location',sort=False)):
 x,y=pts.geometry.x.mean(),pts.geometry.y.mean();sub=v.cx[x-180:x+180,y-180:y+180]
 for cls,col in colors.items():
  a=sub[sub.Vegetation==cls]
  if len(a):a.plot(ax=ax,color=col)
 ax.scatter(pts.geometry.x,pts.geometry.y,s=25,color='black',zorder=4)
 for j,(_,r) in enumerate(pts.iterrows()):ax.annotate(r.colony,(r.geometry.x,r.geometry.y),xytext=(6,6+(j%2)*9),textcoords='offset points',fontsize=8,zorder=5)
 ax.set_xlim(x-180,x+180);ax.set_ylim(y-180,y+180);ax.set_aspect('equal');ax.set_title(name);ax.ticklabel_format(style='plain',useOffset=False);ax.tick_params(labelsize=7)
 ax.plot([x-150,x-50],[y-150,y-150],color='black',lw=3);ax.text(x-100,y-138,'100 m',ha='center',fontsize=8)
axes.flat[-1].axis('off');axes.flat[-1].legend(handles=[Patch(facecolor=c,label=k) for k,c in colors.items()],loc='upper left')
axes.flat[-1].text(0,.55,'Dots: BAS colony reference GPS\nPolygons: Plantarctica 2017–2023 composite\nWhite: not mapped positive; NOT absence\nNo coastline, colony boundary or route inferred\nUTM 23S; panels 360 × 360 m',transform=axes.flat[-1].transAxes,fontsize=10,va='top')
fig.suptitle('Signy: verified colony GPS and mapped vegetation context',fontsize=15);fig.tight_layout(rect=[0,0,1,.95]);fig.savefig(p/'signy_vegetation_context.png',dpi=180);print('saved')
