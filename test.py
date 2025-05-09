import logging
import time
import pandas as pd
from weather_fc import openai_chat

models_to_test = [
    'gpt-4.1-nano-2025-04-14',
    'gpt-4.1-mini-2025-04-14',
    'gpt-4o-mini-2024-07-18',
    'gpt-3.5-turbo-0125'
]

prompts = [
    ("What's the weather like in New York?", "Valid location"),
    ("Tell me the weather forecast for Tokyo.", "Valid location"),
    ("Can you check the weather in College Park?", "Valid location"),
    ("Is it raining today in Paris?", "Valid location"),
    ("Tell me a joke.", "Non-weather query"),
    ("Who won the last FIFA World Cup and who was the most important player of that tournament?", "Non-weather query"),
    ("What's the capital of Norway?", "Non-weather query"),
    ("Do you believe AI Engineering requires significant skill?", "Non-weather query"),
    ("What's the weather like?", "Ambiguous location"),
    ("Is it cold outside?", "Ambiguous location"),
    ("Weather in heaven?", "Nonexistent location"),
    ("How's the sky there?", "Ambiguous location"),
    ("What's the weather in London tomorrow?", "Location + Time"),
    ("Will it rain in Dallas this weekend?", "Location + Time"),
    ("How will the weather be in New Delhi on 2025-06-20?", "Location + Time"),
    ("What's the temperature in Rome next Monday?", "Location + Time"),
    ("What's the forecast for tomorrow?", "Time only"),
    ("What's the weather in College Park?", "Location only"),
    ("Tell me how hot it will be next Friday.", "Time only"),
    ("Next Tuesday's rain forecast?", "Time only"),
    ("Weather in Chicago on Thufriday.", "Invalid time format"),
    ("Forecast in Miami on 2025-99-99.", "Invalid time format"),
    ("Show me weather in Los Angeles next next Monday.", "Invalid time format")
]

# Results container
results = []

# Logging config (only once to avoid overlap)
logging.basicConfig(
    filename='weather_comparison_log.txt',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

for model in models_to_test:
    for prompt_text, category in prompts:
        print(f"\n--- [{model}] Executing {category} ---")
        try:
            response = openai_chat(prompt_text, model_name=model)
            print(f"User: {prompt_text}\nAssistant: {response[:150]}...\n")
            logging.info(f"[{model} | {category}] {prompt_text} => {response}")
            results.append({
                "Prompt": prompt_text,
                "Category": category,
                "Model": model,
                "Response": response
            })
            time.sleep(3)  # Delay to avoid rate limits
        except Exception as e:
            error_msg = f"Error on model {model} with prompt '{prompt_text}': {str(e)}"
            print(error_msg)
            logging.error(error_msg)
            results.append({
                "Prompt": prompt_text,
                "Category": category,
                "Model": model,
                "Response": f"ERROR: {str(e)}"
            })

df = pd.DataFrame(results)
df.to_csv("weather_model_comparison.csv", index=False)
markdown_path = "README.md"
with open(markdown_path, "w", encoding="utf-8") as md:
    md.write("# Weather Assistant Model Comparison\n\n")
    for prompt in prompts:
        md.write(f"## Prompt: {prompt[0]}\n")
        for model in models_to_test:
            filtered = df[(df["Prompt"] == prompt[0]) & (df["Model"] == model)]
            if not filtered.empty:
                response = filtered["Response"].values[0].replace("\n", "  \n")
                md.write(f"**{model}**:\n\n```\n{response}\n```\n\n")
        md.write("\n---\n")

print("✅ Comparison complete. Results saved to `weather_model_comparison.csv` and `README.md`.")
