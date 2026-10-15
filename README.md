## Data

| Dataset | What it provides |
| --- | --- |
| Sentinel-2 L2A, July 2026 | Satellite imagery: true color and vegetation (NDVI) |
| US Census county boundaries (cb_2023) | Snohomish County outline |
| Census TIGER/Line 2023: roads, linear water, area water | Roads, rivers, lakes and glaciers drawn on the true-color map |

Credits: Contains modified Copernicus Sentinel data [2026]. Boundaries, roads and water features: US Census Bureau.

_More datasets will be added when they are actually used._

## Current result

![True-color Snohomish County](outputs/true_color.png)
![NDVI Snohomish County](outputs/ndvi.png)

Sentinel-2, July 2026. Full story: [Seeing Snohomish from Space](stories/01-seeing-snohomish-from-space.md).

Full-resolution (10 m) versions are not in Git; see the story for where to find them.

## Analysis

Sentinel-2 tiles from two acquisition dates were matched in brightness, blended along their overlaps, and clipped to the county outline. True color uses the red, green and blue bands with a contrast stretch and a gamma lift. NDVI is (NIR − Red) / (NIR + Red): healthy plants reflect near-infrared and absorb red, so dense forest scores high, while water, snow, rock and built surfaces score low. Roads, rivers, lakes and glaciers come from Census TIGER/Line. 
Puget Sound is drawn as a polygon, because the imagery is masked outside the county. Landmark positions were placed by hand and are approximate.

To rebuild everything (after downloading the data, see [`data/README.md`](data/README.md)):

```sh
uv run python scripts/01_boundary.py        # county outline + locator map
uv run python scripts/02_inspect_scenes.py  # check CRS, resolution, tile coverage
uv run python scripts/03_mosaic_clip.py     # mosaic tiles, clip to county
uv run python scripts/04_render.py          # maps (add --hires for full 10 m detail)
```

## Notes

- High peaks still hold snow in July, which reads as low NDVI. NDVI cannot tell snow, rock, water and pavement apart.
- Landmark positions are approximate.

## What I am learning

- **Finding and choosing data:** the Copernicus products, tiles, processing levels, and how cloud cover and haze affect a scene.
- **Coordinate systems:** reprojecting to UTM zone 10N so layers line up and areas are in meters.
- **Rasters vs. vectors:** pixels for imagery, geometry for boundaries, roads and rivers.
- **Checking coverage:** confirming the tiles cover the whole county before processing.
- **Mosaicking:** matching brightness and blending tiles from different days.
- **Making a good picture:** reflectance scaling, contrast stretches and gamma.
- **NDVI:** what it shows and what it can't tell apart.
- **Map making:** layers, a polygon for Puget Sound, landmarks by real coordinates, and label offsets.

## Stories

Short write-ups tied to milestones live in [`stories/`](stories/):

- [01 – Seeing Snohomish from Space](stories/01-seeing-snohomish-from-space.md)