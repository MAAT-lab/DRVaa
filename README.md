# DRVA/A

## Affective-Atmospheric Vectorial Drift and Resonance (DRVA/A)
### Intelligent Computational System for Atmospheric Perception and Multi-Sensory Navigation

Traditional cartography operates under a paradigm of spatial positivism that optimizes routes for functional efficiency, ignoring the city's affective reality: the precognitive emotional resonances, sensory atmospheres, and somatic micro-experiences that define human territoriality. DRVA recovers the Situationist gesture of the dérive—displacement guided by the psychic attraction of the territory, rather than the destination—and formalizes it as a computational device capable of translating qualitative urban atmospheres into navigable graph structures using Multimodal Large Language Models (MLLMs) as proxy sensors.

Methodologically, DRVA establishes a decoupled spatial-semantic architecture that extracts non-visual affective fields from immersive 360° street-level imagery. Asynchronously, the system synthesizes latent affective tensors that capture ephemeral dimensions such as acoustic isolation, somatic stress, visual harmony, and olfactory nostalgia—Debord's unities of ambiance—indexed onto OpenStreetMap edges. In real time, a natural language compiler translates subjective user instructions ("a path that feels calm and protective") into deterministic graph weights, calculating routes via affective alignment in less than 100ms.

The core contribution of DRVA is its critical challenge to purely geometric navigation. Where GPS optimizes distance, DRVA optimizes experience, allowing itself to be drawn by the territory's affective gradients instead of resisting them. By shifting the routing objective function from spatial efficiency to emotional resonance, the project demonstrates that methodologies involving AI can formalize qualitative urban design theories that until now resisted operationalization. More than a navigation system, DRVA introduces an epistemic instrument for architecture and urbanism: one that does not measure space but rather its effect on the body, turning the subjective experience of the territory into projectable material. In this shift—from geometry to affect, from trajectory to resonance—a new disciplinary capacity opens up to design cities based on what is felt, not just what is measured.


## Setting up Python
Within a terminal, do the following
1. Create the environment: ```python -m venv venv```
2. Activate the project: ```.\venv\Scripts\activate```
3. Install dependencies: ```pip install osmnx geopandas shapely streetview python-dotenv```


## Setting up the Vision LLM Model
Within a terminal, download and install Ollama (ollama.com).
1. Install the Python bindings for Ollama:
   `pip install ollama`
2. Download the model:
   `ollama pull qwen2.5vl`
   *(Optional alternatives: `ollama pull llava` or `ollama pull llama3.2-vision`)*
3. Run the analysis script:
   `python score_panoramas.py`



