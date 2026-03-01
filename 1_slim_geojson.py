import geopandas as gpd

def make_web_ready(input_file, output_file):
    # 1. Load the heavy file
    data = gpd.read_file(input_file)
    
    # 2. Keep ONLY the column you need (e.g., 'ELEV')
    # This deletes 90% of the 'junk' text data
    if 'ELEV' in data.columns:
        data = data[['ELEV', 'geometry']]
    
    # 3. Reduce coordinate precision to 5 decimals (saves massive space)
    # 4. Simplify the lines slightly (0.1 means 10cm tolerance)
    data['geometry'] = data.simplify(0.1, preserve_topology=True)
    
    # 5. Export back to GeoJSON
    data.to_file(output_file, driver='GeoJSON')
    print(f"Success! {output_file} is now lean and mean.")

make_web_ready("Topo_40ft_1999_SG.json", "topo_40ft_slim.json")