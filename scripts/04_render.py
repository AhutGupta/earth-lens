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
from matplotlib.lines import Line2D
from pyproj import Transformer
from rasterio.enums import Resampling

DATE_LABEL = "Sentinel-2, 20 August 2023"

# Landmarks drawn on the true-color map: (name, longitude, latitude, kind).
# Note: 'lake' and 'peak' are rendered as clean text labels without markers.
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
    ("Mukilteo", -122.304, 47.948, "city"),
    ("Edmonds", -122.379, 47.810, "city"),
    ("Stanwood", -122.370, 48.241, "city"),
    ("Spada Lake", -121.729, 47.970, "lake"),
    ("Glacier Peak", -121.114, 48.112, "peak"),
    ("Mt Pilchuck", -121.798, 48.058, "peak"),
    ("Three Fingers", -121.686, 48.170, "peak"),
    ("Sloan Peak", -121.340, 48.041, "peak"),
]
MARKERS = {"city": "o", "industry": "*"}

ROADS_ZIP = Path("data/tl_2023_53_prisecroads.zip")
RIVERS_ZIP = Path("data/tl_2023_53061_linearwater.zip")
WATER_ZIP = Path("data/tl_2023_53061_areawater.zip")

MIN_LAKE_KM2 = 0.2
MIN_GLACIER_KM2 = 0.2
# Lon/lat (what we know places by) -> UTM zone 10N meters (what the rasters use).
TO_UTM = Transformer.from_crs("EPSG:4326", "EPSG:32610", always_xy=True)


def read_band(name, downsample):
    """Read one band as reflectance (0-1 floats). Pixels outside the county are NaN."""
    with rasterio.open(f"data/clipped/{name}.tif") as src:
        h, w = src.height // downsample, src.width // downsample
        dn = src.read(1, out_shape=(h, w), resampling=Resampling.average)
    outside = dn < 1
    refl = (dn.astype("float32") - 1000) / 10000
    refl = np.clip(refl, 0, 1)
    refl[outside] = np.nan
    return refl


def get_extent():
    """Map extent in UTM meters."""
    with rasterio.open("data/clipped/B04.tif") as src:
        b = src.bounds
    return (b.left, b.right, b.bottom, b.top)


def load(zip_path, county):
    """Read a TIGER file, convert to UTM, cut to the county."""
    layer = gpd.read_file(zip_path).to_crs("EPSG:32610")
    return gpd.clip(layer, county)


def draw_layers(ax):
    """Draw roads, rivers, lakes, glaciers, and Puget Sound with legend box."""
    county = gpd.read_file("data/snohomish_utm.gpkg")
    handles = []
    outline = [pe.withStroke(linewidth=2.5, foreground="white")]

    if WATER_ZIP.exists():
        water = load(WATER_ZIP, county)
        water = water.assign(km2=water.area / 1e6)

        puget_sound = water[water["MTFCC"] == "H2051"]
        lakes = water[water["MTFCC"].isin(["H2030", "H2040"]) & (water.km2 > MIN_LAKE_KM2)]
        glaciers = water[(water["MTFCC"] == "H2081") & (water.km2 > MIN_GLACIER_KM2)]
        wide_rivers = water[water["MTFCC"] == "H3010"]

        # Solid polygon fill for Puget Sound (no dots/markers)
        puget_sound.plot(ax=ax, facecolor="#0288d1", alpha=0.55, edgecolor="#01579b", linewidth=0.8)
        
        # Lakes and rivers
        lakes.plot(ax=ax, facecolor="#0288d1", alpha=0.4, edgecolor="#4fc3f7", linewidth=1.1)
        wide_rivers.plot(ax=ax, facecolor="#4fc3f7", edgecolor="none")

        # Glaciers: Electric cyan
        glaciers.plot(ax=ax, facecolor="#e0f7fa", alpha=0.6, edgecolor="#00e5ff", linewidth=1.2, linestyle="--")

        # Puget Sound label placed strictly offshore (far west into open water)
        puget_x, puget_y = TO_UTM.transform(-122.480, 47.920)
        ax.text(
            puget_x, puget_y, "Puget Sound", fontsize=10, fontstyle="italic",
            fontweight="bold", color="#01579b", path_effects=outline, rotation=-15,
        )

        handles += [
            Line2D([0], [0], color="#01579b", lw=2, label="Puget Sound"),
            Line2D([0], [0], color="#4fc3f7", lw=2, label="Lakes & rivers"),
            Line2D([0], [0], color="#00e5ff", lw=2, ls="--", label="Glaciers"),
        ]

    if RIVERS_ZIP.exists():
        streams = load(RIVERS_ZIP, county)
        # Filter out non-line geometries or point noise along coastline
        streams = streams[streams.geometry.type.isin(["LineString", "MultiLineString"])]
        rivers = streams[streams["FULLNAME"].fillna("").str.contains(r"\bRiv\b")]
        rivers.plot(ax=ax, color="#4fc3f7", linewidth=0.8)

    if ROADS_ZIP.exists():
        roads = load(ROADS_ZIP, county)
        roads[roads["RTTYP"] == "S"].plot(ax=ax, color="#ffb74d", linewidth=0.6)
        roads[roads["RTTYP"].isin(["I", "U"])].plot(ax=ax, color="#ffee58", linewidth=1.4)

        handles += [
            Line2D([0], [0], color="#ffee58", lw=2, label="Interstate / US highway"),
            Line2D([0], [0], color="#ffb74d", lw=2, label="State route"),
        ]

    ax.legend(
        handles=handles,
        loc="lower right",
        fontsize=8.5,
        facecolor="white",
        framealpha=0.92,
        edgecolor="#cccccc",
        borderpad=0.8,
        handletextpad=0.6,
    )


