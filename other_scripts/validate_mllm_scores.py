import os
import geopandas as gpd
import numpy as np
import osmnx as ox
import pandas as pd
from scipy.stats import pearsonr, spearmanr

# ---------------------------------------------------------
# 1. Configuration & Bounding Box (San Juan de Ocotán)
# ---------------------------------------------------------
# Overpass API settings
ox.settings.overpass_endpoint = "https://overpass.kumi.systems/api/interpreter"
ox.settings.timeout = 300

# Bounding Box coordinates matching your previous setup
max_lat, min_lat = 20.71971, 20.69318
max_lon, min_lon = -103.44031, -103.46190

# Target UTM projection for Zapopan / Guadalajara region (in meters)
UTM_CRS = "EPSG:32613"  # WGS 84 / UTM Zone 13N

# Buffer distance around street segment midpoints (in meters)
BUFFER_METERS = 50.0

# ---------------------------------------------------------
# 2. Load Scored Segments Data
# ---------------------------------------------------------
input_csv = "street_segments_scored_360_rationale.csv"

if not os.path.exists(input_csv):
    raise FileNotFoundError(
        f"Could not find '{input_csv}'. Ensure your MLLM scoring script has completed."
    )

df = pd.read_csv(input_csv)

# Convert to GeoDataFrame
gdf_segments = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
    crs="EPSG:4326",
)

# Reproject to meters for spatial buffer analysis
gdf_segments = gdf_segments.to_crs(UTM_CRS)

# Create 50-meter spatial buffers around midpoints
gdf_segments["buffer_geometry"] = gdf_segments.geometry.buffer(BUFFER_METERS)

print(f"Loaded {len(gdf_segments)} scored segments from San Juan de Ocotán.")

# ---------------------------------------------------------
# 3. Fetch Targeted POIs / Urban Features from OpenStreetMap
# ---------------------------------------------------------
print("Fetching target POI categories from OpenStreetMap...")


# Function to query OSM features across different OSMnx API versions
def fetch_osm_features(bbox_coords, tags):
    try:
        # OSMnx 2.0+ standard format (min_lon, min_lat, max_lon, max_lat)
        return ox.features_from_bbox(
            bbox=(
                bbox_coords[3],
                bbox_coords[1],
                bbox_coords[2],
                bbox_coords[0],
            ),
            tags=tags,
        )
    except Exception:
        # Fallback for older OSMnx versions
        return ox.geometries_from_bbox(
            north=bbox_coords[0],
            south=bbox_coords[1],
            east=bbox_coords[2],
            west=bbox_coords[3],
            tags=tags,
        )


bbox = (max_lat, min_lat, max_lon, min_lon)

# Category A: Culinary / Food POIs (Ground truth for Olfactory)
food_tags = {
    "amenity": ["restaurant", "cafe", "fast_food", "food_court", "ice_cream"],
    "shop": ["bakery", "supermarket", "convenience", "butcher", "greengrocer"],
}

# Category B: Commercial & Active Frontages (Ground truth for Social Vitality)
social_tags = {
    "amenity": ["cafe", "restaurant", "bar", "pub", "place_of_worship", "bank"],
    "shop": True,
}

# Category C: Heavy Infrastructure / Freight (Ground truth for Somatic Stress)
stress_tags = {
    "landuse": ["industrial"],
    "railway": ["rail"],
    "highway": ["primary", "trunk"],
    "amenity": ["fuel"],
}

# Category D: Green Spaces & Tree Canopy (Ground truth for Thermal & Acoustic)
green_tags = {
    "leisure": ["park", "garden", "playground"],
    "landuse": ["grass", "forest", "recreation_ground"],
    "natural": ["tree", "tree_row", "wood"],
}

# Fetch POI GeoDataFrames
gdf_food = fetch_osm_features(bbox, food_tags)
gdf_social = fetch_osm_features(bbox, social_tags)
gdf_stress = fetch_osm_features(bbox, stress_tags)
gdf_green = fetch_osm_features(bbox, green_tags)


# Helper function to clean and project POIs
def prepare_poi_gdf(gdf_poi):
    if gdf_poi.empty:
        return gpd.GeoDataFrame(geometry=[], crs=UTM_CRS)
    # Convert polygons/multipolygons to centroids if necessary
    gdf_poi = gdf_poi.copy()
    gdf_poi["geometry"] = gdf_poi.geometry.centroid
    return gdf_poi.to_crs(UTM_CRS)


gdf_food = prepare_poi_gdf(gdf_food)
gdf_social = prepare_poi_gdf(gdf_social)
gdf_stress = prepare_poi_gdf(gdf_stress)
gdf_green = prepare_poi_gdf(gdf_green)

