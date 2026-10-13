"""Step 4: render the true-color and NDVI maps from the clipped bands.

Input:   data/clipped/B02, B03, B04, B08 .tif        (made by step 3)
Output:  outputs/true_color.png, outputs/ndvi.png     web size, goes in Git
         outputs/hires/*.png  (only with --hires)     full 10 m detail, NOT in Git;
                                                      publish via a GitHub Release or blog

Run:  uv run python scripts/04_render.py             quick, web size
      uv run python scripts/04_render.py --hires     slow, needs ~4 GB of free RAM
"""

import sys
from pathlib import Path

import geopandas as gpd
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from pyproj import Transformer
from rasterio.enums import Resampling

DATE_LABEL = "Sentinel-2, 20 August 2023"

# Landmarks drawn on the true-color map: (name, longitude, latitude, kind).
# Positions are approximate (read off a map). If one looks off on the image,
# nudge its lon/lat. No extra data download is needed for these.
LANDMARKS = [
    ("Everett", -122.202, 47.979, "city"),
    ("Marysville", -122.177, 48.052, "city"),
    ("Arlington", -122.125, 48.199, "city"),
    ("Lake Stevens", -122.064, 48.015, "city"),
    ("Snohomish", -122.098, 47.913, "city"),
    ("Monroe", -121.972, 47.855, "city"),
    ("Granite Falls", -121.969, 48.084, "city"),
    ("Darrington", -121.602, 48.255, "city"),
    ("Lynnwood", -122.315, 47.821, "city"),
    ("Boeing Everett\nfactory", -122.273, 47.923, "industry"),
    ("Spada Lake", -121.729, 47.970, "lake"),
    ("Glacier Peak", -121.114, 48.112, "peak"),
]
MARKERS = {"city": "o", "industry": "*", "lake": "s", "peak": "^"}

# Optional layers. Download these from the Census TIGER/Line site into data/ to
# turn them on (see the story/README). If the file is missing, it is skipped.
ROADS_ZIP = Path("data/tl_2023_53_prisecroads.zip")  # primary & secondary roads, WA
WATER_ZIP = Path("data/tl_2023_53061_linearwater.zip")  # rivers and streams, Snohomish

# Lon/lat (what we know places by) -> UTM zone 10N meters (what the rasters use).
TO_UTM = Transformer.from_crs("EPSG:4326", "EPSG:32610", always_xy=True)


def read_band(name, downsample):
    """Read one band as reflectance (0-1 floats). Pixels outside the county are NaN.

    downsample=4 averages 4x4 blocks of 10 m pixels into one 40 m pixel.
    downsample=1 keeps full 10 m detail.
    """
    with rasterio.open(f"data/clipped/{name}.tif") as src:
        h, w = src.height // downsample, src.width // downsample
        dn = src.read(1, out_shape=(h, w), resampling=Resampling.average)
    outside = dn < 1  # 0 = nodata; averaging can leave tiny values near the edge
    # Sentinel-2 files from processing baseline 04.00+ store
    # reflectance * 10000 + 1000, so undo both to get 0-1 reflectance.
    refl = (dn.astype("float32") - 1000) / 10000
    refl = np.clip(refl, 0, 1)
    refl[outside] = np.nan
    return refl


def get_extent():
    """Map extent in UTM meters, so we can plot landmarks in real coordinates."""
    with rasterio.open("data/clipped/B04.tif") as src:
        b = src.bounds
    return (b.left, b.right, b.bottom, b.top)


def draw_optional_layers(ax):
    """Add roads and rivers if their files have been downloaded."""
    county = gpd.read_file("data/snohomish_utm.gpkg")
    if ROADS_ZIP.exists():
        roads = gpd.read_file(ROADS_ZIP).to_crs("EPSG:32610")
        roads = gpd.clip(roads[roads["RTTYP"].isin(["I", "U"])], county)  # I-5, US-2...
        roads.plot(ax=ax, color="#ffd54f", linewidth=1.2)
    if WATER_ZIP.exists():
        water = gpd.read_file(WATER_ZIP).to_crs("EPSG:32610")
        rivers = water[water["FULLNAME"].fillna("").str.contains("River")]
        gpd.clip(rivers, county).plot(ax=ax, color="#4fc3f7", linewidth=0.8)


