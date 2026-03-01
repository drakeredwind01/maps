import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import numpy as np

# --- CONFIG ---
INPUT_JSON = "ib_to_santee_topo_slim.json"
OUTPUT_PNG = "solid_safety_map.png"

print(f"📂 Loading data...")
df = gpd.read_file(INPUT_JSON)

# 1. Extract the raw coordinates and elevation values
# We need these to 'paint' the solid areas
x = df.geometry.centroid.x
y = df.geometry.centroid.y
z = df['elevation']

# 2. Setup the Plot
fig, ax = plt.subplots(figsize=(12, 10))

# 3. Create 'Filled' Contours (This makes the solid colors)
# Levels: 0-50 (Red), 50-130 (Yellow), 130-2000 (Green)
print("🎨 Painting safety zones...")
cntr = ax.tricontourf(x, y, z, levels=[0, 50, 130, 2000], 
                     colors=['#d73027', '#fee08b', '#1a9850'], 
                     alpha=0.6)

# 4. Add the Basemap so you can see the streets
# We use Web Mercator (EPSG:3857) to make the basemap align
ax.set_aspect('equal')
ctx.add_basemap(ax, crs=df.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# 5. Clean up and Legend
ax.set_title("San Diego Elevation Safety Zones (Solid View)", fontsize=15)
ax.set_axis_off()

# Manually add a legend since tricontourf legend is tricky
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], color='#d73027', lw=8, label='SEVERE RISK (<50ft)'),
    Line2D([0], [0], color='#fee08b', lw=8, label='CAUTION (50-130ft)'),
    Line2D([0], [0], color='#1a9850', lw=8, label='SAFE GROUND (>130ft)')
]
ax.legend(handles=legend_elements, loc='lower left', frameon=True)

print(f"💾 Saving to {OUTPUT_PNG}...")
plt.savefig(OUTPUT_PNG, dpi=200, bbox_inches='tight')
print("✅ Done! Open solid_safety_map.png")