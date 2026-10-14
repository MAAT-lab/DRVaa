import os
import time
import json
import pandas as pd
import ollama

# Record start time
start_time = time.time()

# Load existing metadata
csv_file = "street_segments_metadata_360.csv"
df = pd.read_csv(csv_file)

# Initialize new sensory columns PLUS the rationale
metrics = [
    "acoustic_comfort", "thermal_comfort", "somatic_stress", 
    "social_vitality", "territorial_safety", "olfactory_resonance", "rationale"
]
for metric in metrics:
    df[metric] = None

image_dir = "./streetview_panoramas_360"

# Define exact instructions for Qwen2.5-VL to ensure structured JSON output
system_prompt = """
You are an expert urban psychologist, spatial analyst, and pedestrian. Analyze the provided 360-degree street panorama and evaluate it across six affective dimensions.
Output ONLY a raw JSON object with no markdown formatting, no backticks, and no conversational text. Justify your scores with a very brief rationale in a separate column.
Use this exact structure, providing an integer score from 0 to 100 for each:
{
  "acoustic_comfort": 0,
  "thermal_comfort": 0,
  "somatic_stress": 0,
  "social_vitality": 0,
  "territorial_safety": 0,
  "olfactory_resonance": 0,
  "rationale": "Provide a concise justification for the scores, highlighting key environmental cues observed in the panorama."
}
"""

print("Starting local LLM analysis via Ollama (Qwen2.5-VL)...")

for index, row in df.iterrows():
    image_filename = row['image_file']
    if pd.isna(image_filename):
        continue
        
    image_path = os.path.join(image_dir, image_filename)
    if not os.path.exists(image_path):
        print(f"Skipping {image_filename} - File not found.")
        continue
        
    print(f"Analyzing {image_filename} ({index + 1}/{len(df)})...")
    
    try:
        # Send the 360° panorama to the MLLM with a structured prompt requesting a JSON evaluation
        response = ollama.chat(
            model='qwen2.5vl', # Other options: 'llava', 'llama3.2-vision', 'qwen2.5v1' 
            messages=[{
                'role': 'user',
                'content': system_prompt,
                'images': [image_path]
            }]
        )
        
        output_text = response['message']['content'].strip()
        
        # Clean potential markdown code blocks if the model ignores raw text instructions
        if output_text.startswith("```json"):
            output_text = output_text[7:-3].strip()
        elif output_text.startswith("```"):
            output_text = output_text[3:-3].strip()
            
        scores = json.loads(output_text)
        
        for metric in metrics:
            df.at[index, metric] = scores.get(metric, None)
            
    except Exception as e:
        print(f"Error analyzing {image_filename}: {e}\nRaw output: {output_text if 'output_text' in locals() else 'None'}")

output_csv = "street_segments_scored_360.csv"
df.to_csv(output_csv, index=False)
print(f"\nScoring complete! Data saved to {output_csv}")

# Calculate and display total execution time
end_time = time.time()
elapsed_time = end_time - start_time
minutes, seconds = divmod(elapsed_time, 60)
print(f"Total execution time: {int(minutes)} minutes and {seconds:.2f} seconds.")