# ---------------------------------------------------------
# Conteo e impresión de POIs por categoría y Total
# ---------------------------------------------------------
count_food = len(gdf_food)
count_social = len(gdf_social)
count_stress = len(gdf_stress)
count_green = len(gdf_green)
total_pois = count_food + count_social + count_stress + count_green

print("\n" + "=" * 65)
print(" RESUMEN DE ELEMENTOS Y POIs OBTENIDOS DE OPENSTREETMAP")
print("=" * 65)
print(f"  • Gastronómicos / Alimentos (Food):      {count_food}")
print(f"  • Comerciales y Activos (Social):       {count_social}")
print(f"  • Infraestructura / Estrés (Stress):    {count_stress}")
print(f"  • Áreas Verdes / Vegetación (Green):    {count_green}")
print("-" * 65)
print(f"  TOTAL DE ATRIBUTOS/POIs EXTRAÍDOS:      {total_pois}")
print("=" * 65 + "\n")

# ---------------------------------------------------------
# 4. Spatial Overlay: Count POIs within 50m Buffer
# ---------------------------------------------------------
print("Calculating spatial buffer densities (50m radius)...")


def count_pois_in_buffer(segments_gdf, poi_gdf, column_name):
    counts = []
    for buffer_geom in segments_gdf["buffer_geometry"]:
        if poi_gdf.empty:
            counts.append(0)
        else:
            # Count POIs intersecting the 50m buffer polygon
            contained = poi_gdf[poi_gdf.geometry.intersects(buffer_geom)]
            counts.append(len(contained))
    segments_gdf[column_name] = counts
    return segments_gdf


gdf_segments = count_pois_in_buffer(
    gdf_segments, gdf_food, "density_food_pois"
)
gdf_segments = count_pois_in_buffer(
    gdf_segments, gdf_social, "density_social_pois"
)
gdf_segments = count_pois_in_buffer(
    gdf_segments, gdf_stress, "density_stress_features"
)
gdf_segments = count_pois_in_buffer(
    gdf_segments, gdf_green, "density_green_features"
)

# ---------------------------------------------------------
# 5. Targeted Correlation Analysis
# ---------------------------------------------------------
print("\n" + "=" * 65)
print(" TARGETED STATISTICAL VALIDATION (OSM POIs vs. MLLM SCORES)")
print("=" * 65)

# Mapping hypotheses: (Dimension, POI Density Column, Expected Correlation)
hypotheses = [
    (
        "olfactory",
        "density_food_pois",
        "Positive (+)",
        "Food/Culinary POIs",
    ),
    (
        "social",
        "density_social_pois",
        "Positive (+)",
        "Commercial & Active POIs",
    ),
    (
        "stress",
        "density_stress_features",
        "Positive (+)",
        "Industrial/Train/Highway Features",
    ),
    (
        "acoustic",
        "density_green_features",
        "Positive (+)",
        "Parks & Green Features",
    ),
    (
        "thermal",
        "density_green_features",
        "Positive (+)",
        "Parks & Green Features",
    ),
]

results = []

for score_dim, poi_col, expected_dir, description in hypotheses:
    # Filter out missing/NaN scores
    valid_data = gdf_segments[[score_dim, poi_col]].dropna()

    # Convert columns to numeric floats
    x = valid_data[poi_col].astype(float).values
    y = valid_data[score_dim].astype(float).values

    if len(x) > 2 and np.std(x) > 0 and np.std(y) > 0:
        pearson_r, p_p = pearsonr(x, y)
        spearman_r, p_s = spearmanr(x, y)
    else:
        pearson_r, p_p, spearman_r, p_s = 0.0, 1.0, 0.0, 1.0

    results.append({
        "Affective Dimension": score_dim.upper(),
        "OSM Ground Truth Metric": description,
        "Expected": expected_dir,
        "Pearson r": round(pearson_r, 3),
        "Spearman ρ": round(spearman_r, 3),
        "p-value (Spearman)": f"{p_s:.4f}"
        if p_s >= 0.0001
        else "< 0.0001",
        "Significant (p < 0.05)": "YES" if p_s < 0.05 else "NO",
    })

df_results = pd.DataFrame(results)
print(df_results.to_string(index=False))
print("=" * 65)

# ---------------------------------------------------------
# 6. Export Enriched Dataset
# ---------------------------------------------------------
output_file = "street_segments_validated_spatial.csv"
# Drop non-serializable geometries before exporting to CSV
df_export = pd.DataFrame(gdf_segments.drop(columns=["buffer_geometry"]))
df_export.to_csv(output_file, index=False)

print(
    f"\nValidation complete! Enriched dataset saved to '{output_file}' with spatial density columns."
)