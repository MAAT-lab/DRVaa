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

# Column names in your DataFrame
metrics = [
    "acoustic",
    "thermal",
    "stress",
    "social",
    "safety",
    "olfactory",
    "rationale",
]
for metric in metrics:
    df[metric] = None

image_dir = "./streetview_panoramas_360"

# Updated system prompt using exact matching JSON keys
system_prompt = """
You are an expert urban psychologist, spatial analyst, and pedestrian. Analyze the provided 360-degree street panorama and evaluate it across six affective dimensions: acoustic (acoustic comfort), thermal (thermal comfort), stress (somatic stress and stress-inducing factors), social (social vitality and engagement), safety (perceived territorial safety and security), and olfactory (olfactory resonance).
For acoustic comfort consider possitive and negative sound sources, such as traffic noise, construction, or natural sounds. For thermal comfort, consider shade, sun exposure, and wind. For stress, consider visual clutter, traffic density, and environmental stressors. For social vitality, consider the presence of people, social interactions, and community engagement. For safety, consider lighting, visibility, and signs of crime or neglect and avoiding highways as they are high-risk areas for pedestrian accidents. For olfactory resonance, consider the presence of pleasant or unpleasant odors.
Output ONLY a raw JSON object with no markdown formatting, no backticks, and no conversational text. Justify your scores with a very brief rationale in a separate field.
Use this exact structure, providing an integer score from 0 to 100 for each:
{
  "acoustic": 0,
  "thermal": 0,
  "stress": 0,
  "social": 0,
  "safety": 0,
  "olfactory": 0,
  "rationale": "Provide a concise justification for each of the scores, highlighting key environmental cues observed in the panorama."
}
"""

print("Starting local LLM analysis via Ollama (Qwen2.5-VL)...")

# for index, row in df.iloc[6:11].iterrows():  # Testing only first 5 images
for index, row in df.iterrows(): # Full run with all images
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

        # Extract values using exact matching keys
        for metric in metrics:
            df.at[index, metric] = scores.get(metric, None)

    except Exception as e:
        print(
            f"Error analyzing {image_filename}: {e}\nRaw output:"
            f" {output_text if 'output_text' in locals() else 'None'}"
        )

# Save output
output_csv = "street_segments_scored_360_rationale.csv"
df.to_csv(output_csv, index=False)
print(f"\nScoring complete! Data saved to {output_csv}")

# Execution time
end_time = time.time()
elapsed_time = end_time - start_time
minutes, seconds = divmod(elapsed_time, 60)
print(
    f"Total execution time: {int(minutes)} minutes and {seconds:.2f} seconds."
)