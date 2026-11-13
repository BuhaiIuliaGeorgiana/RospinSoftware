import geopandas as gpd
from config import OUT

def export_geojson(src, dst, columns):
    """Read a clean GeoPackage and write a GeoJSON in EPSG:4326."""
    gdf = gpd.read_file(OUT / src).to_crs(4326)
    gdf = gdf[[c for c in columns if c in gdf.columns] + ["geometry"]]
    path = OUT / dst
    gdf.to_file(path, driver="GeoJSON")
    print(f"{dst}: {len(gdf)} features, {path.stat().st_size / 1e6:.1f} MB")

if __name__ == "__main__":
    export_geojson("clean_buildings.gpkg", "pechea_buildings.geojson", ["height", "confidence"])
    export_geojson("clean_roads.gpkg", "pechea_roads.geojson", ["osm_id", "fclass", "name", "is_real_road"])
    export_geojson("clean_farmland.gpkg", "pechea_farmland.geojson", ["osm_id", "fclass", "name"])