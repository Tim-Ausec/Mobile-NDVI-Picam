import os
import numpy as np
import rasterio
import matplotlib.pyplot as plt
import pandas as pd

# === CONFIGURATION ===
NDVI_DIR = "/home/agrovolo/Desktop/ndvi_captures"  # folder with your .tif files
EXPORT_MATRIX = True                         # save pixel values to CSV
LIMIT_PRINT = 10                             # how many rows/cols to print in console

# === FIND MOST RECENT NDVI FILE ===
tiff_files = [f for f in os.listdir(NDVI_DIR) if f.endswith(".tif")]
if not tiff_files:
    raise FileNotFoundError("No NDVI .tif files found!")

tiff_files.sort()
latest_tiff = os.path.join(NDVI_DIR, tiff_files[-1])
print(f"[INFO] Reading: {latest_tiff}")

# === READ THE TIFF ===
with rasterio.open(latest_tiff) as src:
    ndvi = src.read(1)           # band 1 = NDVI values
    meta = src.meta
    print(f"[INFO] CRS: {src.crs}")
    print(f"[INFO] Shape: {ndvi.shape}")
    print(f"[INFO] Resolution: {src.res}")

# === CLEAN DATA ===
ndvi = np.where(np.isfinite(ndvi), ndvi, np.nan)

# === STATS ===
print("\n--- NDVI STATS ---")
print(f"Min: {np.nanmin(ndvi):.3f}")
print(f"Max: {np.nanmax(ndvi):.3f}")
print(f"Mean: {np.nanmean(ndvi):.3f}")
print(f"Std Dev: {np.nanstd(ndvi):.3f}")

# === MATRIX PREVIEW ===
print("\n--- NDVI MATRIX PREVIEW ---")
rows, cols = ndvi.shape
for i in range(min(LIMIT_PRINT, rows)):
    row_values = [f"{v:6.2f}" if not np.isnan(v) else "  nan " for v in ndvi[i, :LIMIT_PRINT]]
    print(" ".join(row_values))
print(f"... ({rows}×{cols} total pixels)")

# === OPTIONAL EXPORT TO CSV ===
if EXPORT_MATRIX:
    out_csv = latest_tiff.replace(".tif", "_matrix.csv")
    np.savetxt(out_csv, ndvi, delimiter=",", fmt="%.5f", header="NDVI pixel matrix")
    print(f"[INFO] Full NDVI matrix saved to: {out_csv}")

# === VISUALIZE ===
plt.figure(figsize=(8,6))
plt.imshow(ndvi, cmap="RdYlGn", vmin=-1, vmax=1)
plt.colorbar(label="NDVI")
plt.title("NDVI Pixel Matrix Visualization")
plt.xlabel("X Pixels")
plt.ylabel("Y Pixels")
plt.tight_layout()
plt.show()
