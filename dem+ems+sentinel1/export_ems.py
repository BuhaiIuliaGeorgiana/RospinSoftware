"""Exporta datele Copernicus EMS (EMSR758, AOI 03 Pechea) pentru aplicatie.

Citeste GeoPackage-ul creat de build_ems_clean.py si tabelele *_source_v1.dbf din
pachetele EMS. Scrie in export/: GeoJSON (EPSG:4326) taiat la PECHEA_BOUNDS si
summary_ems.json, cu aceeasi structura ca summary.json de la Sentinel-1.
"""
import glob
import json
import os
from pathlib import Path

import geopandas as gpd
from shapely.geometry import box

# Ordine: longitudine vest, latitudine sud, longitudine est, latitudine nord.
# Aceeasi valoare ca in notebook-urile Sentinel. Se schimba intr-un singur loc.
PECHEA_BOUNDS = [27.61, 45.46, 27.87, 45.74]
CLIP_LA_BOUNDS = True   # False = pastreaza toata zona AOI 03

GPKG = "data/ems/pechea_flood_ems.gpkg"
EMS_DIR = "data/ems"
OUT_DIR = Path("export")

# cheie produs -> (folder EMS, eticheta, strat inundatie, strat adancime, strat extent maxim)
PRODUSE = {
    "fep":    ("EMSR758_AOI03_FEP_PRODUCT_v1", "First Estimate",
               "flood_fep_20240914", None, None),
    "del":    ("EMSR758_AOI03_DEL_PRODUCT_v1", "Delineation",
               "flood_del_20240915", "depth_del_20240915", None),
    "monit1": ("EMSR758_AOI03_DEL_MONIT01_v1", "Delineation Monitoring 1",
               "flood_monit1_20240917", "depth_monit1_20240917",
               "max_extent_monit1_20240917"),
}


def ha(g):
    return float(g.to_crs(32635).area.sum() / 10_000)


def citeste_sursele(folder):
    # sursele imaginilor, din tabelul *_source_v1.dbf al produsului
    cale = glob.glob(os.path.join(EMS_DIR, folder, "*_source_v1.dbf"))[0]
    tabel = gpd.read_file(cale)
    post = tabel[tabel["eventphase"] == "Post-event"]
    pre = tabel[(tabel["eventphase"] == "Pre-event") & (tabel["source_nam"] == "Sentinel-2")]

    def data_ora(rand):
        zi, luna, an = rand["src_date"].split("/")
        return f"{an}-{luna}-{zi}{rand['source_tm'].replace('Z', '')}Z"

    dem = tabel[tabel["source_nam"].str.contains("DEM", case=False)]
    return {
        "post_event": [
            {"sensor": r["source_nam"], "acquired_at_utc": data_ora(r),
             "resolution": r["sensor_res"], "ems_src_id": int(r["src_id"])}
            for _, r in post.iterrows()
        ],
        "pre_event_reference": [
            {"sensor": r["source_nam"], "acquired_at_utc": data_ora(r),
             "resolution": r["sensor_res"], "ems_src_id": int(r["src_id"])}
            for _, r in pre.iterrows()
        ],
        "elevation_sources": [
            {"name": r["source_nam"], "year": r["src_date"], "resolution": r["sensor_res"]}
            for _, r in dem.iterrows()
        ],
    }


def scrie(g, nume, taie):
    g = g.to_crs(4326)
    if taie is not None:
        g = g.clip(taie)
    g = g[~g.is_empty].copy()
    g["area_ha"] = (g.to_crs(32635).area / 10_000).round(2)
    OUT_DIR.mkdir(exist_ok=True)
    g.to_file(OUT_DIR / f"{nume}.geojson", driver="GeoJSON")
    return g


taie = box(*PECHEA_BOUNDS) if CLIP_LA_BOUNDS else None
OUT_DIR.mkdir(exist_ok=True)

aoi_complet = gpd.read_file(GPKG, layer="aoi").to_crs(4326)
aoi = scrie(aoi_complet[["emsr_id", "locality", "geometry"]], "ems_aoi03", None)

sumar = {
    "event_id": "pechea",
    "name": "Pechea, Galati",
    "source": "Copernicus EMS EMSR758, AOI 03 Pechea",
    "aoi_bbox_wgs84": PECHEA_BOUNDS if CLIP_LA_BOUNDS else [round(v, 5) for v in aoi.total_bounds],
    "clipped_to_bbox": CLIP_LA_BOUNDS,
    "crs": "EPSG:4326",
    "note": "EMS a cartografiat doar in interiorul AOI 03; in afara lui nu stim, nu inseamna 'fara inundatie'.",
    "files": {"aoi": "ems_aoi03.geojson"},
    "products": {},
}

for cheie, (folder, eticheta, l_flood, l_depth, l_max) in PRODUSE.items():
    surse = citeste_sursele(folder)
    info = {"label": eticheta, **surse, "files": {}}

    flood_complet = gpd.read_file(GPKG, layer=l_flood)
    info["acquired_at_utc"] = surse["post_event"][0]["acquired_at_utc"]
    info["flooded_area_ha_total"] = round(ha(flood_complet), 1)

    for rol, strat in (("flood", l_flood), ("depth", l_depth), ("max_extent", l_max)):
        if strat is None:
            continue
        nume = f"ems_{strat}"
        g = scrie(gpd.read_file(GPKG, layer=strat).drop(columns=["area_ha"]), nume, taie)
        info["files"][rol] = f"{nume}.geojson"
        if rol == "flood":
            info["flooded_area_ha_in_bounds"] = round(ha(g), 1) if len(g) else 0.0
            info["polygons_in_bounds"] = int(len(g))
        print(f"{nume:34s} {len(g):4d} poligoane  {ha(g) if len(g) else 0:8.1f} ha")
    sumar["products"][cheie] = info

(OUT_DIR / "summary_ems.json").write_text(
    json.dumps(sumar, indent=2, ensure_ascii=False), encoding="utf-8")
print("\nsalvat in", OUT_DIR)
