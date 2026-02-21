import folium
import geopandas as gpd
import leafmap.foliumap as leafmap
import osmnx as ox
import os

data_folder = '~/Downloads/socal-260220.osm.pbf'
output_folder = './'

if not os.path.exists(data_folder):
    os.mkdir(data_folder)
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

