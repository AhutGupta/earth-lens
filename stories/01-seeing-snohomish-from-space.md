# Seeing Snohomish County from Space

Every few days, a satellite passes over nearly every place on Earth and takes a picture. The images are free and open to the public.  
I was curious what they show about the place I live: Snohomish County, Washington.  

I love maps, and as a software engineer I wanted to learn how raw satellite pixels become one, and to make something beautiful along the way.   
This is the first step of **Earth-Lens**, a project to understand how this landscape has changed over time.

## Why Snohomish County

It is a place I know well enough to sanity-check what the data shows. And it holds an unusual range in one place: Puget Sound coastline, a river delta, farmland, suburbs, foothill forest and glaciated Cascade peaks.

### 📊 Project Snapshot
> - **Satellite Data:** Copernicus Sentinel-2 L2A (10 m spatial resolution), mid-July 2026
> - **Spectral Bands:** Band 2 (Blue), Band 3 (Green), Band 4 (Red), Band 8 (NIR)
> - **Vector Data:** US Census Bureau TIGER/Line (County boundary, roads, rivers, lakes)
> - **Target Region:** Snohomish County, WA (~2,100 sq. miles)
> - **Tech Stack:** Python (`rasterio`, `geopandas`, `matplotlib`, `shapely`)

## The maps

Two maps from the same satellite scenes: one shows the county as your eyes would see it, the other shows where plants are growing.

### True color

![True-color Snohomish County, July 2026](../outputs/true_color.png)

This is the county as your eyes would see it from orbit, built from the satellite's red, green and blue light measurements with the contrast boosted a little so details stand out. If you live here, you can probably find your own neighborhood.

- **West:** the deep water of **Puget Sound**, with **Mukilteo**, **Edmonds** and the **Port of Everett** along the shore, where the **Snohomish River** fans into its delta.
- **Northwest:** a checkerboard of farm fields near **Stanwood** and **Marysville**.
- **Center:** cities strung along **I-5**, with **Lake Stevens** dark against the streets.
- **Foothills:** dark green forest, with **Spada Lake** filling a long valley.
- **East:** the Cascades. **Three Fingers**, **Vesper**, **Sloan**, **Kyes** and **Columbia** peaks rise as pale ridges with snow still in the gullies, and **Glacier Peak**, a volcano ringed by glaciers, sits at the far edge.

[Full-resolution True Color map (~100 MB)](https://github.com/AhutGupta/earth-lens/releases/download/v1.0/true_color.png)

### Vegetation: NDVI

![NDVI Snohomish County, July 2026](../outputs/ndvi.png)

This map shows **NDVI**, the Normalized Difference Vegetation Index, a score for how green and healthy the plants in each pixel are. Same scenes, same pixels, a completely different picture. Green means lots of vegetation, red means little or none.

- **Glaciers and snowfields** around Glacier Peak glow red. Ice has no leaves.
- **Lakes**, including Spada and Lake Stevens, show as red shapes.
- The **Everett river delta** is a tangle of red and dark water.
- **Cities, roads and the Boeing factory and runway** near Mukilteo appear yellow and orange: pavement and rooftops.
- **Farm fields** form a patchwork of greens and yellows.
- **Foothill forest** fills the middle of the map with deep, solid green.

The city-to-forest boundary is much sharper here than in the photo. That is the payoff of looking beyond visible light.

[Full-resolution NDVI map (~100 MB)](https://github.com/AhutGupta/earth-lens/releases/download/v1.0/ndvi.png)

#### How NDVI works

Leaves absorb red light for photosynthesis and reflect near-infrared (NIR) light, which our eyes can't see but the satellite can. The more NIR a pixel reflects compared with red, the more vegetation it likely holds. The formula for each pixel:

**NDVI = (NIR − Red) / (NIR + Red)**

The result runs from −1 to +1:

| NDVI | Typically means |
|---|---|
| 0 or below | Water, snow, ice |
| ~0.1 to 0.2 | Bare ground, rock, pavement |
| ~0.2 to 0.5 | Grass, crops, sparse vegetation |
| 0.6 and above | Dense, healthy forest |

## How the maps were made

**The imagery** comes from **Sentinel-2**, European Space Agency satellites in the EU's Copernicus program. Each pixel, the smallest dot in the image, covers a 10 × 10 meter square, small enough that individual roads and lakes are visible. Each scene also comes as separate **bands**, measurements of different colors of light, including some our eyes can't see. I used four: blue, green, red and near-infrared. I downloaded the scenes from the Copernicus Browser, choosing ones with little cloud cover, and they arrive already corrected for the atmosphere's effects.

**The process** was four small Python scripts, run in order:

1. `01_boundary.py` extracts the county outline and makes a locator map.
2. `02_inspect_scenes.py` checks that the downloaded satellite tiles cover the whole county.
3. `03_mosaic_clip.py` stitches the tiles into one seamless image for each of the four bands (red, green, blue and NIR), evens out brightness between tiles, and trims each image to the county's shape.
4. `04_render.py` draws the two final maps from those four bands, then overlays the physical features and map layers: Puget Sound, rivers, lakes, glaciers, roads, and labeled cities and peaks.

Getting the details onto the map was half the fun, and each one was a small puzzle. The imagery stops at the county line, so I drew Puget Sound in myself as a shape. Peaks and cities were placed by their real latitude and longitude, and labels were nudged so the text doesn't cover what it names. Together, these turn a satellite photo into a map you can read.

It also took a few tries. My first scene was hazy, so I switched dates. The next was missing a tile, so I added a second scene, taken two days apart, to complete the map.

## What I learned

- **A satellite image is just numbers.** A few lines of code turn them into a picture or a map of where the plants are. I didn't expect one formula to pull glaciers, lakes and city grids out of the same four bands.
- **Maps are layers.** Imagery, boundaries, roads and rivers only line up once they share one coordinate system, the rule for flattening a round Earth onto a flat screen.
- **Small choices shape the picture.** Contrast, color and label placement decide whether a map is merely accurate or actually readable.
- **Check before you trust.** A coverage check and a close look at every render are what caught those problems before they reached the final maps.

## Next question

If one summer looks like this, **how different did earlier summers look?** In the next release, I'll line up July–August scenes from **2018, 2020, 2023 and the latest year** and compare them using the same method.

---

Contains modified Copernicus Sentinel data 2026. County boundaries, roads and water features: US Census Bureau (cb_2023 and TIGER/Line 2023).