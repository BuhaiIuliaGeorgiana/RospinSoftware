from pathlib import Path

WEST, SOUTH, EAST, NORTH = 27.74, 45.58, 27.86, 45.68
BBOX = (WEST, SOUTH, EAST, NORTH)

ROOT = Path(__file__).resolve().parents[2] 
RAW = ROOT / "data" / "raw"
GEOFABRIK = RAW / "romania" 
OUT = ROOT / "data" / "osm" 
MEASURE_CRS = 3844 

RAW.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)