def draw_landmarks(ax):
    """Plot landmarks: cities get markers; lakes/peaks get cleanly offset text labels."""
    outline = [pe.withStroke(linewidth=2.5, foreground="white")]
    
    # Custom offsets for peaks and lakes so text doesn't obscure terrain features
    OFFSETS = {
        "Glacier Peak": (10, -10),
        "Mt Pilchuck": (10, 8),
        "Sloan Peak": (10, -6),
        "Three Fingers": (8, 6),
        "Spada Lake": (0, 12),
    }

    for name, lon, lat, kind in LANDMARKS:
        x, y = TO_UTM.transform(lon, lat)
        if kind in MARKERS:
            ax.plot(x, y, MARKERS[kind], color="black", markersize=4.5)
            ax.annotate(
                name, (x, y), xytext=(4, 4), textcoords="offset points",
                fontsize=7.5, fontweight="normal", path_effects=outline,
            )
        else:
            font_style = "italic" if kind == "lake" else "normal"
            offset = OFFSETS.get(name, (5, 5))
            
            # Draw a small subtle dot for peaks so the actual summit location is clear
            if kind == "peak":
                ax.plot(x, y, "^", color="#3e2723", markersize=4)
                
            ax.annotate(
                name, (x, y), xytext=offset, textcoords="offset points",
                fontsize=8, fontstyle=font_style, fontweight="bold",
                color="#1a237e" if kind == "lake" else "#3e2723",
                path_effects=outline,
            )


def render(downsample, dpi, out_dir):
    """Make both true-color and annotated NDVI maps."""
    out_dir.mkdir(parents=True, exist_ok=True)
    extent = get_extent()
    blue, green, red, nir = (read_band(b, downsample) for b in ["B02", "B03", "B04", "B08"])

    with np.errstate(invalid="ignore", divide="ignore"):
        ndvi = np.where(nir + red > 0.01, (nir - red) / (nir + red), np.nan)

    rgb = np.dstack([red, green, blue])
    del red, green, nir
    lo, hi = np.nanpercentile(rgb[::20, ::20], [2, 98])
    rgb -= lo
    rgb /= (hi - lo)
    np.clip(rgb, 0, 1, out=rgb)
    rgb **= 1 / 1.4
    rgb[np.isnan(blue)] = 1
    del blue

    # True Color Map
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.imshow(rgb, extent=extent)
    draw_layers(ax)
    draw_landmarks(ax)
    ax.set_xlim(extent[0], extent[1])
    ax.set_ylim(extent[2], extent[3])
    ax.set_title(f"Snohomish County, WA: true color\n{DATE_LABEL}", fontsize=14)
    ax.set_axis_off()
    fig.savefig(out_dir / "true_color.png", dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    del rgb

    # NDVI Map with key terrain feature callouts
    fig, ax = plt.subplots(figsize=(16, 9))
    im = ax.imshow(ndvi, cmap="RdYlGn", vmin=-0.2, vmax=0.9, extent=extent)
    ax.set_title(f"Snohomish County, WA: NDVI (vegetation)\n{DATE_LABEL}", fontsize=14)
    ax.set_axis_off()
    fig.colorbar(im, ax=ax, shrink=0.7, label="NDVI")

    # Explanatory annotations on NDVI map
    outline = [pe.withStroke(linewidth=2.5, foreground="white")]
    
    # Dense Forest Foothills (High NDVI)
    x_forest, y_forest = TO_UTM.transform(-121.800, 47.920)
    ax.annotate(
        "Dense Conifer Forest\n(High NDVI ~ 0.8)", (x_forest, y_forest),
        xytext=(-80, -20), textcoords="offset points",
        fontsize=8, fontweight="bold", color="#1b5e20", path_effects=outline,
        arrowprops=dict(arrowstyle="->", color="#1b5e20", lw=1.2),
    )

    # High Alpine Bare Rock & Snow (Low NDVI)
    x_peak, y_peak = TO_UTM.transform(-121.114, 48.112)
    ax.annotate(
        "Glaciers & Exposed Rock\n(Low / Negative NDVI)", (x_peak, y_peak),
        xytext=(-100, 30), textcoords="offset points",
        fontsize=8, fontweight="bold", color="#b71c1c", path_effects=outline,
        arrowprops=dict(arrowstyle="->", color="#b71c1c", lw=1.2),
    )

    # Boeing / Urban Infrastructure (Low NDVI / Red)
    x_urban, y_urban = TO_UTM.transform(-122.273, 47.923)
    ax.annotate(
        "Urban & Built Surface\n(Boeing Factory / Runway)", (x_urban, y_urban),
        xytext=(-120, -30), textcoords="offset points",
        fontsize=8, fontweight="bold", color="#b71c1c", path_effects=outline,
        arrowprops=dict(arrowstyle="->", color="#b71c1c", lw=1.2),
    )

    fig.savefig(out_dir / "ndvi.png", dpi=dpi, bbox_inches="tight")
    plt.close(fig)

    print(f"saved true_color.png and ndvi.png in {out_dir}/")
    print(f"NDVI range: {np.nanmin(ndvi):.2f} to {np.nanmax(ndvi):.2f}")


render(downsample=4, dpi=200, out_dir=Path("outputs"))

if "--hires" in sys.argv:
    render(downsample=1, dpi=800, out_dir=Path("outputs/hires"))