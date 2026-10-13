"""Step 2: inspect the downloaded Sentinel-2 products.

For each .SAFE folder in data/s2/, print the tile, the 10 m red band's CRS,
size and resolution, and how much of Snohomish County the tile covers.
"""

from pathlib import Path

import geopandas as gpd
import rasterio
from shapely.geometry import box
from shapely.ops import unary_union

county = gpd.read_file("data/snohomish_utm.gpkg").geometry.iloc[0]
print(f"County area: {county.area / 1e6:.0f} km²\n")

footprints = []

for safe in sorted(Path("data/s2").glob("*.SAFE")):
    # Red band at 10 m. Other bands follow the same naming pattern.
    matches = list(safe.glob("GRANULE/*/IMG_DATA/R10m/*_B04_10m.jp2"))
    if not matches:
        print(f"{safe.name}: no B04 10m file found, skipping\n")
        continue

    with rasterio.open(matches[0]) as src:
        footprint = box(*src.bounds)
        footprints.append(footprint)
        covered = county.intersection(footprint).area / county.area
        print(safe.name)
        print("  CRS:       ", src.crs)
        print("  Size (px): ", src.width, "x", src.height)
        print("  Pixel size:", src.res, "meters")
        print("  Dtype:     ", src.dtypes[0])
        print(f"  Covers {covered:.0%} of the county\n")

# Overlaps are counted once here, so this is the real combined coverage.
union = unary_union(footprints)
combined = county.intersection(union).area / county.area
print(f"All tiles together cover {combined:.0%} of the county")
