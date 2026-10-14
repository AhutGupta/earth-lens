"""Step 3: mosaic the Sentinel-2 tiles and clip them to Snohomish County.

For each band (blue, green, red, near-infrared):
  1. put every tile on one common grid covering the county's bounding box
  2. match each tile's brightness to the tiles already placed (using the overlap)
  3. blend the tiles with feathered edges, so there is no hard seam
  4. set every pixel outside the county outline to 0 (our "no data" value)
  5. save it as a GeoTIFF in data/clipped/
"""

import math
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.merge import merge
from shapely.geometry import box

BANDS = ["B02", "B03", "B04", "B08"]  # blue, green, red, near-infrared
RAMP_M = 5000  # tiles fade in/out over 5 km from their edge
OUT_DIR = Path("data/clipped")
OUT_DIR.mkdir(exist_ok=True)

county = gpd.read_file("data/snohomish_utm.gpkg").geometry.iloc[0]

# Snap the bounding box outward to the 10 m grid so pixels line up with the tiles.
minx, miny, maxx, maxy = county.bounds
bounds = (
    math.floor(minx / 10) * 10,
    math.floor(miny / 10) * 10,
    math.ceil(maxx / 10) * 10,
    math.ceil(maxy / 10) * 10,
)

def read_on_grid(path):
    """Read one tile onto the common county grid. Pixels it doesn't cover are 0."""
    with rasterio.open(path) as src:
        data, transform = merge([src], bounds=bounds, nodata=0)
        return data[0], transform, src.bounds, src.crs


def edge_weight(transform, shape, tile_bounds):
    """1 deep inside a tile, fading linearly to 0 at the tile's edge (RAMP_M wide)."""
    h, w = shape
    xs = transform.c + (np.arange(w) + 0.5) * transform.a
    ys = transform.f + (np.arange(h) + 0.5) * transform.e
    dx = np.minimum(xs - tile_bounds.left, tile_bounds.right - xs)
    dy = np.minimum(ys - tile_bounds.bottom, tile_bounds.top - ys)
    wx = np.clip(dx / RAMP_M, 0, 1).astype("float32")
    wy = np.clip(dy / RAMP_M, 0, 1).astype("float32")
    return np.minimum(wy[:, None], wx[None, :])


def tile_coverage(path):
    """How much of the county's bounding box this tile covers (for ordering)."""
    with rasterio.open(path) as src:
        return box(*src.bounds).intersection(box(*bounds)).area


for band in BANDS:
    paths = sorted(
        Path("data/s2").glob(f"*.SAFE/GRANULE/*/IMG_DATA/R10m/*_{band}_10m.jp2"),
        key=tile_coverage,
        reverse=True,  # the tile covering the most area is the brightness reference
    )
    print(f"{band}: blending {len(paths)} tiles")

    sum_wv = None  # running sum of (weight * value)
    sum_w = None  # running sum of weights
    for path in paths:
        dn, transform, tile_bounds, crs = read_on_grid(path)
        valid = dn > 0
        value = dn.astype("float32")
        del dn
        weight = edge_weight(transform, value.shape, tile_bounds) * valid

        if sum_w is None:
            sum_wv = np.zeros(value.shape, "float32")
            sum_w = np.zeros(value.shape, "float32")
        else:
            # Compare this tile with the mosaic so far, on a sparse sample of
            # the pixels where they overlap.
            s = (slice(None, None, 10), slice(None, None, 10))
            placed = sum_w[s] > 0
            both = valid[s] & placed
            if both.sum() > 1000:
                ref = sum_wv[s][both] / sum_w[s][both]
                new = value[s][both]
                # Match mean and spread: new' = a * new + b
                a = float(np.clip(ref.std() / new.std(), 0.5, 2.0))
                b = float(ref.mean() - a * new.mean())
                value = np.clip(a * value + b, 1, None)
                print(f"  {path.name.split('_')[0]}: gain a={a:.2f}, offset b={b:.0f}")
            else:
                print(f"  {path.name.split('_')[0]}: too little overlap, left as is")

        sum_wv += weight * value
        sum_w += weight
        del value, weight, valid

    mosaic = np.where(sum_w > 0, sum_wv / np.maximum(sum_w, 1e-6), 0)
    mosaic = np.rint(np.clip(mosaic, 0, 65535)).astype("uint16")[np.newaxis]
    del sum_wv, sum_w

    # True inside the county outline, False outside.
    inside = geometry_mask(
        [county], out_shape=mosaic.shape[1:], transform=transform, invert=True
    )
    mosaic[:, ~inside] = 0

    out_path = OUT_DIR / f"{band}.tif"
    with rasterio.open(
        out_path,
        "w",
        driver="GTiff",
        height=mosaic.shape[1],
        width=mosaic.shape[2],
        count=1,
        dtype=mosaic.dtype,
        crs=crs,
        transform=transform,
        nodata=0,
        compress="deflate",
    ) as dst:
        dst.write(mosaic)

    print(f"  saved {out_path}  shape={mosaic.shape[1:]}  dtype={mosaic.dtype}")
