import json
import geopandas as gpd
from shapely.geometry import box
from config import WEST, SOUTH, EAST, NORTH, BBOX, RAW, GEOFABRIK, OUT, MEASURE_CRS

AOI = gpd.GeoDataFrame({"name": ["Pechea_team_AOI"]},
                       geometry=[box(*BBOX)], crs=4326)

REAL_ROADS = ["motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link",
              "secondary", "secondary_link", "tertiary", "tertiary_link",
              "unclassified", "residential", "living_street", "service"]
FARM_CLASSES = ["farmland", "meadow", "orchard", "vineyard"]

def clean(gdf, geom_types):
    gdf = gdf[~gdf.geometry.isna()].copy()
    gdf["geometry"] = gdf.geometry.make_valid()
    gdf = gdf[gdf.geometry.type.isin(geom_types)]
    return gdf[~gdf.geometry.is_empty]

def clip_to_aoi(gdf, geom_types):
    clipped = gpd.clip(gdf.to_crs(4326), AOI, keep_geom_type=True)
    return clean(clipped, geom_types).reset_index(drop=True)

def show_extent(name, gdf):
    b = gdf.total_bounds
    print(f"  {name}: W {b[0]:.4f} S {b[1]:.4f} E {b[2]:.4f} N {b[3]:.4f}")

# --- Buildings ---
print("Buildings...")
bld = clip_to_aoi(gpd.read_file(RAW / "pechea_buildings_ms.gpkg"), ["Polygon", "MultiPolygon"])
bld = bld[[c for c in ["height", "confidence", "geometry"] if c in bld.columns]]
bld.to_file(OUT / "clean_buildings.gpkg", driver="GPKG")
show_extent("buildings", bld)

# --- Roads ---
print("Roads...")
roads = gpd.read_file(GEOFABRIK / "gis_osm_roads_free_1.shp", bbox=BBOX)
roads = clip_to_aoi(roads, ["LineString", "MultiLineString"])
roads["is_real_road"] = roads["fclass"].isin(REAL_ROADS)
roads = roads[["osm_id", "fclass", "name", "is_real_road", "geometry"]]
roads.to_file(OUT / "clean_roads.gpkg", driver="GPKG")
show_extent("roads", roads)

# --- Farmland ---
print("Farmland...")
land = gpd.read_file(GEOFABRIK / "gis_osm_landuse_a_free_1.shp", bbox=BBOX)
print(land["fclass"].value_counts().to_string())
farm = clip_to_aoi(land[land["fclass"].isin(FARM_CLASSES)], ["Polygon", "MultiPolygon"])
farm = farm[["osm_id", "fclass", "name", "geometry"]]
farm.to_file(OUT / "clean_farmland.gpkg", driver="GPKG")
show_extent("farmland", farm)

AOI.to_file(OUT / "aoi_box.gpkg", driver="GPKG")

# --- Stats (measured in meters) ---
aoi_m2 = AOI.to_crs(MEASURE_CRS).area.sum()
roads_m = roads.to_crs(MEASURE_CRS)
roads_m["km"] = roads_m.length / 1000
farm_m2 = farm.to_crs(MEASURE_CRS).area.sum()

stats = {
    "aoi_box_wsen": [WEST, SOUTH, EAST, NORTH],
    "aoi_area_km2": round(aoi_m2 / 1e6, 1),
    "buildings": int(len(bld)),
    "buildings_footprint_ha": round(bld.to_crs(MEASURE_CRS).area.sum() / 1e4, 1),
    "roads_total_km": round(roads_m["km"].sum(), 1),
    "roads_real_km": round(roads_m.loc[roads_m.is_real_road, "km"].sum(), 1),
    "roads_by_type_km": roads_m.groupby("fclass")["km"].sum().round(1).sort_values(ascending=False).to_dict(),
    "farmland_polygons": int(len(farm)),
    "farmland_ha": round(farm_m2 / 1e4, 1),
    "farmland_pct_of_aoi": round(farm_m2 / aoi_m2 * 100, 1),
}
print(json.dumps(stats, indent=2))
(OUT / "stats.json").write_text(json.dumps(stats, indent=2))