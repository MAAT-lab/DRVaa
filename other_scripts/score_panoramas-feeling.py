import json
import os
import time
import pandas as pd
import ollama

# Record start time
start_time = time.time()

# Load existing metadata
csv_file = "street_segments_metadata_360.csv"
df = pd.read_csv(csv_file)

# Updated qualitative columns for the exploratory project
metrics = [
    "primary_emotion",
    "sensory_triggers",
    "spatial_feeling"
]
for metric in metrics:
    df[metric] = None

image_dir = "./streetview_panoramas_360"

# Updated system prompt focusing purely on emotional and atmospheric resonance
system_prompt = """
You are an observant pedestrian and urban flâneur. Look at the provided 360-degree street panorama and describe exactly how this space feels to be in. Focus on the emotional resonance, the atmosphere, and the overall psychological vibe of the environment.
Output ONLY a raw JSON object with no markdown formatting, no backticks, and no conversational text. 
Use this exact structure:
{
  "primary_emotion": "A single word or short phrase capturing the dominant feeling (e.g., Restless, Sheltered, Melancholic, Invigorating).",
  "sensory_triggers": "A brief list of 2-3 specific visual elements in the image that evoke this feeling.",
  "spatial_feeling": "Provide a 2-3 sentence descriptive narrative of what it actually feels like to stand in this specific environment."
}
"""

print("Starting qualitative LLM analysis via Ollama (Qwen2.5-VL)...")

for index, row in df.iterrows():
    image_filename = row["image_file"]
    if pd.isna(image_filename):
        continue

    image_path = os.path.join(image_dir, image_filename)
    if not os.path.exists(image_path):
        print(f"Skipping {image_filename} - File not found.")
        continue

    print(f"Analyzing {image_filename} ({index + 1}/{len(df)})...")

    try:
        response = ollama.chat(
            model="qwen2.5vl",
            messages=[{
                "role": "user",
                "content": system_prompt,
                "images": [image_path],
            }],
        )

        output_text = response["message"]["content"].strip()

        # Strip markdown code blocks if present
        if output_text.startswith("```json"):
            output_text = output_text[7:-3].strip()
        elif output_text.startswith("```"):
            output_text = output_text[3:-3].strip()

        scores = json.loads(output_text)

        # Extract qualitative values
        for metric in metrics:
            df.at[index, metric] = scores.get(metric, None)

    except Exception as e:
        print(
            f"Error analyzing {image_filename}: {e}\nRaw output:"
            f" {output_text if 'output_text' in locals() else 'None'}"
        )

# Save output to a newly named file to avoid overwriting your quantitative data
output_csv = "street_segments_feelings_360.csv"
df.to_csv(output_csv, index=False)
print(f"\nExploratory analysis complete! Qualitative data saved to {output_csv}")

# Execution time
end_time = time.time()
elapsed_time = end_time - start_time
minutes, seconds = divmod(elapsed_time, 60)
print(f"Total execution time: {int(minutes)} minutes and {seconds:.2f} seconds.")