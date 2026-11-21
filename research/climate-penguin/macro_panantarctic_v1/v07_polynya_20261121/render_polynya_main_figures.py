#!/usr/bin/env python3
"""Render five author-review polynya figures from verified numerical sources.

No ecological regressions, interval estimates, searches, or new sample selections
are performed. Coefficients, uncertainty intervals, leave-region-out estimates,
and residual-variation fractions are read from the verified source artifacts.
Figure 2 additionally reads the separately disclosed 2026-11-21 informative-
eight-region covariance sensitivity performed by the manuscript verifier.
Only the specified 439-row join, descriptive site means, map geometry, and the
already reported site + region-by-season residualization are recomputed.

Usage (from this directory):
  python render_polynya_main_figures.py
Optional first-render projection fallback when pyproj is in another runtime:
  python render_polynya_main_figures.py --projection-python /usr/bin/python3
After the first render, the verified site and Antarctic-land coordinate caches
permit offline rerender without pyproj. Every input is checked against
source_manifest.json. The land outline is display context, never an analysis mask.
Use --figure1-only to update the map without rewriting Figures 2–5.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon
from matplotlib.text import Text
from PIL import Image

HERE = Path(__file__).resolve().parent
P = "direct_DEEPAA_coastal_polynya_fraction"
S = "GLORYS_NovFeb_salinity"
WIDTH_MM = 170.0
MIN_TIFF_DPI = 800
# A 170-mm canvas cannot be exactly represented by integer pixels at 800 dpi.
# Rounding UP gives 5355 px at 800.1 dpi, retaining exactly 170 mm and >=800 dpi.
TIFF_WIDTH_PX = math.ceil(WIDTH_MM / 25.4 * MIN_TIFF_DPI)
TIFF_DPI = TIFF_WIDTH_PX / (WIDTH_MM / 25.4)
INK = "#253449"
BLUE = "#34658D"
TEAL = "#287D78"
ORANGE = "#B46D48"
GREY = "#86929A"
LIGHT = "#E4E9EC"
PALE = "#F2F5F6"
LAND_SOURCE_SHA256 = "9e0729ee253ca7d7a5c4ae9395fb1902264c5377c52e224d13dd85010e2835d9"
LAND_SOURCE_GIT_BLOB = "04811d72fff2701ec67587e30ad8942675b511e3"
STEMS = [
    "Fig1_Polynya_source_footprint",
    "Fig2_Polynya_association_and_sensitivity",
    "Fig3_Preceding_following_winter_contrast",
    "Fig4_Polynya_salinity_conditional_information",
    "Fig5_Observation_and_unresolved_pathways",
]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def verify_inputs(base):
    manifest = json.loads((base / "source_manifest.json").read_text())
    for rec in manifest["inputs"]:
        path = base / rec["local_file"]
        if sha256(path) != rec["sha256"]:
            raise ValueError(f"Frozen input digest changed: {path}")
    return manifest


def project_two_fe(v, site, region_season):
    """Exact frozen alternating-demeaning algorithm, not a new fitted model."""
    x = np.asarray(v, dtype=float).copy()
    ids = pd.Series(site).reset_index(drop=True)
    groups = pd.Series(region_season).reset_index(drop=True)
    for k in range(3000):
        before = x.copy()
        x -= pd.Series(x).groupby(ids, sort=False).transform("mean").to_numpy()
        x -= pd.Series(x).groupby(groups, sort=False).transform("mean").to_numpy()
        if np.max(np.abs(x - before)) < 1e-10:
            break
    max_site_mean = float(np.max(np.abs(pd.Series(x).groupby(ids).mean())))
    max_region_season_mean = float(np.max(np.abs(pd.Series(x).groupby(groups).mean())))
    if max(max_site_mean, max_region_season_mean) > 1e-7:
        raise ValueError("Frozen two-way FE projection did not converge")
    return x, {"iterations": k + 1, "max_abs_site_mean": max_site_mean,
               "max_abs_region_season_mean": max_region_season_mean}


PROJECTION_PROGRAM = r'''
import json,sys
import pyproj
from pyproj import Transformer, Geod
d=json.load(sys.stdin)
tr=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
geod=Geod(ellps="WGS84")
rows=[]
for r in d["sites"]:
    x,y=tr.transform(r["colony_lon"],r["colony_lat"])
    points=[]
    for bearing in range(0,361,6):
        lon,lat,_=geod.fwd(r["colony_lon"],r["colony_lat"],bearing,100000.)
        xx,yy=tr.transform(lon,lat)
        points.append([xx/1e6,yy/1e6])
    rows.append({"site_id":r["site_id"],"x_1000km":x/1e6,"y_1000km":y/1e6,
                 "support_radius_km":100,"support_circle":points})
graticules={}
for lat in [-60,-70,-80]:
    graticules[str(lat)]=[[xx/1e6,yy/1e6] for xx,yy in
      [tr.transform(float(lon),lat) for lon in range(-180,181,2)]]
lo1,la1,_=geod.fwd(0,-70,270,500000.)
lo2,la2,_=geod.fwd(0,-70,90,500000.)
x1,y1=tr.transform(lo1,la1);x2,y2=tr.transform(lo2,la2)
_,_,distance=geod.inv(lo1,la1,lo2,la2)
print(json.dumps({"projection":"EPSG:3031","ellipsoid":"WGS84",
 "pyproj_version":pyproj.__version__,"input_digest":d["input_digest"],
 "sites":rows,"graticules":graticules,
 "scale_bar":{"geodesic_distance_m":distance,"reference_center_latitude_deg":-70,
              "projected_length_1000km":abs(x2-x1)/1e6,
              "meaning":"Projected chord joining endpoints of a 1000-km WGS84 geodesic centered at 70 S, oriented east-west at its midpoint."}}))
'''


def map_geometry(base, sites, projection_python):
    payload_sites = sites[["site_id", "colony_lon", "colony_lat"]].sort_values("site_id")
    input_digest = hashlib.sha256(payload_sites.to_csv(index=False).encode()).hexdigest()
    target = base / "source_inputs/map_geometry.json"
    if target.exists():
        g = json.loads(target.read_text())
        if g["input_digest"] != input_digest:
            raise ValueError("Map geometry cache disagrees with the frozen 85-site input")
        return g
    payload = json.dumps({"sites": payload_sites.to_dict("records"), "input_digest": input_digest})
    candidates = list(dict.fromkeys([projection_python, sys.executable, "/usr/bin/python3"]))
    failures = []
    for interpreter in candidates:
        if not interpreter:
            continue
        result = subprocess.run([interpreter, "-c", PROJECTION_PROGRAM], input=payload,
                                text=True, capture_output=True)
        if result.returncode == 0:
            g = json.loads(result.stdout)
            if abs(g["scale_bar"]["geodesic_distance_m"] - 1_000_000) > 1e-6:
                raise ValueError("Scale bar is not a 1000-km WGS84 geodesic")
            write_json(target, g)
            return g
        failures.append(f"{interpreter}: {result.stderr.strip().splitlines()[-1]}")
    raise RuntimeError("Provide --projection-python with pyproj installed; " + "; ".join(failures))


LAND_PROJECTION_PROGRAM = r'''
import json,sys
import pyproj
from pyproj import Transformer
d=json.load(sys.stdin)
tr=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
polygons=[]
omitted=[]
for i,feature in enumerate(d["geojson"]["features"]):
    geometry=feature["geometry"]
    parts=geometry["coordinates"] if geometry["type"]=="MultiPolygon" else [geometry["coordinates"]]
    for j,polygon in enumerate(parts):
        if max(p[1] for ring in polygon for p in ring)>-60:
            continue
        if len(polygon)!=1:
            raise ValueError("Pinned Antarctic land unexpectedly contains polygon holes")
        ring=[]
        for k,(lon,lat) in enumerate(polygon[0]):
            # Geographic antimeridian closure vertices are not coastline.
            # At the South Pole they create a false inland line after projection.
            if lat==-90 and abs(lon)==180:
                omitted.append({"feature_index":i,"polygon_index":j,"vertex_index":k,
                                "longitude":lon,"latitude":lat})
                continue
            x,y=tr.transform(lon,lat)
            ring.append([x/1e6,y/1e6])
        polygons.append({"feature_index":i,"polygon_index":j,"xy_1000km":ring})
if [p["feature_index"] for p in polygons]!=list(range(8)) or len(omitted)!=2:
    raise ValueError("Pinned Antarctic-land selection changed")
meridians={}
for lon in [-180,-90,0,90]:
    meridians[str(lon)]=[[x/1e6,y/1e6] for x,y in
                       [tr.transform(lon,lat) for lat in range(-90,-59)]]
print(json.dumps({"source_sha256":d["source_sha256"],"source_git_blob":d["source_git_blob"],
 "projection":"EPSG:3031","ellipsoid":"WGS84","pyproj_version":pyproj.__version__,
 "selection":"All vertices at or south of 60 degrees S; exactly source features 0–7; no geographic clipping.",
 "display_only":True,"polygons":polygons,"meridians":meridians,
 "omitted_synthetic_pole_cap_vertices":omitted,
 "seam_handling":"Omit the two exact +/-180 longitude, -90 latitude antimeridian-cap vertices from display geometry only. Adjacent +/-180, -84.71338 coastline endpoints coincide in EPSG:3031; no inland seam is stroked.",
 "meaning":"Generalized Natural Earth 1:110m land outline, not a precise coastline, ice-shelf or polynya boundary, exposure mask, or source of colony coordinates."}))
'''


def antarctic_land_geometry(base, projection_python):
    source = base / "source_inputs/ne_110m_land.geojson"
    if sha256(source) != LAND_SOURCE_SHA256:
        raise ValueError("Pinned Natural Earth land source changed")
    raw = source.read_bytes()
    git_blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if git_blob != LAND_SOURCE_GIT_BLOB:
        raise ValueError("Natural Earth Git blob identity changed")
    target = base / "source_inputs/antarctic_land_EPSG3031.json"
    if target.exists():
        g = json.loads(target.read_text())
        if g["source_sha256"] != LAND_SOURCE_SHA256 or g["source_git_blob"] != git_blob:
            raise ValueError("Antarctic display cache disagrees with its pinned source")
        return g
    payload = json.dumps({"geojson": json.loads(raw), "source_sha256": LAND_SOURCE_SHA256,
                          "source_git_blob": git_blob})
    failures = []
    for interpreter in dict.fromkeys([projection_python, sys.executable, "/usr/bin/python3"]):
        if not interpreter:
            continue
        result = subprocess.run([interpreter, "-c", LAND_PROJECTION_PROGRAM], input=payload,
                                text=True, capture_output=True)
        if result.returncode == 0:
            g = json.loads(result.stdout)
            write_json(target, g)
            return g
        failures.append(f"{interpreter}: {result.stderr.strip().splitlines()[-1]}")
    raise RuntimeError("Provide --projection-python with pyproj installed; " + "; ".join(failures))


def save_figure(fig, out, name, receipt):
    """Fixed physical canvas; never tight-crop the publication dimensions."""
    for ax in fig.axes:
        if not ax.axison:
            ax.set_xticks([])
            ax.set_yticks([])
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    # Matplotlib retains locator ticks outside the visible axis range, although
    # those ticks are not drawn. Exclude those objects from canvas-bound QA.
    hidden_tick_texts = set()
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            lo, hi = sorted(axis.get_view_interval())
            for tick in axis.get_major_ticks() + axis.get_minor_ticks():
                if not ax.axison or not axis.get_visible() or not (lo-1e-9 <= tick.get_loc() <= hi+1e-9):
                    hidden_tick_texts.update([tick.label1, tick.label2])
    texts = [t for t in fig.findobj(Text) if t not in hidden_tick_texts and t.get_visible() and t.get_text().strip()]
    small = [(t.get_text(), t.get_fontsize()) for t in texts if t.get_fontsize() < 8 - 1e-9]
    if small:
        raise ValueError(f"Text smaller than 8 pt in {name}: {small}")
    # Check text bounds rather than treating a successful save as visual QA.
    box = fig.bbox
    clipped = []
    for t in texts:
        b = t.get_window_extent(renderer)
        if b.x0 < box.x0 - 1 or b.x1 > box.x1 + 1 or b.y0 < box.y0 - 1 or b.y1 > box.y1 + 1:
            clipped.append(t.get_text())
    if clipped:
        raise ValueError(f"Text outside the {WIDTH_MM}-mm canvas in {name}: {clipped}")
    fig.savefig(out / (name + ".svg"), facecolor="white")
    fig.savefig(out / (name + ".png"), dpi=300, facecolor="white")
    buff = io.BytesIO()
    fig.savefig(buff, format="png", dpi=TIFF_DPI, facecolor="white")
    buff.seek(0)
    with Image.open(buff) as rendered:
        cmyk = rendered.convert("RGB").convert("CMYK")
        if cmyk.width != TIFF_WIDTH_PX:
            raise ValueError(f"Raster width drift: {cmyk.width} != {TIFF_WIDTH_PX}")
        cmyk.save(out / (name + ".tif"), compression="tiff_lzw", dpi=(TIFF_DPI, TIFF_DPI))
        pixels = [cmyk.width, cmyk.height]
    receipt.append({"stem": name, "width_mm": WIDTH_MM,
                    "height_mm": float(fig.get_size_inches()[1] * 25.4),
                    "minimum_text_pt": min(float(t.get_fontsize()) for t in texts),
                    "tiff_pixels": pixels, "tiff_dpi": TIFF_DPI, "tiff_mode": "CMYK",
                    "tiff_compression": "LZW", "svg_editable_text": True,
                    "outside_canvas_text_count": 0})
    plt.close(fig)


def new_figure(height_mm):
    return plt.figure(figsize=(WIDTH_MM / 25.4, height_mm / 25.4), facecolor="white")


def title(ax, s):
    ax.set_title(s, loc="left", fontsize=10, fontweight="bold", pad=8)


def coefficient_point(ax, beta, lo, hi, y, color, marker="o", size=33):
    ax.plot([lo, hi], [y, y], color=color, lw=1.5, solid_capstyle="round", zorder=2)
    ax.plot([lo, lo], [y - .065, y + .065], color=color, lw=1.0, zorder=2)
    ax.plot([hi, hi], [y - .065, y + .065], color=color, lw=1.0, zorder=2)
    ax.scatter([beta], [y], s=size, color=color, marker=marker, edgecolors="white", linewidths=.4, zorder=3)


def figure1(sites, region_support, geo, land, out, receipt):
    fig = new_figure(133)
    ax = fig.add_axes([.035, .205, .55, .70])
    title(ax, "a   Exposure and spatial support")
    for polygon in land["polygons"]:
        ax.add_patch(Polygon(polygon["xy_1000km"], closed=True, facecolor="#E9ECE9",
                             edgecolor="#A1ADA9", linewidth=.65, zorder=-2))
    for points in land["meridians"].values():
        xy = np.asarray(points)
        ax.plot(xy[:, 0], xy[:, 1], ls=":", color="#B8C2C8", lw=.55, zorder=-1)
    for xx, yy, label, ha, va in [(-.15, 3.48, "0°", "right", "center"),
                                 (-3.48, 0, "90°W", "left", "center"),
                                 (3.48, 0, "90°E", "right", "center")]:
        ax.text(xx, yy, label, fontsize=8, color=GREY, ha=ha, va=va,
                bbox={"facecolor":"white", "edgecolor":"none", "pad":.15, "alpha":.9})
    for lat, points in geo["graticules"].items():
        xy = np.asarray(points)
        ax.plot(xy[:, 0], xy[:, 1], ls=":", color="#B8C2C8", lw=.65, zorder=0)
        ax.text(.26 if int(lat)==-60 else .08, float(xy[:, 1].max()) + .035,
                f"{abs(int(lat))}°S", fontsize=8, color=GREY)
    gl = {g["site_id"]: g for g in geo["sites"]}
    for r in sites.itertuples(index=False):
        points = np.asarray(gl[r.site_id]["support_circle"])
        ax.plot(points[:, 0], points[:, 1], color="#8EACB8", lw=.35, alpha=.5, zorder=1)
    x = [gl[s]["x_1000km"] for s in sites.site_id]
    y = [gl[s]["y_1000km"] for s in sites.site_id]
    scatter = ax.scatter(x, y, c=sites.mean_polynya_percent, vmin=0, vmax=22,
                         cmap="viridis", s=22, linewidths=.3, edgecolors="white", zorder=3)
    ax.set_aspect("equal"); ax.set_xlim(-3.6, 3.6); ax.set_ylim(-3.6, 3.6); ax.axis("off")
    anchors = {
        "Adelie Land": (2.5, -2.40), "Enderby Land": (2.42, 2.22),
        "Mac. Robertson Land": (3.05, 1.82), "Marie Byrd Land": (-2.62, -1.30),
        "Northeast Antarctic Peninsula": (-3.27, 2.14), "Palmer Land": (-2.75, -.20),
        "Princess Elizabeth Land": (3.17, .85), "Queen Mary Land": (3.21, -.25),
        "Southwest Antarctic Peninsula": (-3.18, .88), "Victoria Land": (.40, -2.50),
        "Wilkes Land": (3.11, -1.33),
    }
    for j, region in enumerate(region_support.source_region):
        sub = sites.loc[sites.source_region.eq(region)]
        mx = np.mean([gl[s]["x_1000km"] for s in sub.site_id])
        my = np.mean([gl[s]["y_1000km"] for s in sub.site_id])
        ax.annotate(chr(65+j), xy=(mx, my), xytext=anchors[region], ha="center", va="center",
                    fontsize=8.5, color=INK, fontweight="bold",
                    arrowprops={"arrowstyle":"-", "color":GREY, "lw":.55}, zorder=4,
                    bbox={"facecolor":"white", "edgecolor":"none", "pad":.7, "alpha":.9})
    length = geo["scale_bar"]["projected_length_1000km"]
    x0, y0 = -.5*length, -3.08
    ax.plot([x0, x0+length], [y0, y0], color=INK, lw=1.5)
    ax.plot([x0, x0], [y0-.06, y0+.06], color=INK, lw=1)
    ax.plot([x0+length, x0+length], [y0-.06, y0+.06], color=INK, lw=1)
    ax.text(0, y0-.16, "1000 km · centred at 70°S", ha="center", va="top", fontsize=8)
    cax = fig.add_axes([.07, .155, .48, .024])
    cb = fig.colorbar(scatter, cax=cax, orientation="horizontal", ticks=[0,5,10,15,20])
    cb.set_label("Mean winter coastal-polynya area fraction (%)", fontsize=8.3, labelpad=4)
    cb.ax.tick_params(labelsize=8, length=2)
    tx = fig.add_axes([.625, .245, .36, .67]); tx.axis("off")
    title(tx, "b   Matched observations")
    tx.text(0, .93, "Region", fontsize=8, color=GREY)
    tx.text(.77, .93, "Sites", ha="center", fontsize=8, color=GREY)
    tx.text(.98, .93, "Rows", ha="right", fontsize=8, color=GREY)
    labels = {"Northeast Antarctic Peninsula":"NE Antarctic Peninsula",
              "Southwest Antarctic Peninsula":"SW Antarctic Peninsula", "Adelie Land":"Adélie Land"}
    for j, r in enumerate(region_support.itertuples(index=False)):
        yy = .862-j*.069
        tx.text(0, yy, f"{chr(65+j)}  {labels.get(r.source_region,r.source_region)}", fontsize=8)
        tx.text(.77, yy, str(int(r.n_original_sites)), ha="center", fontsize=8)
        tx.text(.98, yy, str(int(r.n_observations)), ha="right", fontsize=8)
    tx.text(0, .045, "Circles: 100 km geodesic support.\nThey are sampling footprints.", fontsize=8, linespacing=1.5)
    fig.text(.04, .063, "439 colony-seasons · 85 sites · 11 regions · 2004–2010", fontsize=9, fontweight="bold")
    fig.text(.04, .035, "Colours average each site's available matched June–October winters; EPSG:3031.", fontsize=8)
    fig.text(.04, .011, "Pale land: Natural Earth 1:110m; generalized geographic context only.", fontsize=8, color=GREY)
    save_figure(fig, out, STEMS[0], receipt)


def figure2(effects, leaves, out, receipt):
    fig = new_figure(167)
    a = fig.add_axes([.36, .645, .60, .285])
    title(a, "a   Association and calibration sensitivity")
    ys = np.array([3.4, 2.7, 1.3, .6])
    for y, r in zip(ys, effects.itertuples(index=False)):
        color = BLUE if r.model == "M_P" else TEAL
        coefficient_point(a, r.beta_per_10pp, r.lower, r.upper, y, color,
                          marker="o" if r.measurement == "Original single PLSR" else "s")
    a.set_yticks(ys, ["M_P · original single PLSR", "M_P · author R1,000", 
                     "M_SP · original single PLSR", "M_SP · author R1,000"], fontsize=8.5)
    a.set_ylim(-.05, 4.15); a.set_xlim(-1.65, .08)
    a.axvline(0, color=GREY, lw=.9, ls="--")
    a.grid(axis="x", color=LIGHT, lw=.6)
    fig.text(.04, .595, "M_P adjusts for image timing, summer sea ice and temperature; M_SP also includes salinity.\nIntervals use 425 informative rows / 82 sites / 8 regions; the 439-row coefficients are unchanged.",
             fontsize=8, linespacing=1.6, va="top")
    b = fig.add_axes([.36, .13, .60, .365])
    title(b, "b   Omit one reporting region at a time")
    regions = list(dict.fromkeys(leaves.omitted_original_region))
    for j, region in enumerate(regions):
        for model, dy, color, marker in [("M_P",-.12,BLUE,"o"),("M_SP",.12,TEAL,"s")]:
            value = leaves.loc[leaves.omitted_original_region.eq(region)&leaves.model.eq(model),"beta_per_10pp"].iloc[0]
            b.scatter([value], [j+dy], s=23, color=color, marker=marker, zorder=3)
    display = {"Northeast Antarctic Peninsula":"NE Antarctic Peninsula", "Southwest Antarctic Peninsula":"SW Antarctic Peninsula", "Adelie Land":"Adélie Land"}
    b.set_yticks(range(len(regions)), [display.get(r,r) for r in regions], fontsize=8.2)
    b.set_ylim(len(regions)-.4, -.7); b.set_xlim(-1.65, .08)
    b.axvline(0, color=GREY, ls="--", lw=.9); b.grid(axis="x", color=LIGHT, lw=.6)
    b.set_xlabel("Optical δ¹⁵N proxy difference (‰) per 10 percentage points", fontsize=8.3)
    b.legend(handles=[Line2D([],[],marker="o",color=BLUE,lw=0,label="M_P"),
                      Line2D([],[],marker="s",color=TEAL,lw=0,label="M_SP")],
             loc="upper right", frameon=False, fontsize=8, handletextpad=.3)
    fig.text(.04, .057, "Panel a: 8-region t(7) 95% intervals, covariance sensitivity dated 2026-11-21. Same historical images.", fontsize=8)
    fig.text(.04, .027, "Panel b: point estimates only; all 11 omissions retain negative signs in both models.", fontsize=8)
    save_figure(fig, out, STEMS[1], receipt)


def rounded_box(ax, xy, width, height, label, color=PALE, fontsize=8.5, edge=LIGHT):
    patch = FancyBboxPatch(xy, width, height, boxstyle="round,pad=0.012,rounding_size=0.015",
                           facecolor=color, edgecolor=edge, lw=.8, transform=ax.transAxes, clip_on=False)
    ax.add_patch(patch)
    ax.text(xy[0]+width/2, xy[1]+height/2, label, ha="center", va="center",
            fontsize=fontsize, transform=ax.transAxes, linespacing=1.5)
    return patch


def figure3(temporal, out, receipt):
    fig = new_figure(159)
    a = fig.add_axes([.045, .735, .91, .20]); a.axis("off")
    title(a, "a   Matched time order")
    boxes = [(0.005,"P0 · preceding winter\nJune–October, year y",BLUE),
             (.35,"Optical summer δ¹⁵N proxy\nNovember y–February y+1",TEAL),
             (.695,"P1 · following winter\nJune–October, year y+1",ORANGE)]
    for x, label, col in boxes:
        rounded_box(a, (x,.35), .295, .43, label, fontsize=8.5, edge=col)
    for x1,x2 in [(.304,.338),(.649,.683)]:
        a.add_patch(FancyArrowPatch((x1,.56),(x2,.56),arrowstyle="-|>",mutation_scale=9,
                                   color=GREY,lw=1,transform=a.transAxes))
    a.text(.5,.08,"358 matched colony-seasons · 85 sites · 2004–2009 start years",ha="center",fontsize=8.5)
    b = fig.add_axes([.375, .25, .58, .40])
    title(b, "b   Eight-region estimates and sensitivity checks")
    labels = ["P0 · preceding winter", "P1 · following winter", "P0 − P1 · 347 / 8 regions",
              "P0 − P1 · R1,000, 347 / 8", "P0 − P1 · 358 / 11 regions", "P0 − P1 · R1,000, 358 / 11"]
    ys = [5.4,4.5,3.4,2.4,1.3,.3]
    for y,r in zip(ys, temporal.itertuples(index=False)):
        color = (ORANGE if r.measurement == "Author R1000" else TEAL) if r.n == 347 else GREY
        coefficient_point(b,r.beta_per_10pp,r.lower,r.upper,y,color,
                          marker="s" if r.measurement == "Author R1000" else "o",size=36)
    b.set_yticks(ys,labels,fontsize=8.2); b.set_ylim(-.4,6.2); b.set_xlim(-2.5,.35)
    b.axvline(0,color=GREY,lw=.9,ls="--");b.grid(axis="x",color=LIGHT,lw=.6)
    b.set_xlabel("Optical δ¹⁵N proxy difference (‰) per 10 percentage points",fontsize=8.3)
    fig.text(.045,.125,"Both winters enter one model with summer salinity and the original adjustments.",fontsize=8)
    fig.text(.045,.082,"First four rows: 347 / 8 informative regions, t(7). Last two: 358 / 11 reporting regions, t(10).",fontsize=8)
    fig.text(.045,.040,"P0 − P1 intervals include covariance. R1,000 uses the same historical images.",fontsize=8)
    save_figure(fig,out,STEMS[2],receipt)


def figure4(residuals, fit_information, r_value, out, receipt):
    fig=new_figure(110)
    a=fig.add_axes([.11,.28,.36,.58]);title(a,"a   Residual exposure relation")
    a.scatter(residuals.polynya_residual_percentage_points,residuals.salinity_residual,
              s=10,c=BLUE,alpha=.47,edgecolors="none")
    a.axvline(0,color=GREY,lw=.7,ls=":");a.axhline(0,color=GREY,lw=.7,ls=":")
    a.set_xlabel("Winter polynya residual\n(percentage points)",fontsize=8.5)
    a.set_ylabel("Summer salinity residual\n(salinity units)",fontsize=8.5)
    a.set_xlim(-12,9);a.set_ylim(-1.1,1.3)
    a.text(.04,.94,f"r = {r_value:.5f}",transform=a.transAxes,
           va="top",fontsize=8.5,linespacing=1.6)
    b=fig.add_axes([.64,.28,.32,.58]);title(b,"b   Model information")
    vals=fit_information.additional_residual_variation_percent.to_numpy()
    yy=np.arange(3)
    b.barh(yy,vals,color=[GREY,BLUE,TEAL],height=.48)
    b.set_yticks(yy,["M_S", "M_P", "M_SP"],fontsize=8.5);b.invert_yaxis()
    b.set_xlim(0,6.7);b.set_xticks([0,2,4,6]);b.grid(axis="x",color=LIGHT,lw=.6);b.set_axisbelow(True)
    for y,val in zip(yy,vals):b.text(val+.12,y,f"{val:.2f}%",va="center",fontsize=8.5)
    b.set_xlabel("Residual variation explained\nrelative to M0 (%)",fontsize=8.5)
    fig.text(.055,.135,"Panel a removes site and region-by-season effects only. Panel b compares the same 439 rows.",fontsize=8)
    fig.text(.055,.086,"M_S: salinity; M_P: polynya; M_SP: both. M0 includes the original covariates and fixed effects.",fontsize=8)
    fig.text(.055,.035,"These are modest conditional associations; independent physical causes are not identified.",fontsize=8.5)
    save_figure(fig,out,STEMS[3],receipt)


def figure5(out,receipt):
    fig=new_figure(152)
    a=fig.add_axes([.045,.68,.91,.255]);a.axis("off");title(a,"a   Observed historical association")
    rounded_box(a,(.005,.36),.355,.39,"Winter coastal-polynya area fraction\nJune–October · within 100 km",edge=BLUE)
    rounded_box(a,(.64,.36),.355,.39,"Subsequent summer\noptical δ¹⁵N proxy\nNovember–February",edge=TEAL)
    a.plot([.375,.625],[.555,.555],color=BLUE,lw=1.8,transform=a.transAxes)
    a.text(.5,.80,"Negative conditional\nassociation",ha="center",va="center",fontsize=8.5,transform=a.transAxes)
    a.text(.5,.19,"439 colony-seasons · 85 sites · 11 regions · 2004–2010",ha="center",fontsize=8.5,transform=a.transAxes)
    a.text(.5,.015,"Site and region-by-season effects; summer sea ice, temperature and image timing adjusted",ha="center",fontsize=8,transform=a.transAxes)
    b=fig.add_axes([.045,.335,.91,.295]);b.axis("off");title(b,"b   Candidate explanations remain unresolved")
    rounded_box(b,(.005,.36),.18,.28,"Winter\nexposure",edge=BLUE)
    rounded_box(b,(.805,.36),.19,.28,"Optical δ¹⁵N\nproxy",edge=TEAL)
    pathways=[(.72,"Trophic composition\nNot measured here"),(.40,"Nitrogen-isotope baseline\nNot measured here"),(.08,"Optical mixture and surface effects\nUnresolved")]
    for y,label in pathways:
        rounded_box(b,(.33,y),.33,.23,label,fontsize=8.3)
        b.add_patch(FancyArrowPatch((.20,.50),(.315,y+.115),arrowstyle="-|>",mutation_scale=9,
                                   color=GREY,linestyle="--",lw=.9,transform=b.transAxes))
        b.add_patch(FancyArrowPatch((.675,y+.115),(.79,.50),arrowstyle="-|>",mutation_scale=9,
                                   color=GREY,linestyle="--",lw=.9,transform=b.transAxes))
    fig.text(.06,.302,"Dashed arrows show possible pathways, not identified mechanisms.",fontsize=8.5)
    c=fig.add_axes([.045,.045,.91,.205]);c.axis("off");title(c,"c   Separate published comparison")
    rounded_box(c,(.005,.08),.985,.80,"",color=PALE,edge=LIGHT)
    c.text(.5,.76,"Reaves et al. (2025): between-colony context",ha="center",fontsize=8.7,fontweight="bold",transform=c.transAxes)
    c.text(.17,.43,"Southern latent-heat\npolynya settings",ha="center",fontsize=8.5,transform=c.transAxes)
    c.text(.84,.43,"Higher bone δ¹⁵N\nin southern colonies",ha="center",fontsize=8.5,transform=c.transAxes)
    c.plot([.34,.67],[.48,.48],color=GREY,lw=1.2,transform=c.transAxes)
    c.text(.50,.58,"Spatial context",ha="center",fontsize=8.2,transform=c.transAxes)
    c.text(.5,.18,"15 colony locations; modern and ancient chick bones. Distinct estimand.",ha="center",fontsize=8.2,transform=c.transAxes)
    save_figure(fig,out,STEMS[4],receipt)


def main(a):
    base=a.base.resolve();inputs=base/"source_inputs";out=a.out or base/"figures"
    out.mkdir(parents=True,exist_ok=True)
    numbers=out/"numeric_source_extract";numbers.mkdir(exist_ok=True)
    manifest=verify_inputs(base)
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":8.5,
        "axes.titlesize":10,"axes.titleweight":"bold","axes.labelsize":8.5,
        "xtick.labelsize":8,"ytick.labelsize":8,"legend.fontsize":8,
        "text.color":INK,"axes.labelcolor":INK,"xtick.color":INK,"ytick.color":INK,
        "axes.edgecolor":GREY,"axes.spines.top":False,"axes.spines.right":False,
        "axes.linewidth":.7,"svg.fonttype":"none","figure.facecolor":"white"})
    readcsv=lambda name:pd.read_csv(inputs/name)
    readjson=lambda name:json.loads((inputs/name).read_text())
    iso=readcsv("matched_isotope860.csv");physical=readcsv("polynya_physical860.csv")
    main_result=readjson("main439_verdict.json");author=readjson("author_R1000_verdict.json")
    gate=readjson("physical_gate.json")
    if gate["status"]!="PASS_DIRECT_POLYNYA_MACRO_SUPPORT_SOURCE_ONLY_NO_Y_FIT":
        raise ValueError("Frozen physical source gate missing")
    d=iso.merge(physical[["site_id","season","source_region",P]],
                on=["site_id","season"],validate="one_to_one",suffixes=("","_physical"))
    if len(d)!=860 or not d.source_region.eq(d.source_region_physical).all():
        raise ValueError("Frozen 860-row source join changed")
    d=d.loc[d[P].notna()].reset_index(drop=True)
    if (len(d),d.site_id.nunique(),d.source_region.nunique())!=(439,85,11):
        raise ValueError("Frozen 439/85/11 cohort changed")
    if sorted(d.season.unique())!=list(range(2004,2011)) or int(d[P].gt(0).sum())!=405:
        raise ValueError("Frozen winter support changed")
    geography=readcsv("colony_geography.csv").query("radius_km == 100")
    sites=d.groupby(["site_id","source_region"],as_index=False).agg(
        mean_polynya_fraction=(P,"mean"),n_matched_seasons=("season","size"))
    sites=sites.merge(geography[["site_id","source_region","colony_lat","colony_lon"]],
                      on=["site_id","source_region"],validate="one_to_one")
    if len(sites)!=85:raise ValueError("Map lost matched colonies")
    sites["mean_polynya_percent"]=100*sites.mean_polynya_fraction
    region_support=readcsv("region_support.csv").sort_values("source_region").reset_index(drop=True)
    expected=d.groupby("source_region").agg(rows=("site_id","size"),sites=("site_id","nunique"))
    if not (region_support.n_observations.to_numpy()==expected.rows.to_numpy()).all():
        raise ValueError("Regional colony-season counts changed")
    if not (region_support.n_original_sites.to_numpy()==expected.sites.to_numpy()).all():
        raise ValueError("Regional site counts changed")
    geometry=map_geometry(base,sites,a.projection_python)
    land=antarctic_land_geometry(base,a.projection_python)
    geom_lookup={r["site_id"]:r for r in geometry["sites"]}
    sites["EPSG3031_x_1000km"]=[geom_lookup[s]["x_1000km"] for s in sites.site_id]
    sites["EPSG3031_y_1000km"]=[geom_lookup[s]["y_1000km"] for s in sites.site_id]
    sites.to_csv(numbers/"fig1_site_mean_exposure_and_geography.csv",index=False)
    region_support.to_csv(numbers/"fig1_region_support.csv",index=False)
    write_json(numbers/"fig1_map_geometry.json",geometry)
    effects=[]
    for model in ["M_P","M_SP"]:
        source=next(c for c in main_result["models"][model]["region"]["coefficients"] if c["feature"]==P)
        effects.append(dict(model=model,measurement="Original single PLSR",n=439,sites=85,regions=11,
          beta_per_10pp=source["native_beta"]*.1,lower=source["t95ci"][0]*.1,upper=source["t95ci"][1]*.1,
          interval="region cluster t(10) 95%",source="main439_verdict.json"))
        r=author["original439_"+model]
        if not np.isclose(effects[-1]["beta_per_10pp"],r["old_single_PLSR_beta_per_10pp"],rtol=0,atol=2e-14):
            raise ValueError("Original coefficient differs between pinned source artifacts")
        effects.append(dict(model=model,measurement="Author R1000",n=439,sites=85,regions=11,
          beta_per_10pp=r["author_R1000_PLSR_beta_per_10pp"],lower=r["author_region_cluster_t95"][0],
          upper=r["author_region_cluster_t95"][1],interval="region cluster t(10) 95%",source="author_R1000_verdict.json"))
    frozen_effects=pd.DataFrame(effects)
    frozen_effects.to_csv(numbers/"fig2_original_frozen11_intervals.csv",index=False)
    support_sensitivity=readjson("main425_informative8_20261121.json")
    dated=support_sensitivity["new_20261121_main425_informative8_support_sensitivity"]
    if (dated["n"],dated["sites"],dated["informative_regions"],dated["interval_t_df"])!=(425,82,8,7):
        raise ValueError("Dated informative-region support changed")
    effects=[]
    for model in ["M_P","M_SP"]:
        for key,measurement in [("original_single_PLSR","Original single PLSR"),("author_R1000_mean_Y","Author R1000")]:
            value=dated[key][model]["polynya_per_10pp"]
            frozen=frozen_effects.loc[frozen_effects.model.eq(model)&frozen_effects.measurement.eq(measurement)].iloc[0]
            if abs(value["estimate"]-frozen.beta_per_10pp)>1e-10:
                raise ValueError("Dated covariance sensitivity altered a frozen coefficient")
            effects.append(dict(model=model,measurement=measurement,n=425,sites=82,regions=8,
                original_cohort_n=439,original_cohort_sites=85,original_reporting_regions=11,
                beta_per_10pp=value["estimate"],lower=value["ci95"][0],upper=value["ci95"][1],
                interval="informative-region cluster t(7) 95%; dated 2026-11-21 covariance sensitivity",
                source="main425_informative8_20261121.json"))
    effects=pd.DataFrame(effects);effects.to_csv(numbers/"fig2_main_and_measurement_sensitivity.csv",index=False)
    leaves=readcsv("main439_leave_region_out.csv");leaves["beta_per_10pp"]=leaves.polynya_beta*.1
    if len(leaves)!=22 or not leaves.beta_per_10pp.lt(0).all():raise ValueError("Frozen omission signs changed")
    leaves.to_csv(numbers/"fig2_leave_one_region_out.csv",index=False)
    temporal_source=readcsv("temporal358_coefficients.csv")
    informative_source=readcsv("temporal347_informative.csv")
    temporal=[]
    for term in ["P0","P1","P0_minus_P1"]:
        r=informative_source.loc[informative_source.term.eq(term)].iloc[0]
        if (int(r.n),int(r.regions))!=(347,8):raise ValueError("Informative temporal support changed")
        temporal.append(dict(term=term,measurement="Original single PLSR",n=347,regions=8,
            beta_per_10pp=float(r.beta_per_10pp),lower=float(r.lower),upper=float(r.upper),
            source="temporal347_informative.csv"))
    r=author["original358_informative_8region_P0_minus_P1"]
    temporal.append(dict(term="P0_minus_P1",measurement="Author R1000",n=347,regions=8,
       beta_per_10pp=r["author_R1000_PLSR_beta_per_10pp"],lower=r["author_region_cluster_t95"][0],
       upper=r["author_region_cluster_t95"][1],source="author_R1000_verdict.json"))
    r=temporal_source.query("model == 'Mjoint' and term == 'P0_minus_P1'").iloc[0]
    temporal.append(dict(term="P0_minus_P1",measurement="Original single PLSR",n=358,regions=11,
        beta_per_10pp=float(r.beta_per_10pp),lower=float(r.lower),upper=float(r.upper),
        source="temporal358_coefficients.csv"))
    r=author["original358_P0_minus_P1"]
    temporal.append(dict(term="P0_minus_P1",measurement="Author R1000",n=358,regions=11,
       beta_per_10pp=r["author_R1000_PLSR_beta_per_10pp"],lower=r["author_region_cluster_t95"][0],
       upper=r["author_region_cluster_t95"][1],source="author_R1000_verdict.json"))
    temporal=pd.DataFrame(temporal);temporal.to_csv(numbers/"fig3_reported_temporal_coefficients.csv",index=False)
    region_season=d.source_region+"__"+d.season.astype(str)
    rp,pa=project_two_fe(d[P],d.site_id,region_season)
    rs,sa=project_two_fe(d[S],d.site_id,region_season)
    correlation=float(np.corrcoef(rp,rs)[0,1])
    if abs(correlation-(-.08043))>5e-6:raise ValueError("Frozen residual P–S correlation not reproduced")
    residuals=d[["site_id","season","source_region",P,S]].copy()
    residuals["polynya_residual_percentage_points"]=100*rp
    residuals["salinity_residual"]=rs
    residuals.to_csv(numbers/"fig4_same439_fixed_effect_residuals.csv",index=False)
    fit_information=pd.DataFrame([{"model":m,"n":439,
        "additional_residual_variation_percent":100*main_result["models"][m]["additional_M0_residual_fraction"],
        "source":"main439_verdict.json"} for m in ["M_S","M_P","M_SP"]])
    fit_information.to_csv(numbers/"fig4_reported_model_information.csv",index=False)
    receipt=[]
    figure1(sites,region_support,geometry,land,out,receipt)
    if a.figure1_only:
        prior = json.loads((out/"polynya_figure_verification_receipt.json").read_text())
        receipt.extend(r for r in prior["figures"] if r["stem"] != STEMS[0])
        if [r["stem"] for r in receipt] != STEMS:
            raise ValueError("--figure1-only requires the existing verified five-figure receipt")
    else:
        figure2(effects,leaves,out,receipt)
        figure3(temporal,out,receipt)
        figure4(residuals,fit_information,correlation,out,receipt)
        figure5(out,receipt)
    # Include the deterministic coordinate cache as a checked offline input.
    map_record={"local_file":"source_inputs/map_geometry.json","sha256":sha256(inputs/"map_geometry.json"),
                "bytes":(inputs/"map_geometry.json").stat().st_size,"derived_from":"colony_geography.csv and the frozen matched 85 site IDs",
                "operation":"EPSG:4326 to EPSG:3031; WGS84 100-km geodesic sampling circles and a 1000-km scale bar; colony geometry only, independent of the display land layer"}
    if not any(r["local_file"]==map_record["local_file"] for r in manifest["inputs"]):
        manifest["inputs"].append(map_record)
    else:
        next(r for r in manifest["inputs"] if r["local_file"]==map_record["local_file"])["operation"] = map_record["operation"]
    land_record={"local_file":"source_inputs/antarctic_land_EPSG3031.json",
                 "sha256":sha256(inputs/"antarctic_land_EPSG3031.json"),
                 "bytes":(inputs/"antarctic_land_EPSG3031.json").stat().st_size,
                 "derived_from":"source_inputs/ne_110m_land.geojson",
                 "source_sha256":LAND_SOURCE_SHA256,"source_git_blob":LAND_SOURCE_GIT_BLOB,
                 "operation":land["selection"] + " " + land["seam_handling"],
                 "use":"Figure 1 display context only; no ecological input, exposure, coefficient or site coordinate is changed"}
    if not any(r["local_file"]==land_record["local_file"] for r in manifest["inputs"]):
        manifest["inputs"].append(land_record)
    manifest["renderer"]="render_polynya_main_figures.py"
    manifest["renderer_sha256"]=sha256(Path(__file__))
    manifest["offline_rerender"]="python render_polynya_main_figures.py (numpy, pandas, matplotlib, Pillow; pyproj unnecessary when verified site and Antarctic-land map caches are present)"
    write_json(base/"source_manifest.json",manifest)
    audit={"status":"PASS_FIVE_VERIFIED_SOURCE_FIGURES_WITH_DATED_COVARIANCE_SENSITIVITY",
       "renderer_performed_no_model_fit":True,"renderer_performed_no_interval_estimation_or_threshold_search":True,
       "new_dated_result_plotted":"Figure 2 reads the explicitly requested 2026-11-21 main425 informative-eight-region covariance sensitivity from the manuscript verification workflow. It is not an original frozen 11-region result.",
       "recomputed":{"original_join_rows":860,"matched_main_rows":439,"matched_sites":85,"matched_regions":11,
          "winter_years":list(range(2004,2011)),"nonzero_polynya_rows":405,
          "site_mean_exposure_percent_min":float(sites.mean_polynya_percent.min()),
          "site_mean_exposure_percent_max":float(sites.mean_polynya_percent.max()),
          "same439_P_S_FE_only_correlation":correlation,"source_reported_correlation_rounded":-.08043,
          "polynya_FE_projection":pa,"salinity_FE_projection":sa,"map_scale":geometry["scale_bar"]},
       "plotted_reported_results":{"main_coefficients_dated_informative8_intervals":effects.to_dict("records"),
          "original_frozen11_intervals_retained_in_numeric_extract":frozen_effects.to_dict("records"),
          "temporal_coefficients":temporal.to_dict("records"),
          "additional_residual_variation_percent":fit_information.to_dict("records"),
          "leave_region_out_M_P_all_11_negative":bool(leaves.query("model == 'M_P'").beta_per_10pp.lt(0).all()),
          "leave_region_out_M_SP_all_11_negative":bool(leaves.query("model == 'M_SP'").beta_per_10pp.lt(0).all())},
       "precision_note":"Temporal original CI endpoints differ by <=9e-12 between the original temporal table and later author-calibration reproduction; Figure 3 retains original temporal table endpoints.",
       "raster_quantization_note":"170 mm at exactly 800 dpi is 5354.3307 pixels. TIFF width is rounded upward to 5355 pixels and tagged 800.1 dpi, preserving exactly 170 mm and at least 800 dpi.",
       "figure1_cartographic_context":{"source":"Natural Earth 1:110m land", "source_sha256":LAND_SOURCE_SHA256,
          "source_git_blob":LAND_SOURCE_GIT_BLOB,"projected_cache_sha256":sha256(inputs/"antarctic_land_EPSG3031.json"),
          "selected_source_feature_indices":[p["feature_index"] for p in land["polygons"]],
          "display_only":True,"exposure_or_site_geography_changed":False,
          "seam_handling":land["seam_handling"],"longitude_labels":["0°","90°W","90°E"],
          "terms":"https://www.naturalearthdata.com/about/terms-of-use/","license":"Public domain"},
       "figures":receipt,
       "conceptual_panel_c":"Reaves et al. (2025) primary-abstract context verified by manuscript team: southern latent-heat polynya settings and higher bone delta15N in southern colonies, 15 colony locations with modern and ancient chick bones. No continuous polynya-area slope or direct sign reversal is claimed.",
       "source_manifest_sha256":sha256(base/"source_manifest.json")}
    write_json(out/"polynya_figure_verification_receipt.json",audit)
    alt={
       STEMS[0]:"Antarctic polar stereographic map of the 85 matched Adélie sites, coloured by each site's mean observed June–October coastal-polynya area fraction within 100 km. A pale generalized Natural Earth 1:110m land outline and labelled 0, 90 west and 90 east meridians provide geographic context only; land is not used as an analysis mask. Thin blue outlines show 100-km geodesic sampling circles, not polynya boundaries. A region table totals 439 colony-seasons in 11 regions during 2004–2010. The geodesically calibrated scale bar is centred at 70 degrees south. All original colony locations and exposure values are unchanged.",
       STEMS[1]:"Forest plot of four polynya coefficients, with original single-PLSR and author-R1000 optical measurements, without and with summer salinity adjustment. The displayed covariance sensitivity, dated 2026-11-21, uses 425 informative rows, 82 sites and 8 regions with t(7) intervals. Coefficients are unchanged from the 439-row cohort; all four intervals are below zero. A separate plot shows the 11 leave-region-out point estimates for each original model; all point estimates are negative, with no omission-specific intervals drawn. Original frozen 11-region intervals are preserved in the numerical extract.",
       STEMS[2]:"Time order of preceding winter P0, summer optical isotope proxy, and following winter P1 on 358 matched observations. The first four forest-plot rows show simultaneous-model P0, P1, the covariance-based contrast, and the author-R1000 contrast for 347 observations in 8 informative regions with t(7) intervals. Final rows compare original and author-R1000 contrasts on 358 observations in all 11 reporting regions. P1 intervals cross zero; all displayed direct contrast intervals end just below zero.",
       STEMS[3]:"Scatter plot of winter polynya and summer salinity residuals after site and region-by-season effects only, on the same 439 observations, with correlation minus 0.08043. A bar plot reports additional residual variation relative to M0: salinity 2.1429%, polynya 3.7939%, and both 5.2928%. These modest conditional associations do not identify independent physical causes.",
       STEMS[4]:"Conceptual figure separating the observed negative historical within-colony association from three unresolved candidate pathways: trophic composition, nitrogen-isotope baseline, and optical mixture or surface effects. The observed association has no causal arrowhead; candidate pathways use dashed arrows. A distinct shaded panel places the Reaves et al. 2025 southern latent-heat-polynya settings and higher bone delta15N in southern colonies in a separate between-colony context: 15 locations with modern and ancient chick bones. The tissue, timescale and estimand differ; no continuous polynya-area slope, direct sign reversal or proven mechanism is implied."
    }
    write_json(base/"figure_alt_text.json",alt)
    print(json.dumps({"status":audit["status"],"output":str(out),"same439_correlation":correlation,
                      "figures":receipt},ensure_ascii=False,indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--base",type=Path,default=HERE)
    parser.add_argument("--out",type=Path)
    parser.add_argument("--projection-python",default=None)
    parser.add_argument("--figure1-only",action="store_true",help="Update Figure 1 and provenance while preserving existing Figures 2–5")
    main(parser.parse_args())
