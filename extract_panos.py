import os
import io
import warnings
import pandas as pd
import osmnx as ox
import requests
from PIL import Image
from dotenv import load_dotenv

# Ignorar la advertencia de CRS geográfico
warnings.filterwarnings("ignore", message="Geometry is in a geographic CRS")

# Cargar API key
load_dotenv()
api_key = os.getenv("GOOGLE_MAPS_API_KEY")

if not api_key:
    raise ValueError("Google Maps API key not found.")

# Cargar el grafo desde tu archivo local
graph = ox.graph_from_xml(r"Grasshopper\cityModels\SJO_match_large.osm")
nodes, edges = ox.graph_to_gdfs(graph)
edges['midpoint'] = edges.geometry.interpolate(0.5, normalized=True)

output_dir = "./streetview_panoramas_360"
os.makedirs(output_dir, exist_ok=True)

records = []

# Ángulos para cubrir los 360 grados (Norte, Este, Sur, Oeste)
headings = [0, 90, 180, 270]

for idx, row in edges.iterrows():
    segment_id = f"{idx[0]}_{idx[1]}_{idx[2]}" if isinstance(idx, tuple) else str(idx)
    street_name = row.get('name', 'Unnamed Street')
    if isinstance(street_name, list):
        street_name = " / ".join(street_name)
    elif pd.isna(street_name):
        street_name = "Unnamed Street"

    lat, lon = row['midpoint'].y, row['midpoint'].x

    # 1. Validar si existe imagen en las coordenadas
    meta_url = f"https://maps.googleapis.com/maps/api/streetview/metadata?location={lat},{lon}&key={api_key}"
    
    try:
        meta_response = requests.get(meta_url).json()
        
        if meta_response.get("status") == "OK":
            pano_id = meta_response.get("pano_id")
            image_filename = f"{pano_id}_360.jpg"
            filepath = os.path.join(output_dir, image_filename)
            
            # 2. Descargar las 4 caras de la panorámica
            images = []
            for h in headings:
                img_url = f"https://maps.googleapis.com/maps/api/streetview?size=640x640&pano={pano_id}&heading={h}&fov=90&key={api_key}"
                img_response = requests.get(img_url)
                
                if img_response.status_code == 200:
                    # Cargar la imagen en la memoria
                    img = Image.open(io.BytesIO(img_response.content))
                    images.append(img)
            
            # 3. Unir las 4 imágenes en una sola panorámica de 2560x640
            if len(images) == 4:
                total_width = sum(im.width for im in images)
                max_height = max(im.height for im in images)
                
                pano_image = Image.new('RGB', (total_width, max_height))
                
                x_offset = 0
                for im in images:
                    pano_image.paste(im, (x_offset, 0))
                    x_offset += im.width
                    
                # Guardar la panorámica final
                pano_image.save(filepath, "JPEG")
                print(f"Guardado 360°: {filepath} ({street_name})")
                
                records.append({
                    "segment_id": segment_id,
                    "latitude": lat,
                    "longitude": lon,
                    "street_name": street_name,
                    "pano_id": pano_id,
                    "image_file": image_filename
                })
            else:
                print(f"Error descargando los cuadrantes en {lat}, {lon}")
                
        else:
            print(f"Sin cobertura Street View en {lat}, {lon}. Status: {meta_response.get('status')}")
            
    except Exception as e:
        print(f"Error procesando {lat}, {lon}: {e}")

if records:
    df = pd.DataFrame(records)
    csv_filename = "street_segments_metadata_360.csv"
    df.to_csv(csv_filename, index=False)
    print(f"\n¡Proceso completo! {len(df)} panorámicas 360° ensambladas. Metadatos en {csv_filename}")