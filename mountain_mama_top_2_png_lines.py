import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import contextily as ctx
from matplotlib.lines import Line2D

# --- CONFIG ---
INPUT_JSON = "ib_to_santee_topo_slim.json"
OUTPUT_PNG = "topo_risk_map.png"

# Match the bounds we used to clip
BBOX = [-117.15, 32.53, -116.90, 32.88] 

# Match the column name from your example (it's case-sensitive)
ELEV_COL = 'elevation' 

# Define our 3 risk zones (in feet, matching the 40ft dataset)
ZONES = [50, 130] 

def define_color_map():
    # We will make a custom "segmented" colormap.
    # 0 -> ZONE[0] is Blue (Risk)
    # ZONE[0] -> ZONE[1] is Cyan (Caution)
    # ZONE[1] -> max is Gray (Safe)
    
    # Define colors for the 'Low', 'Medium', and 'High' ranges
    colors = ['#08306b', '#9ecae1', '#e0e0e0']  # Dark Blue, Light Blue, Light Gray
    
    # The 'boundaries' must be the values between the segments.
    # To use segment colors, we need a listed colormap and a norm.
    cmap = mcolors.ListedColormap(colors)
    norm = mcolors.BoundaryNorm([0, *ZONES, 1000], cmap.N) # Assuming 1000ft is a safe upper bound
    return cmap, norm

if __name__ == "__main__":
    print(f"📂 Loading {INPUT_JSON}...")
    try:
        df = gpd.read_file(INPUT_JSON)
        # Ensure the bounds match what we are plotting
        df = df.cx[BBOX[0]:BBOX[2], BBOX[1]:BBOX[3]]
    except Exception as e:
        print(f"❌ ERROR: Could not read file. {e}")
        exit()

    print(f"🌍 Setting up the map (Found {len(df)} lines)...")
    
    # We use a segmented custom colormap and norm
    custom_cmap, custom_norm = define_color_map()
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(14, 12))

    # Convert to Web Mercator (Required for the 'Live' contextily basemap)
    print("🌍 Reprojecting to Web Mercator for basemap...")
    df_web = df.to_crs(epsg=3857)

    print("🎨 Plotting styled lines...")
    # Plot the lines, coloring them by elevation. Use the custom colormap and norm.
    # Line thickness (lw) = 0.8 is good to keep it detailed.
    df_web.plot(ax=ax, 
                column=ELEV_COL, 
                cmap=custom_cmap, 
                norm=custom_norm, 
                lw=0.8,
                alpha=0.9, 
                legend=False)

    # Add the "Live" basemap (streams from the web, no disk space used)
    # OpenStreetMap.Mapnik gives good context with road names.
    print("🗺️ Adding basemap overlay...")
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

    print("🔧 Cleaning up the output...")
    # Add a custom legend
    custom_lines = [
        Line2D([0], [0], color='#08306b', lw=2, label='SEVERE RISK (<50ft)'),
        Line2D([0], [0], color='#9ecae1', lw=2, label='CAUTION (50-130ft)'),
        Line2D([0], [0], color='#e0e0e0', lw=2, label='SAFE GROUND (>130ft)')
    ]
    ax.legend(handles=custom_lines, loc='lower left', title="Elevation Risk", framealpha=1)

    ax.set_title("San Diego Topo Risk: IB to Santee/El Cajon", fontsize=16)
    ax.set_axis_off()  # Hide coordinates

    print(f"💾 Saving to {OUTPUT_PNG}...")
    plt.savefig(OUTPUT_PNG, dpi=200, bbox_inches='tight', facecolor='white')
    print("✅ Success! Check topo_risk_map.png")
    # plt.show() # Uncomment to see the window locally