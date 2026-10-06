# earth-lens

Exploring environmental change in Snohomish County through open satellite, weather, and geospatial data.

## Project motivation
I live in Snohomish County, Washington. I wanted to understand how the landscape around me has changed. Not just through anecdotes or weather impressions, but through open satellite and environmental data.

## Study area
Snohomish County, Washington: a region spanning Puget Sound shoreline, river valleys, farmland, growing suburbs, and the Cascade Mountains — a compact place with a wide range of land cover to observe from space.

## Data
| Dataset | What it provides |
| --- | --- |
| _Satellite imagery (e.g. Sentinel-2, Landsat)_ | Land cover and vegetation change over time |
| _Weather data (e.g. NOAA)_ | Temperature and precipitation context |
| _Boundaries (e.g. US Census)_ | County and sub-area outlines |

_Placeholders; updated as datasets are actually used._

## Current result
_The best map or figure will go here, saved in [`outputs/`](outputs/)._

## Analysis
_Plain-language explanation of what was done. (To be written.)_

## Data flow
```
Data source → processing → analysis → artifact
```

## Stories
Short write-ups tied to milestones live in [`stories/`](stories/):

- [01 – Seeing Snohomish from space](stories/01-seeing-snohomish-from-space.md) (draft)

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
