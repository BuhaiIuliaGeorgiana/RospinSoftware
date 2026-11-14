import glob
import os

import geopandas as gpd

ROOT = "data/ems"
OUT = "data/ems/pechea_flood_ems.gpkg"

# folder name, short key, image acquisition time (UTC) shown on the EMSR758 page
PRODUCTS = [
    ("EMSR758_AOI03_FEP_PRODUCT_v1", "fep",    "2024-09-14 04:22"),
    ("EMSR758_AOI03_DEL_PRODUCT_v1", "del",    "2024-09-15 15:59"),
    ("EMSR758_AOI03_DEL_MONIT01_v1", "monit1", "2024-09-17 16:13"),
]


def read(folder, layer):
    paths = glob.glob(os.path.join(ROOT, folder, f"*_{layer}_v1.json"))
    return gpd.read_file(paths[0]).to_crs(4326) if paths else None


def tag(g, key, acq, keep=()):
    g = g.copy()
    g["product"] = key
    g["acq_utc"] = acq
    g["area_ha"] = (g.to_crs(32635).area / 10_000).round(2)
    return g[["product", "acq_utc", "area_ha", *keep, "geometry"]]


os.makedirs(os.path.dirname(OUT), exist_ok=True)
if os.path.exists(OUT):
    os.remove(OUT)


def save(g, name):
    g.to_file(OUT, layer=name, driver="GPKG")
    print(f"{name:28s} {len(g):4d} polygons  {g['area_ha'].sum():9,.1f} ha")


# area of interest (same in every product)
aoi = read(PRODUCTS[1][0], "areaOfInterestA")
aoi["area_ha"] = (aoi.to_crs(32635).area / 10_000).round(2)
save(aoi[["emsr_id", "locality", "area_ha", "geometry"]], "aoi")

for folder, key, acq in PRODUCTS:
    date = acq[:10].replace("-", "")
    flood = read(folder, "observedEventA")
    save(tag(flood, key, acq), f"flood_{key}_{date}")

    depth = read(folder, "floodDepthA")
    if depth is not None:
        depth = depth.rename(columns={"value": "depth_class"})
        save(tag(depth, key, acq, keep=("depth_class",)), f"depth_{key}_{date}")

    max_extent = read(folder, "maximumFloodExtentA")
    if max_extent is not None:
        save(tag(max_extent, key, acq), f"max_extent_{key}_{date}")

print("\nsaved:", OUT)