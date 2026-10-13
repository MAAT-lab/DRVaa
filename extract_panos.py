import os
import warnings
import pandas as pd
import osmnx as ox
import requests
from dotenv import load_dotenv

# Suppress the harmless geographic CRS warning
warnings.filterwarnings("ignore", message="Geometry is in a geographic CRS")

# Load API key securely
load_dotenv()
api_key = os.getenv("GOOGLE_MAPS_API_KEY")

if not api_key:
    raise ValueError("Google Maps API key not found. Check your .env file.")

# Load the graph directly from your local file
graph = ox.graph_from_xml(r"Grasshopper\cityModels\SJO_match_small.osm")
nodes, edges = ox.graph_to_gdfs(graph)

# Compute midpoints for every street edge
edges['midpoint'] = edges.geometry.interpolate(0.5, normalized=True)

output_dir = "./streetview_panoramas"
os.makedirs(output_dir, exist_ok=True)

records = []

# Remove .iloc[:10] to run on all edges, or keep it for a small test
for idx, row in edges.iterrows():
    segment_id = f"{idx[0]}_{idx[1]}_{idx[2]}" if isinstance(idx, tuple) else str(idx)

    street_name = row.get('name', 'Unnamed Street')
    if isinstance(street_name, list):
        street_name = " / ".join(street_name)
    elif pd.isna(street_name):
        street_name = "Unnamed Street"

    lat, lon = row['midpoint'].y, row['midpoint'].x

    # 1. Check official Google API Metadata to see if a panorama exists here
    meta_url = f"https://maps.googleapis.com/maps/api/streetview/metadata?location={lat},{lon}&key={api_key}"
    
    try:
        meta_response = requests.get(meta_url).json()
        
        # If status is OK, Google has imagery for this location
        if meta_response.get("status") == "OK":
            pano_id = meta_response.get("pano_id")
            image_filename = f"{pano_id}.jpg"
            filepath = os.path.join(output_dir, image_filename)
            
            # 2. Download the actual image using the official endpoint
            img_url = f"https://maps.googleapis.com/maps/api/streetview?size=640x640&pano={pano_id}&key={api_key}"
            img_response = requests.get(img_url)
            
            if img_response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(img_response.content)
                print(f"Saved: {filepath} ({street_name})")
                
                records.append({
                    "segment_id": segment_id,
                    "latitude": lat,
                    "longitude": lon,
                    "street_name": street_name,
                    "pano_id": pano_id,
                    "image_file": image_filename
                })
            else:
                print(f"Failed to download image at {lat}, {lon} (HTTP {img_response.status_code})")
        
        else:
            print(f"No Street View coverage at {lat}, {lon}. Status: {meta_response.get('status')}")
            
    except Exception as e:
        print(f"Error processing {lat}, {lon}: {e}")

# Export dataset to CSV
if records:
    df = pd.DataFrame(records)
    csv_filename = "street_segments_metadata.csv"
    df.to_csv(csv_filename, index=False)
    print(f"\nRun complete! Processed {len(df)} segments with images. Metadata saved to {csv_filename}")
else:
    print("\nRun complete! No images were found or downloaded.")