def draw_landmarks(ax):
    """Plot each landmark as a marker plus a label with a white outline."""
    outline = [pe.withStroke(linewidth=3, foreground="white")]
    for name, lon, lat, kind in LANDMARKS:
        x, y = TO_UTM.transform(lon, lat)
        ax.plot(x, y, MARKERS[kind], color="black", markersize=6)
        ax.annotate(
            name, (x, y), xytext=(5, 5), textcoords="offset points",
            fontsize=9, path_effects=outline,
        )


def render(downsample, dpi, out_dir):
    """Make both maps. Bigger dpi + smaller downsample = sharper, bigger files."""
    out_dir.mkdir(parents=True, exist_ok=True)
    extent = get_extent()
    blue, green, red, nir = (read_band(b, downsample) for b in ["B02", "B03", "B04", "B08"])

    # NDVI = (NIR - Red) / (NIR + Red). Plants absorb red and reflect near-infrared.
    # Skip pixels where the sum is ~0 (dividing by ~0 gives garbage like -1 or 1).
    with np.errstate(invalid="ignore", divide="ignore"):
        ndvi = np.where(nir + red > 0.01, (nir - red) / (nir + red), np.nan)

    # True color = red, green, blue stacked as image channels.
    # Raw reflectance looks dark and flat, so stretch contrast between the 2nd and
    # 98th percentile (sampled sparsely to save time), then brighten with gamma.
    rgb = np.dstack([red, green, blue])
    del red, green, nir
    lo, hi = np.nanpercentile(rgb[::20, ::20], [2, 98])
    rgb -= lo
    rgb /= hi - lo
    np.clip(rgb, 0, 1, out=rgb)
    rgb **= 1 / 1.4
    rgb[np.isnan(blue)] = 1  # white outside the county
    del blue

    # imshow with extent= places the image in real UTM meters, so landmarks
    # (converted to UTM) land in the right spot.
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.imshow(rgb, extent=extent)
    draw_optional_layers(ax)
    draw_landmarks(ax)
    ax.set_xlim(extent[0], extent[1])  # geopandas may change the limits; reset
    ax.set_ylim(extent[2], extent[3])
    ax.set_title(f"Snohomish County, WA: true color\n{DATE_LABEL}", fontsize=14)
    ax.set_axis_off()
    fig.savefig(out_dir / "true_color.png", dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    del rgb

    # RdYlGn: red = bare/built, green = dense vegetation. vmin/vmax fix the scale
    # so different dates can be compared with the same colors later.
    fig, ax = plt.subplots(figsize=(16, 9))
    im = ax.imshow(ndvi, cmap="RdYlGn", vmin=-0.2, vmax=0.9, extent=extent)
    ax.set_title(f"Snohomish County, WA: NDVI (vegetation)\n{DATE_LABEL}", fontsize=14)
    ax.set_axis_off()
    fig.colorbar(im, ax=ax, shrink=0.7, label="NDVI")
    fig.savefig(out_dir / "ndvi.png", dpi=dpi, bbox_inches="tight")
    plt.close(fig)

    print(f"saved true_color.png and ndvi.png in {out_dir}/")
    print(f"NDVI range: {np.nanmin(ndvi):.2f} to {np.nanmax(ndvi):.2f}")


# Web size: 40 m pixels at 200 dpi = ~3,000 px wide, about 3 MB. Fine for Git.
render(downsample=4, dpi=200, out_dir=Path("outputs"))

# Full detail: 10 m pixels at 800 dpi = ~12,000 px wide. Too big for Git, so
# it goes in outputs/hires/ (ignored by Git) for publishing elsewhere.
if "--hires" in sys.argv:
    render(downsample=1, dpi=800, out_dir=Path("outputs/hires"))
