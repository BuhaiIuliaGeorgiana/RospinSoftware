"""Compara o masca de inundatie (GeoTIFF, 1 = inundat) cu produsele Copernicus EMS.

Folosire:  python validate_vs_ems.py cale/catre/flood_mask.tif
Evalueaza doar pixelii valizi din interiorul AOI 03 (EMS nu a cartografiat in afara lui).
"""
import sys

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import rasterize

GPKG = "data/ems/pechea_flood_ems.gpkg"
REFERINTE = [
    ("flood_fep_20240914",   "First Estimate, 14 Sept (Sentinel-1, aceeasi achizitie)"),
    ("flood_del_20240915",   "Delineation, 15 Sept (PAZ-1)"),
    ("flood_monit1_20240917", "Monitoring 1, 17 Sept (COSMO-SkyMed)"),
]

mask_path = sys.argv[1] if len(sys.argv) > 1 else "flood_mask.tif"
with rasterio.open(mask_path) as src:
    mask = src.read(1)
    transform, shape, crs = src.transform, src.shape, src.crs

valid = ~np.isnan(mask) & (mask != -9999)      # NaN = in afara zonei, -9999 = fara date
pred = mask == 1


def pe_grila(layer):
    g = gpd.read_file(GPKG, layer=layer).to_crs(crs)
    return rasterize([(x, 1) for x in g.geometry], out_shape=shape,
                     transform=transform, fill=0).astype(bool)


aoi = pe_grila("aoi")
zona = valid & aoi
print(f"pixeli evaluati: {zona.sum()} = {zona.sum() / 100:,.0f} ha (valizi si in AOI 03)\n")
print(f"{'referinta':58s} {'ref ha':>7s} {'pred ha':>8s} {'IoU':>6s} {'prec':>6s} {'rec':>6s} {'F1':>6s}")
for layer, eticheta in REFERINTE:
    ref = pe_grila(layer) & zona
    p = pred & zona
    tp, fp, fn = (p & ref).sum(), (p & ~ref).sum(), (~p & ref).sum()
    iou = tp / (tp + fp + fn) if tp + fp + fn else float("nan")
    prec = tp / (tp + fp) if tp + fp else float("nan")
    rec = tp / (tp + fn) if tp + fn else float("nan")
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else float("nan")
    print(f"{eticheta:58s} {ref.sum() / 100:7.1f} {p.sum() / 100:8.1f} {iou:6.3f} {prec:6.3f} {rec:6.3f} {f1:6.3f}")
