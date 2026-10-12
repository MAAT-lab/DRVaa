import os
import osmnx as ox
import geopandas as gpd
from dotenv import load_dotenv
from streetview import search_panoramas, get_panorama

# Load API key securely
load_dotenv()
api_key = os.getenv("GOOGLE_MAPS_API_KEY")


#Select a place to extract the street network
# place_name = "Zapopan, Jalisco, Mexico"
# graph = ox.graph_from_place(place_name, network_type="walk")

# Define your bounding box coordinates (matching Urbano's Max/Min Lat and Lon)
max_lat = 20.71971  # North
min_lat = 20.69318  # South
max_lon = -103.44031 # East
min_lon = -103.46190 # West
# Create the graph from the bounding box
# Note: If using OSMnx v2.0+, use the bbox=(...) tuple argument format
graph = ox.graph_from_bbox(bbox=(max_lat, min_lat, max_lon, min_lon), network_type="walk")

nodes, edges = ox.graph_to_gdfs(graph)

edges['midpoint'] = edges.geometry.interpolate(0.5, normalized=True)
midpoints = [(point.y, point.x) for point in edges['midpoint']]

output_dir = "./streetview_panoramas"
os.makedirs(output_dir, exist_ok=True)

panorama_ids = []

# CRITICAL: Keep the [:10] slice for your first test run to avoid API costs
for lat, lon in midpoints[:10]: 
    panos = search_panoramas(lat=lat, lon=lon)
    if panos:
        closest_pano = panos[0]
        panorama_ids.append(closest_pano.pano_id)
        
        # Pass your API key to download the actual image
        image = get_panorama(pano_id=closest_pano.pano_id, api_key=api_key)
        filename = os.path.join(output_dir, f"{closest_pano.pano_id}.jpg")
        image.save(filename, "jpeg")
        print(f"Saved: {filename}")