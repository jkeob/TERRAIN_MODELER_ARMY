# -*- coding: utf-8 -*-
import sys, rasterio, numpy as np
from pathlib import Path

dem_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dem_1m.tif")
out_obj  = dem_path.with_suffix(".obj")
GRID_STEP = 1  # set to 2–4 for a lighter mesh

with rasterio.open(dem_path) as src:
    z = src.read(1).astype(float)
    if src.nodata is not None:
        z[z==src.nodata] = np.nan
    z = z[::GRID_STEP, ::GRID_STEP]
    h, w = z.shape
    x0, dx, _, y0, _, dy = src.transform.to_gdal()
    xs = x0 + dx * np.arange(w)
    ys = y0 + dy * np.arange(h)
    X, Y = np.meshgrid(xs, ys)
    X -= X.min(); Y -= Y.min()

# simple nearest fill so OBJ has no holes
mask = np.isnan(z)
if mask.any():
    for j in range(w):
        col = z[:, j]; idx = np.where(~np.isnan(col))[0]
        if idx.size:
            z[:idx[0], j] = col[idx[0]]; z[idx[-1]+1:, j] = col[idx[-1]]
            for a,b in zip(idx, idx[1:]): z[a:b, j] = col[a]
    for i in range(h):
        row = z[i, :]; idx = np.where(~np.isnan(row))[0]
        if idx.size:
            z[i, :idx[0]] = row[idx[0]]; z[i, idx[-1]+1:] = row[idx[-1]]
            for a,b in zip(idx, idx[1:]): z[i, a:b] = row[a]

verts = np.column_stack([X.ravel(), Y.ravel(), z.ravel()])
faces = []
for r in range(h-1):
    base = r*w
    for c in range(w-1):
        i = base + c
        # OBJ uses 1-based indices
        faces.append([i+1, i+2, i+1+w])
        faces.append([i+2, i+2+w, i+1+w])

with open(out_obj, "w", newline="\n") as f:
    for v in verts:
        f.write(f"v {v[0]:.3f} {v[1]:.3f} {v[2]:.3f}\n")
    for a,b,c in faces:
        f.write(f"f {a} {b} {c}\n")

print(f"OK → {out_obj}")
