"""Harta combinata Pechea: DEM + produse Copernicus EMS + masca Sentinel-1.

Panou stanga : relief (DEM) cu extinderea inundatiei din EMS (First Estimate, Delineation, Monitoring 1).
Panou dreapta: acord intre masca Sentinel-1 si EMS First Estimate (aceeasi achizitie, 14 Sept), doar in AOI 03.

Folosire (din folderul proiectului):
    python plot_combined.py [--save]
Cai implicite: data/dem/dem_m.tif, data/sentinel-1/flood_mask.tif, export/*.geojson
Necesita: rasterio, numpy, matplotlib.
"""
import json
import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.path import Path as MplPath

DEM = "data/dem/dem_m.tif"
MASCA = "data/sentinel-1/flood_mask.tif"
EXPORT = Path("export")
NODATA = -9999
PIXEL_M = 10

PRODUSE = [  # fisier, eticheta, culoare (paleta Okabe-Ito, distincta si pentru daltonisti)
    ("ems_flood_fep_20240914.geojson", "EMS First Estimate, 14 Sept (Sentinel-1)", "#0072B2"),
    ("ems_flood_del_20240915.geojson", "EMS Delineation, 15 Sept (PAZ-1)", "#E69F00"),
    ("ems_flood_monit1_20240917.geojson", "EMS Monitoring 1, 17 Sept (COSMO-SkyMed)", "#CC79A7"),
]


# --- WGS84 lon/lat -> UTM 35N (EPSG:32635), formula Kruger, fara pyproj ---------------
def utm35(lon, lat):
    a, f, k0, lon0 = 6378137.0, 1 / 298.257223563, 0.9996, math.radians(27.0)
    n = f / (2 - f)
    A = a / (1 + n) * (1 + n**2 / 4 + n**4 / 64)
    al = [n / 2 - 2 * n**2 / 3 + 5 * n**3 / 16, 13 * n**2 / 48 - 3 * n**3 / 5,
          61 * n**3 / 240]
    phi, lam = np.radians(lat), np.radians(lon) - lon0
    e = math.sqrt(f * (2 - f))
    t = np.sinh(np.arctanh(np.sin(phi)) - e * np.arctanh(e * np.sin(phi)))
    xi = np.arctan2(t, np.cos(lam))
    eta = np.arctanh(np.sin(lam) / np.sqrt(1 + t**2))
    x = eta + sum(c * np.cos(2 * (j + 1) * xi) * np.sinh(2 * (j + 1) * eta) for j, c in enumerate(al))
    y = xi + sum(c * np.sin(2 * (j + 1) * xi) * np.cosh(2 * (j + 1) * eta) for j, c in enumerate(al))
    return 500000 + k0 * A * x, k0 * A * y


def poligoane_utm(cale):
    """GeoJSON (lon/lat) -> lista de poligoane; fiecare e o lista de inele (N,2) in metri UTM."""
    rezultat = []
    for ft in json.loads(Path(cale).read_text())["features"]:
        g = ft["geometry"]
        if g is None:
            continue
        parti = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"] if g["type"] == "MultiPolygon" else []
        for poly in parti:
            rezultat.append([np.column_stack(utm35(np.array(r)[:, 0], np.array(r)[:, 1])) for r in poly])
    return rezultat


