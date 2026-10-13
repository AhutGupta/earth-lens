# Seeing My Home from Space

## The question
What does Snohomish County look like through Earth-observation data?

## Why I care
I live here. I moved to the Seattle area in 2018 and have spent years looking at this landscape from the ground: the Sound, the river valleys, the farmland, the foothills, the Cascades. I wanted to see it from the other direction, from about 800 km up, and eventually find out whether the changes I think I've noticed show up in the data.

This first step is simpler: just look.

## The data
- **Sentinel-2 Level-2A**: a European Space Agency satellite that images the whole planet every few days. I used scenes from **20 August 2023** with under 10% cloud cover. The county spans three tiles, which I stitched together.
- **US Census county boundaries (2023)**: used to cut the imagery to the county outline.

Level-2A means the images are already corrected for the atmosphere, so values are comparable between dates. That matters later when I compare years.

## What I did
1. Pulled out Snohomish County's outline and converted it to the same coordinate system as the imagery (UTM zone 10N), so the two lined up.
2. Merged three satellite tiles into one image covering the whole county.
3. Cut the merged image to the county outline.
4. Made two pictures from four of the satellite's bands: a true-color image and a vegetation map.

## Result

### True color
![True-color Snohomish County](../outputs/true_color.png)

This is roughly what your eyes would see from orbit. It's built from three bands (red, green, and blue), one for each color channel of the image. I stretched the contrast a little because raw satellite data looks flat and dark.

_TODO: what stands out to you? The Sound, the Cascades, Everett, the Snohomish River valley, snow, haze?_

### NDVI
![NDVI Snohomish County](../outputs/ndvi.png)

NDVI stands for Normalized Difference Vegetation Index. Plants absorb red light for photosynthesis and strongly reflect near-infrared light, which our eyes can't see. NDVI compares the two:

$$\text{NDVI} = \frac{\text{NIR} - \text{Red}}{\text{NIR} + \text{Red}}$$

The result runs from -1 to 1. Roughly:

| NDVI | What it usually means |
| --- | --- |
| Below 0 | Water. It absorbs near-infrared, so the value goes negative. |
| 0 to 0.2 | Bare rock, snow, pavement, buildings, or bare soil |
| 0.2 to 0.5 | Sparse or stressed vegetation: grass, pasture, cropland, lawns |
| 0.5 to 0.7 | Healthy, dense vegetation |
| Above 0.7 | Very dense, healthy canopy, like conifer forest |

These cutoffs are rules of thumb, not hard lines. The same number can mean different things in different places.

_TODO: where is it greenest? Lowest? Does the pattern match what you know?_

## What I learned
- A satellite image is a stack of numbers, one per band per pixel. A photo is three of those bands. NDVI is a different combination.
- Each Sentinel-2 pixel covers 10 m × 10 m. The county is about 5,460 km², so that's roughly 54 million pixels per band.
- Tiles don't follow political boundaries. Snohomish County needed three.
- Coordinate systems matter. Area in degrees is meaningless, while area in meters gave 5,463 km², close to the Census's 5,404 km² of land.
- Newer Sentinel-2 data has a +1000 offset, so reflectance is `(value − 1000) / 10000`. Skipping it quietly skews NDVI.
- **Mosaics have seams.** My first merge showed a rectangular "shadow" where two tiles met, in both true color and NDVI. Over the same ground, one tile read about 30% darker in the visible bands than its neighbor (haze and atmospheric correction differ per tile). Near-infrared agreed within 3%, so the seam was mostly in the visible bands. NDVI is a ratio, but haze adds light rather than scaling it, so the ratio doesn't cancel it. I fixed it by matching each tile's brightness to its neighbor over the overlap and blending across 5 km, which brought the visible-band ratio from 0.64–0.71 to 0.95–0.97.
- **Resolution is a choice.** Native pixels are 10 m. The web images in this repo use 40 m pixels; a full 10 m render is about 12,000 px wide.

_TODO: add what surprised you._

## What I cannot conclude
- This is a single day in August 2023. It says nothing about change, trends, or what's "normal".
- NDVI measures how much green plant material there is, not why. A low value could be rock, snow, pavement, a mown field, or stressed plants.
- Thin haze, cloud shadows, and smoke can shift values even in a "clear" scene.
- Each pixel mixes whatever is in a 10 m square, so one value can blend trees, a road, and a roof.
- Brightness matching changes pixel values. That's fine for a picture, but for comparing years in Release 2 I should use original values, or compare only inside a single tile, so the correction doesn't add its own bias.
- Landmark positions on the true-color map were placed by hand from approximate coordinates, not read from a dataset.

## Next question
How does this same view look in other summers? I want to compare August 2018, the year I moved here, with 2020, 2023, and the latest year, and see whether anything has really changed.
