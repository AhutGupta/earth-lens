# earth-lens

Exploring environmental change in Snohomish County through open satellite, weather, and geospatial data.

## Project motivation
I live in Snohomish County, Washington. I wanted to understand how the landscape around me has changed. Not just through anecdotes or weather impressions, but through open satellite and environmental data.

## Study area
Snohomish County, Washington: a region spanning Puget Sound shoreline, river valleys, farmland, growing suburbs, and the Cascade Mountains — a compact place with a wide range of land cover to observe from space.

## Data
| Dataset | What it provides |
| --- | --- |
| Sentinel-2 L2A | Satellite imagery: true color and vegetation (NDVI) |
| US Census county boundaries | Snohomish County outline |

_More datasets will be added when they are actually used._

## Current result
![True-color Snohomish County](outputs/true_color.png)
![NDVI Snohomish County](outputs/ndvi.png)

Sentinel-2, 20 August 2023. Full story: [Seeing My Home from Space](stories/01-seeing-snohomish-from-space.md). Full-resolution (10 m) versions are not in Git; see the story for where to find them.

## Analysis
Three Sentinel-2 tiles were matched in brightness, blended along their overlaps, and clipped to the county outline. True color comes from the red, green and blue bands. NDVI is (NIR − Red) / (NIR + Red).

To rebuild everything (after downloading the data, see [`data/README.md`](data/README.md)):
```sh
uv run python scripts/01_boundary.py      # county outline + locator map
uv run python scripts/02_inspect_scenes.py # check CRS, resolution, tile coverage
uv run python scripts/03_mosaic_clip.py   # mosaic tiles, clip to county
uv run python scripts/04_render.py        # maps (add --hires for full 10 m detail)
```

## Data flow
```
Data source → processing → analysis → artifact
```

## Stories
Short write-ups tied to milestones live in [`stories/`](stories/):

- [01 – Seeing My Home from Space](stories/01-seeing-snohomish-from-space.md)

## What I am learning
_Geospatial concepts met along the way (coordinate systems, rasters vs. vectors, cloud cover, ...)._

## Limitations
_Scientific and data caveats (resolution, cloud cover, seasonal variation, ...)._

## Technical setup
### Docker (recommended)
Geospatial packages such as `rasterio` and GDAL can trigger long C++ builds on macOS (especially Apple Silicon). Docker avoids this by using pre-built Linux wheels, so it works the same on any host OS.

```sh
docker build -t earth-lens .
docker run --rm earth-lens
```

### Local setup
Requires [uv](https://docs.astral.sh/uv/) and Python 3.12.

```sh
uv sync            # create the environment and install dependencies
uv run pytest      # run tests
uv run ruff check . && uv run ruff format .   # lint and format
uv run earth-lens  # run the command-line entry point
```

Layout: `src/` reusable code, `scripts/` standalone scripts, `data/` local datasets (not in Git), `outputs/` publishable visuals, `stories/` write-ups, `tests/` tests.
