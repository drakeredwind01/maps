# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "geopandas",
#     "matplotlib",
#     "shapely",
#     "pyogrio",
#     "contextily",
#     "rasterio",
#     "numpy",
#     "elevation",
# ]
# ///
"""
mountain_mama_flood.py
----------------------
Flood risk map for San Diego.

Layers (darkest = most dangerous):
  Dark blue  = below 10m elevation  (severe flood pool, sewage risk)
  Medium blue = below 30m elevation  (moderate low-lying risk)
  Light blue  = within 300m of a river corridor (flood inundation zone)
  Green       = everything else (relatively safe)
"""
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import contextily as ctx
import rasterio
from rasterio.mask import mask as rio_mask
from shapely.geometry import box
from shapely.ops import unary_union
import subprocess, sys, os

# ── settings ────────────────────────────────────────────────────────────────
# PBF    = "V:/MSI_GL63_8SE_25H2_20251221/socal_latest_20260221.osm.pbf"
PBF    = "/media/no1/A662-9307/MSI_GL63_8SE_25H2_20251221"

BBOX   = (-117.20, 32.70, -117.10, 32.80)   # west, south, east, north
BUF_M  = 300                                 # 300 m river corridor buffer
DEM_TIF = "san_diego_dem.tif"               # downloaded once, reused

# ── 1. download DEM (SRTM 30m) if needed ─────────────────────────────────────
if not os.path.exists(DEM_TIF):
    print("Downloading DEM tiles (one-time, ~10 MB)...")
    subprocess.run([
        sys.executable, "-m", "elevation.cli", "clip",
        "--bounds", str(BBOX[0]), str(BBOX[1]), str(BBOX[2]), str(BBOX[3]),
        "--output", DEM_TIF,
        "--product", "SRTM3",
    ], check=True)
else:
    print(f"Using cached DEM: {DEM_TIF}")

# ── 2. load waterways ─────────────────────────────────────────────────────────
print("Loading waterways...")
rivers = gpd.read_file(PBF, layer="lines", bbox=BBOX, engine="pyogrio")
rivers = rivers[rivers["waterway"].isin(["river", "stream", "canal", "drain"])]
print(f"  Waterways found: {len(rivers)}")

# ── 3. buffer rivers ──────────────────────────────────────────────────────────
print("Buffering river corridors (300 m)...")
riv_proj  = rivers.to_crs("EPSG:32611")
buf_union = unary_union(riv_proj.buffer(BUF_M))
river_buf = gpd.GeoDataFrame(geometry=[buf_union], crs="EPSG:32611").to_crs("EPSG:3857")

# ── 4. extract low-elevation zones from DEM ───────────────────────────────────
print("Reading elevation data...")
study_4326 = gpd.GeoDataFrame(geometry=[box(*BBOX)], crs="EPSG:4326")

with rasterio.open(DEM_TIF) as src:
    # Clip DEM to study area
    shapes = [geom.__geo_interface__ for geom in study_4326.geometry]
    dem_data, dem_transform = rio_mask(src, shapes, crop=True)
    dem_crs = src.crs
    dem_data = dem_data[0].astype(float)
    dem_data[dem_data == src.nodata] = np.nan

# Build polygons for each elevation band using rasterio features
from rasterio.features import shapes as rio_shapes
from shapely.geometry import shape

def elev_band_to_gdf(dem_arr, transform, crs, max_elev):
    """Return GeoDataFrame of pixels at or below max_elev."""
    mask_arr = (dem_arr <= max_elev) & (~np.isnan(dem_arr))
    mask_uint = mask_arr.astype(np.uint8)
    polys = [
        shape(geom)
        for geom, val in rio_shapes(mask_uint, mask=mask_uint, transform=transform)
        if val == 1
    ]
    if not polys:
        return gpd.GeoDataFrame(geometry=[], crs=crs)
    return gpd.GeoDataFrame(
        geometry=[unary_union(polys)], crs=crs
    ).to_crs("EPSG:3857")

print("Building elevation zones (10m and 30m)...")
zone_30m = elev_band_to_gdf(dem_data, dem_transform, dem_crs, 30)
zone_10m = elev_band_to_gdf(dem_data, dem_transform, dem_crs, 10)

# ── 5. build study area & safe zone ──────────────────────────────────────────
study = gpd.GeoDataFrame(geometry=[box(*BBOX)], crs="EPSG:4326").to_crs("EPSG:3857")
study_geom = study.geometry.iloc[0]

# Combine all risk polygons so safe = everything else
all_risk = unary_union(
    [g for gdf in [river_buf, zone_30m, zone_10m] for g in gdf.geometry if not g.is_empty]
)
safe = gpd.GeoDataFrame(geometry=[study_geom.difference(all_risk)], crs="EPSG:3857")

# Clip each layer to study area for clean edges
def clip_to_study(gdf):
    if gdf.empty:
        return gdf
    return gpd.GeoDataFrame(
        geometry=[study_geom.intersection(gdf.geometry.iloc[0])], crs="EPSG:3857"
    )

river_buf = clip_to_study(river_buf)
zone_30m  = clip_to_study(zone_30m)
zone_10m  = clip_to_study(zone_10m)

# ── 6. plot ───────────────────────────────────────────────────────────────────
print("Drawing map...")
fig, ax = plt.subplots(figsize=(12, 12))

# Draw layers bottom-to-top; darker = higher risk on top
safe.plot(     ax=ax, color="#4CAF50", alpha=0.40, zorder=2)   # green
river_buf.plot(ax=ax, color="#90CAF9", alpha=0.50, zorder=3)   # light blue
zone_30m.plot( ax=ax, color="#1976D2", alpha=0.45, zorder=4)   # medium blue
zone_10m.plot( ax=ax, color="#0D47A1", alpha=0.55, zorder=5)   # dark blue

print("Fetching basemap tiles...")
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, zoom=13)

ax.set_axis_off()
ax.set_title(
    "Mountain Mama — Flood Risk Map\n(darker blue = greater flood/sewage danger)",
    fontsize=14, pad=12
)
ax.legend(handles=[
    mpatches.Patch(color="#4CAF50", alpha=0.7, label="Relatively safe"),
    mpatches.Patch(color="#90CAF9", alpha=0.8, label="River corridor (300 m)"),
    mpatches.Patch(color="#1976D2", alpha=0.8, label="Low elevation < 30 m"),
    mpatches.Patch(color="#0D47A1", alpha=0.9, label="Very low elevation < 10 m (sewage risk)"),
], fontsize=11, loc="lower right")

plt.tight_layout()
plt.savefig("mountain_mama_flood.png", dpi=150)
print("Saved → mountain_mama_flood.png")
plt.show()