import pandas as pd
import geopandas as gpd
import mercantile
from shapely.geometry import shape
from config import WEST, SOUTH, EAST, NORTH, RAW

LINKS_URL = "https://bfppub.blob.core.windows.net/%24web/2026-07-24/dataset-links.csv"

links = pd.read_csv(LINKS_URL, dtype=str)
quadkeys = {mercantile.quadkey(t) for t in mercantile.tiles(WEST, SOUTH, EAST, NORTH, 9)}
subset = links[(links.Location == "Romania") & (links.QuadKey.isin(quadkeys))]
print(len(subset), "tile(s) to download")

frames = []
for url in subset.Url:
    df = pd.read_json(url, lines=True)
    df["geometry"] = df["geometry"].apply(shape)
    frames.append(gpd.GeoDataFrame(df, geometry="geometry", crs=4326))

buildings = pd.concat(frames).cx[WEST:EAST, SOUTH:NORTH]
print(len(buildings), "buildings (before exact clip)")
buildings.to_file(RAW / "pechea_buildings_ms.gpkg", driver="GPKG")