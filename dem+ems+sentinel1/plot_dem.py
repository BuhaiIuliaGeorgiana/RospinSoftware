"""Deseneaza dem_m.tif (elevatie) si slope_deg.tif (panta) din exportul Copernicus DEM.

Folosire:  python plot_dem.py [folder_cu_tif-uri] [--save]
Fara --save se deschide o fereastra; cu --save se scrie dem_preview.png langa fisiere.
Necesita: rasterio, numpy, matplotlib.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import rasterio

NODATA = -9999

args = [a for a in sys.argv[1:] if not a.startswith("--")]
folder = Path(args[0]) if args else Path(".")


def citeste(nume):
    with rasterio.open(folder / nume) as src:
        a = src.read(1).astype("float32")
        b = src.bounds
        crs = src.crs
    a[(a == NODATA) | ~np.isfinite(a)] = np.nan   # NaN = in afara zonei / fara date
    return a, (b.left, b.right, b.bottom, b.top), crs


dem, extent, crs = citeste("./data/dem/dem_m.tif")
panta, _, _ = citeste("./data/dem/slope_deg.tif")

# Hillshade simplu din DEM (pixeli de 10 m), doar pentru relief in desen.
dy, dx = np.gradient(np.nan_to_num(dem, nan=float(np.nanmean(dem))), 10)
az, alt = np.radians(315), np.radians(45)
slope_r, aspect = np.arctan(np.hypot(dx, dy)), np.arctan2(-dx, dy)
hill = (np.sin(alt) * np.cos(slope_r)
        + np.cos(alt) * np.sin(slope_r) * np.cos(az - aspect))
hill[np.isnan(dem)] = np.nan

fig, ax = plt.subplots(1, 2, figsize=(13, 7), constrained_layout=True)

ax[0].imshow(hill, extent=extent, cmap="gray", vmin=0, vmax=1)
im0 = ax[0].imshow(dem, extent=extent, cmap="terrain", alpha=0.7,
                   vmin=np.nanpercentile(dem, 1), vmax=np.nanpercentile(dem, 99))
fig.colorbar(im0, ax=ax[0], shrink=0.8, label="elevatie (m, EGM2008)")
ax[0].set_title(f"Copernicus GLO-30 DSM  (min {np.nanmin(dem):.0f} m, max {np.nanmax(dem):.0f} m)")

im1 = ax[1].imshow(panta, extent=extent, cmap="YlOrRd", vmin=0,
                   vmax=np.nanpercentile(panta, 99))
fig.colorbar(im1, ax=ax[1], shrink=0.8, label="panta (grade)")
ax[1].set_title("Panta (calculata la 30 m)")

for a in ax:
    a.set_xlabel(f"E ({crs}, m)")
    a.set_ylabel("N (m)")
    a.ticklabel_format(style="plain")
    a.tick_params(axis="x", labelrotation=30)

if "--save" in sys.argv:
    iesire = folder / "dem_preview.png"
    fig.savefig(iesire, dpi=150)
    print("salvat:", iesire)
else:
    plt.show()
