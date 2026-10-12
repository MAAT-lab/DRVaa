import os
import pandas as pd
import osmnx as ox
import geopandas as gpd
from dotenv import load_dotenv
from streetview import search_panoramas, get_panorama



# Switch to the alternative Overpass mirror and increase the timeout
# ox.settings.overpass_endpoint = "https://lz4.overpass-api.de/api/interpreter" # Optional server mirror for Overpass API
ox.settings.overpass_endpoint = "https://overpass.kumi.systems/api/interpreter" # Another optional server mirror for Overpass API
ox.settings.timeout = 300

# Load API key securely
load_dotenv()
api_key = os.getenv("GOOGLE_MAPS_API_KEY")

# Bounding box coordinates
max_lat = 20.71971   # North
min_lat = 20.69318   # South
max_lon = -103.44031 # East
min_lon = -103.46190 # West

# Fetch street network from bounding box
graph = ox.graph_from_bbox(bbox=(max_lat, min_lat, max_lon, min_lon), network_type="walk")
nodes, edges = ox.graph_to_gdfs(graph)

# Compute midpoints for every street edge
edges['midpoint'] = edges.geometry.interpolate(0.5, normalized=True)

output_dir = "./streetview_panoramas"
os.makedirs(output_dir, exist_ok=True)

records = []


for idx, row in edges.iloc[:10].iterrows(): # Access to first 10 edges  
# for idx, row in edges.iterrows(): #Full access to all edges
    # Format a unique segment ID from OSM edge indices (u, v, key)
    segment_id = f"{idx[0]}_{idx[1]}_{idx[2]}" if isinstance(idx, tuple) else str(idx)

    # Clean street name (OSM names can be lists, missing/NaN, or strings)
    street_name = row.get('name', 'Unnamed Street')
    if isinstance(street_name, list):
        street_name = " / ".join(street_name)
    elif pd.isna(street_name):
        street_name = "Unnamed Street"

    midpoint = row['midpoint']
    lat, lon = midpoint.y, midpoint.x

    # Query panorama at street midpoint
    panos = search_panoramas(lat=lat, lon=lon)
    if panos:
        closest_pano = panos[0]
        image_filename = f"{closest_pano.pano_id}.jpg"
        filepath = os.path.join(output_dir, image_filename)

        # Download panorama image
        image = get_panorama(pano_id=closest_pano.pano_id, api_key=api_key)
        image.save(filepath, "jpeg")
        print(f"Saved: {filepath}")

        # Record segment metadata
        records.append({
            "segment_id": segment_id,
            "latitude": lat,
            "longitude": lon,
            "street_name": street_name,
            "image_file": image_filename
        })

# Export test dataset to CSV
df = pd.DataFrame(records)
csv_filename = "street_segments_metadata.csv"
df.to_csv(csv_filename, index=False)

print(f"\nTest run complete! Processed {len(df)} segments. Metadata saved to {csv_filename}")