# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "geopandas",
#     "matplotlib",
#     "shapely",
#     "pyogrio",
#     "contextily",
# ]
# ///

"""
mountain_mama_1.py
------------------
Shows areas clear of freeways in San Diego, over a real street basemap.
Green = safe from freeways.  Red = too close to a freeway.
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import contextily as ctx
from shapely.geometry import box
from shapely.ops import unary_union

# ── settings ────────────────────────────────────────────────────────────────

PBF   = "V:/MSI_GL63_8SE_25H2_20251221/socal_latest_20260221.osm.pbf"
BBOX  = (-117.20, 32.70, -117.10, 32.80)   # west, south, east, north
BUF_M = 610                                 # 2,000 ft in metres

# ── 1. load roads ────────────────────────────────────────────────────────────

print("Loading roads...")
roads    = gpd.read_file(PBF, layer="lines", bbox=BBOX, engine="pyogrio")
freeways = roads[roads["highway"].isin(["motorway", "motorway_link", "trunk", "trunk_link"])]
print(f"  Freeways found: {len(freeways)}")

# ── 2. buffer freeways ───────────────────────────────────────────────────────

print("Buffering freeways...")
fwy_proj  = freeways.to_crs("EPSG:32611")
buf_union = unary_union(fwy_proj.buffer(BUF_M))
danger    = gpd.GeoDataFrame(geometry=[buf_union], crs="EPSG:32611").to_crs("EPSG:3857")

# ── 3. subtract from study area ──────────────────────────────────────────────

# contextily needs Web Mercator (EPSG:3857) for the basemap to align
study    = gpd.GeoDataFrame(geometry=[box(*BBOX)], crs="EPSG:4326").to_crs("EPSG:3857")
safe     = gpd.GeoDataFrame(geometry=[study.geometry.iloc[0].difference(danger.geometry.iloc[0])], crs="EPSG:3857")
freeways = freeways.to_crs("EPSG:3857")

# ── 4. plot ──────────────────────────────────────────────────────────────────

print("Drawing map...")
fig, ax = plt.subplots(figsize=(12, 12))

safe.plot(    ax=ax, color="green",   alpha=0.35, zorder=2)
danger.plot(  ax=ax, color="red",     alpha=0.35, zorder=2)
freeways.plot(ax=ax, color="darkred", linewidth=1.2, zorder=3)

# basemap tiles — needs internet, downloads once then caches
print("Fetching basemap tiles (needs internet, cached after first run)...")
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, zoom=13)

ax.set_axis_off()
ax.set_title("Mountain Mama - Freeway Clearance Map\n(green = safe, red = avoid)",
             fontsize=14, pad=12)
ax.legend(handles=[
    mpatches.Patch(color="green",   alpha=0.6, label="Clear of freeways"),
    mpatches.Patch(color="red",     alpha=0.6, label="Too close (2,000 ft)"),
    mpatches.Patch(color="darkred", alpha=0.9, label="Freeways"),
], fontsize=11, loc="lower right")

plt.tight_layout()
plt.savefig("mountain_mama_1.png", dpi=150)
print("Saved -> mountain_mama_1.png")
plt.show()
