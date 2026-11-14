# DEM + EMS notes

## Use these settings everywhere

- Area: `ee.Geometry.Rectangle([27.61, 45.46, 27.87, 45.74])`
- Dates: before 2024-08-15 → 2024-09-14, during 2024-09-14 → 2024-09-19, after 2024-09-19 → 2024-10-04
- Grid: EPSG:32635, 10 m pixels
- No data: `-9999`

## What is in the repo

- `export/`: EMS flood polygons, depth, and the Pechea area outline (GeoJSON). You can use these directly.
- `data/ems/pechea_flood_ems.gpkg`: the same EMS layers in one file.
- `dem+ems+sentinel1/`: the scripts.

The big files (`data/dem`, `data/sentinel-1`) are not in git. To get them, run the Colab notebooks and download the results from Drive.

## Which EMS map matches our Sentinel-1 image

EMS First Estimate = Sentinel-1, 14 Sept 2024, 04:22 UTC. This is the same image as our "during" scene, so **compare against this one**.

The other EMS maps (15 and 17 Sept) are later, when the water had already gone down, so they will not match well.

## Run (from the repo root)

```
python dem+ems+sentinel1/validate_vs_ems.py data/sentinel-1/flood_mask.tif
python dem+ems+sentinel1/plot_combined.py --save
```

## Current result

Sentinel-1 vs EMS First Estimate: IoU 0.49, F1 0.66.

The main error is the river in the south-west, which Sentinel-1 marks as flood. Next step: remove permanent water, then re-run the validation.

## Remember

- Don't commit `.tif` files
- DEM is 30 m (resampled to 10 m) and includes buildings and trees.
- EMS only mapped inside its area. Outside it means "not mapped", not "no flood".