def rasterizeaza(poligoane, left, top, shape):
    """Masca booleana pe grila rasterului (nord sus, pixel 10 m); gaurile sunt scoase (xor)."""
    h, w = shape
    masca = np.zeros(shape, bool)
    for inele in poligoane:
        xs = np.concatenate([r[:, 0] for r in inele])
        ys = np.concatenate([r[:, 1] for r in inele])
        c0, c1 = max(int((xs.min() - left) // PIXEL_M), 0), min(int((xs.max() - left) // PIXEL_M) + 1, w)
        r0, r1 = max(int((top - ys.max()) // PIXEL_M), 0), min(int((top - ys.min()) // PIXEL_M) + 1, h)
        if c0 >= c1 or r0 >= r1:
            continue
        cc, rr = np.meshgrid(np.arange(c0, c1), np.arange(r0, r1))
        centre = np.column_stack([left + (cc.ravel() + 0.5) * PIXEL_M, top - (rr.ravel() + 0.5) * PIXEL_M])
        in_poly = np.zeros(len(centre), bool)
        for inel in inele:
            in_poly ^= MplPath(inel).contains_points(centre)
        masca[r0:r1, c0:c1] |= in_poly.reshape(rr.shape)
    return masca


def contur(ax, poligoane, **kw):
    for inele in poligoane:
        for r in inele:
            ax.plot(r[:, 0], r[:, 1], **kw)


# --- date ------------------------------------------------------------------------------
with rasterio.open(DEM) as src:
    dem = src.read(1).astype("float32")
    b = src.bounds
    left, top = b.left, b.top
extent = (b.left, b.right, b.bottom, b.top)
dem[(dem == NODATA) | ~np.isfinite(dem)] = np.nan

with rasterio.open(MASCA) as src:
    s1 = src.read(1).astype("float32")
    assert src.bounds.left == left and src.bounds.top == top, "DEM si masca nu sunt pe aceeasi grila"
valid = np.isfinite(s1) & (s1 != NODATA)
pred = s1 == 1

aoi = rasterizeaza(poligoane_utm(EXPORT / "ems_aoi03.geojson"), left, top, dem.shape)
zona = valid & aoi
ems = {f: poligoane_utm(EXPORT / f) for f, _, _ in PRODUSE}
fep = rasterizeaza(ems[PRODUSE[0][0]], left, top, dem.shape) & zona

# hillshade din DEM (pixel 10 m)
dy, dx = np.gradient(np.nan_to_num(dem, nan=float(np.nanmean(dem))), PIXEL_M)
slope, aspect = np.arctan(np.hypot(dx, dy)), np.arctan2(-dx, dy)
hill = np.sin(np.radians(45)) * np.cos(slope) + np.cos(np.radians(45)) * np.sin(slope) * np.cos(np.radians(315) - aspect)
hill[np.isnan(dem)] = np.nan

fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 8), constrained_layout=True)

# --- stanga: relief + EMS ---------------------------------------------------------------
a1.imshow(hill, extent=extent, cmap="gray", vmin=0, vmax=1)
a1.imshow(dem, extent=extent, cmap="Greys", alpha=0.35,
          vmin=np.nanpercentile(dem, 1), vmax=np.nanpercentile(dem, 99))
for i, (f, eticheta, culoare) in enumerate(PRODUSE):
    for inele in ems[f]:
        a1.fill(inele[0][:, 0], inele[0][:, 1], color=culoare, alpha=0.35 if i == 0 else 0.0, lw=0)
    contur(a1, ems[f], color=culoare, lw=0.9)
contur(a1, poligoane_utm(EXPORT / "ems_aoi03.geojson"), color="black", lw=1.2, ls="--")
a1.legend(handles=[Line2D([], [], color=c, lw=2, label=e) for _, e, c in PRODUSE]
          + [Line2D([], [], color="black", lw=1.2, ls="--", label="AOI 03 Pechea (EMSR758)")],
          loc="lower right", fontsize=8, framealpha=0.9)
a1.set_title("Relief (Copernicus GLO-30) si inundatia cartografiata de EMS")

# --- dreapta: acord Sentinel-1 vs EMS FEP ----------------------------------------------
p = pred & zona
tp, fp, fn = p & fep, p & ~fep, ~p & fep
imagine = np.full(dem.shape + (4,), np.nan)
imagine[...] = 0
imagine[..., 3] = 0
for masca, culoare in ((tp, "#009E73"), (fp, "#D55E00"), (fn, "#0072B2")):
    imagine[masca] = plt.matplotlib.colors.to_rgba(culoare)
a2.imshow(hill, extent=extent, cmap="gray", vmin=0, vmax=1)
a2.imshow(imagine, extent=extent, interpolation="nearest")
contur(a2, poligoane_utm(EXPORT / "ems_aoi03.geojson"), color="black", lw=1.2, ls="--")
iou = tp.sum() / max(tp.sum() + fp.sum() + fn.sum(), 1)
prec = tp.sum() / max(tp.sum() + fp.sum(), 1)
rec = tp.sum() / max(tp.sum() + fn.sum(), 1)
a2.set_title(f"Sentinel-1 (VV) vs EMS First Estimate, aceeasi achizitie\n"
             f"IoU {iou:.3f}   precizie {prec:.3f}   recall {rec:.3f}   F1 {2*prec*rec/max(prec+rec,1e-9):.3f}")
ha = lambda m: m.sum() * PIXEL_M**2 / 1e4
a2.legend(handles=[Patch(color="#009E73", label=f"ambele: {ha(tp):,.0f} ha"),
                   Patch(color="#D55E00", label=f"doar Sentinel-1: {ha(fp):,.0f} ha"),
                   Patch(color="#0072B2", label=f"doar EMS: {ha(fn):,.0f} ha")],
          loc="lower right", fontsize=8, framealpha=0.9)

for a in (a1, a2):
    a.set_xlim(extent[0], extent[1]); a.set_ylim(extent[2], extent[3])
    a.set_xlabel("E (EPSG:32635, m)"); a.set_ylabel("N (m)")
    a.ticklabel_format(style="plain"); a.tick_params(axis="x", labelrotation=30)

if "--save" in sys.argv:
    fig.savefig("combined_preview.png", dpi=150)
    print("salvat: combined_preview.png")
else:
    plt.show()
