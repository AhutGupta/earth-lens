# Seeing Snohomish County from Space

I have always loved maps. A good map takes a huge, messy piece of the real world and makes it something you can hold in your hands and understand at a glance. It tells you where you are, how things connect, and what is worth a closer look.

### 📊 Project Snapshot
> - **Satellite Data:** Copernicus Sentinel-2 L2A (10 m spatial resolution)
> - **Spectral Bands:** Band 2 (Blue), Band 3 (Green), Band 4 (Red), Band 8 (NIR)
> - **Vector Data:** US Census Bureau TIGER/Line (County boundary, roads, rivers, lakes)
> - **Target Region:** Snohomish County, WA (~2,100 sq. miles)
> - **Tech Stack:** Python (`rasterio`, `geopandas`, `matplotlib`, `shapely`)

## Why this project

These days there is more satellite data than ever, and a lot of it is free. Satellites photograph the whole planet every few days, and anyone with a laptop can download the files. I'm a software engineer, and I wanted to learn how to turn that raw data into something meaningful, and to learn geospatial concepts along the way. I also wanted the result to be beautiful: maps as a kind of art.

So I decided to start simple, and to start at home. Snohomish County, Washington, is where I live, and it turns out to be a perfect first subject. In one county there is saltwater, river deltas, farmland, cities, dense forest, alpine country and a volcano.

I was also curious about NDVI, a vegetation index that you calculate from just two bands of light. The formula is a single line, and yet it reveals a surprising amount about a landscape.

## Where the data comes from

The imagery is from **Sentinel-2**, a pair of European Space Agency satellites that photograph the Earth's land at 10 meter detail. I downloaded it for free from the Copernicus Browser, picking scenes with little cloud cover, around the peak of summer 2026. The county boundary, roads, rivers and lakes come from the US Census Bureau.

## How it came together

Four small Python scripts, run in order:

1. **`01_boundary.py`** pulls out the county outline and makes a locator map.
2. **`02_inspect_scenes.py`** checks that the downloaded tiles actually cover the whole county.
3. **`03_mosaic_clip.py`** stitches the tiles into one image, evens out their brightness, and trims it to the county shape.
4. **`04_render.py`** draws the final maps, with the roads, rivers, glaciers, Puget Sound and landmarks on top.

It took several rounds to get right. My first scene was hazy, so I switched dates. The next one was missing a tile, so I added a second one, taken two days apart, to complete the map. Every round taught me something.

## The true-color map

![True-color Snohomish County, July 2026](../outputs/true_color.png)

True color is the picture your eyes would see from space: the red, green and blue bands, stretched a little for contrast.

Start at the left edge, in the deep water of **Puget Sound**. Moving east, the shoreline runs past **Mukilteo** and **Edmonds** to the **Port of Everett**, where the **Snohomish River** spreads into its delta. In the north-west are the checkerboard farm fields near **Stanwood** and **Marysville**, and the cities line up along the Interstate 5 corridor, with **Lake Stevens** dark against the streets around it.

Further east the city grid gives way to dark green foothill forest, with **Spada Lake** lying in a long valley. Then the Cascades begin. **Three Fingers**, **Vesper Peak**, **Sloan Peak**, **Kyes Peak** and **Columbia Peak** rise as pale, rocky ridges with July snow still in the gullies. At the far east edge is **Glacier Peak**, a volcano, ringed by glaciers.

Getting the details onto the map was half the fun: drawing Puget Sound as a polygon, adding the roads and rivers as layers, placing peaks and cities by their real coordinates, and nudging the labels so the text doesn't cover what it names.

## The NDVI map

![NDVI Snohomish County, July 2026](../outputs/ndvi.png)

NDVI (Normalized Difference Vegetation Index) is a metric that quantifies green vegetation health and density by measuring the difference between two kinds of light: red and near-infrared. Healthy plants absorb red and reflect a lot of near-infrared, so the difference between them shows how green and leafy a place is. Dense forest comes out dark green. Everything that isn't leafy shows up red or yellow.

The same satellite pixels that made the true-color map now tell a different story:

- The **glaciers and snowfields** around Glacier Peak and the high ridges glow red.
- **Lakes**, including Spada Lake and Lake Stevens, stand out as red shapes.
- The **river delta** at Everett is a tangle of red and dark water.
- **Cities, roads and the Boeing factory and runway area** near Mukilteo show up in yellow and orange.
- The **farm fields** in the north-west form a patchwork of greens and yellows.

One simple formula, and the landscape sorts itself into plants and not-plants.

## What I took away

This project taught me how satellite imagery is stored, how to put different kinds of map data into the same coordinate system, how to stitch and clean up imagery, and how to turn numbers into something worth looking at. Most of all, it reminded me why I love maps, and how lucky I am to live somewhere this beautiful.

## Hi-Res Maps

Full-resolution (10 m) versions of the maps are available here (NOTE: Clicking on the links will download the files)
1. [True Color map](https://github.com/AhutGupta/earth-lens/releases/download/v1.0/true_color.png) 
2. [NDVI map](https://github.com/AhutGupta/earth-lens/releases/download/v1.0/ndvi.png)

## Credits

Contains modified Copernicus Sentinel data [2026]. County boundaries, roads and water features: US Census Bureau (cb_2023 and TIGER/Line 2023).