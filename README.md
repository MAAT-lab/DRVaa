# DRVA/A

## Drift and Resonance through Vectorial Affects and Atmospheres (DRVA/A)
### Intelligent Computational System for Atmospheric Perception and Multi-Sensory Navigation

Traditional cartography operates under a paradigm of spatial positivism that optimizes routes for functional efficiency, making use of the typical Dijkstra algorithm or its derivatives, ignoring the city's affective reality: the precognitive emotional resonances, sensory atmospheres, and somatic micro-experiences that define human territoriality. DRVA/A recovers the Situationist gesture of the dérive—displacement guided by the psychic attraction of the territory, rather than the destination—and formalizes it as a computational device capable of translating qualitative urban atmospheres into navigable graph structures using Multimodal Large Language Models (MLLMs) as proxy sensors.

Methodologically, DRVA/A establishes a decoupled spatial-semantic architecture that extracts non-visual affective fields from immersive 360° street-level imagery. Asynchronously, the system synthesizes latent affective tensors that capture ephemeral dimensions such as acoustic isolation, somatic stress, visual harmony, and olfactory nostalgia—Debord's unities of ambiance—indexed onto OpenStreetMap edges. In real time, the system calculates routes according to the selected affective dimension, and the MLLM synthesizes the trajectory through an atmospheric summary of the route.

The core contribution of DRVA/A is its critical challenge to purely geometric navigation. Where GPS optimizes distance, DRVA/A optimizes experience, allowing itself to be drawn by the territory's affective gradients instead of resisting them. By shifting the routing objective function from spatial efficiency to emotional resonance, the project demonstrates that methodologies involving AI can formalize qualitative urban design theories that until now resisted operationalization. More than a navigation system, DRVA/A introduces an epistemic instrument for architecture and urbanism: one that does not measure space but rather its effect on the body, turning the subjective experience of the territory into projectable material. In this shift—from geometry to affect, from trajectory to resonance—a new disciplinary capacity opens up to design cities based on what is felt, not just what is measured.

## Setup
### Setting up Python
Within a terminal, do the following
1. Create the environment: ```python -m venv venv```
2. Activate the project: ```.\venv\Scripts\activate```
3. Install dependencies: ```pip install osmnx geopandas shapely streetview python-dotenv```


### Setting up the Vision LLM Model
Within a terminal, download and install Ollama (ollama.com).
1. Install the Python bindings for Ollama:
   `pip install ollama`
2. Download the model:
   `ollama pull qwen2.5vl`
   *(Optional alternatives: `ollama pull llava` or `ollama pull llama3.2-vision`)*
3. Run the analysis script:
   `python score_panoramas.py`

## Simulation
### Panorama (or image) extraction from Google Street View
1. Get key from Google Street View Static API within Google Cloud
2. Insert key inside ```extract_panos.py```
3. Select an area to analyze from OpenStreetMap and download as OSM file
4. Reference the downloaded OSM within ```extract_panos.py```
5. Run the PY file.
   - A folder will be created where all panoramic images will be saved: `./streetview_panoramas_360`.
   - A CSV file will also be created where all data, like street segment ID, latitude, longitude, street name, and image file will be recorded: `street_segments_metadata_360.csv`.

### Panorama scoring through LLM vision model
1. Open the ```score_panoramas.py``` file.
2. Make sure you point to CSV file (`street_segments_metadata_360.csv`) and panorama folder (`./streetview_panoramas_360`).
3. Select vision model (in this case, `qwen2.5vl` was used through Ollama as indicated before.
4. Run PY file.
   - A CSV file will be created adding LLM scores and rationale for each panoramic image: `street_segments_scored_360_rationale2.csv`

### Simulation run
1. Open the Grasshopper simulation `DRVaa.gh` file
2. Point to OSM file and latest CSV file (`street_segments_scored_360_rationale2.csv`).
3. Explore and analyze scores and routes.

## Other references
For panorama images used in this project look at the following Google Drive folder: 

