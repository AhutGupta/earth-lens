"""Step 1: extract the Snohomish County boundary and make a locator map."""

import geopandas as gpd
import matplotlib.pyplot as plt

# 1. LOAD: geopandas reads a zipped shapefile directly
counties = gpd.read_file("data/cb_2023_us_county_500k.zip")

# 2. INSPECT: always look before you filter
print(counties.head())
print(counties.columns.tolist())
print("Original CRS:", counties.crs)

# 3. FILTER: STATEFP "53" = Washington
wa = counties[counties["STATEFP"] == "53"]
snohomish = wa[wa["NAME"] == "Snohomish"]
print(f"Washington counties: {len(wa)}, Snohomish rows: {len(snohomish)}")

# 4. MEASURE BEFORE reprojecting (to see why it matters)
print("Area in square DEGREES (meaningless):", snohomish.geometry.area.iloc[0])

# 5. REPROJECT to meters, then measure again
wa_utm = wa.to_crs("EPSG:32610")
snohomish_utm = snohomish.to_crs("EPSG:32610")
area_km2 = snohomish_utm.geometry.area.iloc[0] / 1e6
print(f"Computed area: {area_km2:.0f} km²")
print(f"Census ALAND column: {snohomish['ALAND'].iloc[0] / 1e6:.0f} km² (land only)")

# Sanity check: the real county is ~5,400 km². Wrong file = fail loudly.
assert area_km2 > 5000, f"Area {area_km2:.0f} km² is too small. Wrong file?"

# 6. SAVE the boundary for later steps (clipping imagery)
snohomish_utm.to_file("data/snohomish_utm.gpkg", driver="GPKG")

# 7. PLOT: the locator map
fig, ax = plt.subplots(figsize=(8, 6))
wa_utm.plot(ax=ax, facecolor="#e8e8e8", edgecolor="white", linewidth=0.5)
snohomish_utm.plot(ax=ax, facecolor="#2e7d32", edgecolor="black", linewidth=1)
ax.set_title("Study area: Snohomish County, Washington")
ax.set_axis_off()
plt.savefig("outputs/locator_map.png", dpi=200, bbox_inches="tight")
plt.show()
