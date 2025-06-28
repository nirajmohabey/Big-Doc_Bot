# docgen_all_repos.py

import os
import json
import torch
import evaluate
import csv
import re
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoConfig, BitsAndBytesConfig
from datasets import load_from_disk
from torch.amp import autocast

# Create directories
os.makedirs("logs", exist_ok=True)
os.makedirs("data/reports", exist_ok=True)
os.makedirs("data/doc_output", exist_ok=True)
os.makedirs("models", exist_ok=True)

# Config
MODEL_TAG = "codet5p"
MODEL_ID = "Salesforce/codet5p-770m"
MODEL_DIR = f"models/{MODEL_ID.split('/')[-1]}"
BATCH_SIZE = 128

# Device settings
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
torch.set_float32_matmul_precision("high")

# Quantization settings
QUANT_CONFIG = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=6.0,
    llm_int8_has_fp16_weight=False,
    bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32
)

# Evaluators
bleu = evaluate.load("bleu")
rouge = evaluate.load("rouge")
rouge_scores = []
bleu_scores = []
lang_scores = {"python": [], "javascript": []}

def detect_language(code: str) -> str:
    if re.search(r"function\s+\w+\s*\(|=>", code) or "console.log" in code:
        return "javascript"
    return "python"

def load_model():
    model_path = MODEL_DIR if os.path.exists(MODEL_DIR) else MODEL_ID
    print("Loading model from:", model_path)

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    config = AutoConfig.from_pretrained(model_path)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id

    model = AutoModelForSeq2SeqLM.from_pretrained(
        model_path,
        device_map="auto",
        quantization_config=QUANT_CONFIG
    )
    model.eval()
    return tokenizer, model

def build_prompt(code):
    return f"""### Code:\n{code}\n\n### Docstring:\n"""

def process_all_repos(input_path, output_path):
    if os.path.isdir(input_path):
        dataset = load_from_disk(input_path)
        data = dataset.to_list()
    else:
        with open(input_path, "r", encoding="utf-8") as f:
            data = [json.loads(line) for line in f]

    if not data:
        print("No data found.")
        return

    print("Sample keys:", list(data[0].keys()))
    code_key = "content"
    reference_key = "summary"

    results = []
    cache_path = output_path.replace(".json", ".partial.json")
    completed = 0
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            results = [json.loads(line) for line in f]
        completed = len(results)

    tokenizer, model = load_model()

    for i in tqdm(range(completed, len(data), BATCH_SIZE), desc=f"Processing {input_path}"):
        batch = data[i:i + BATCH_SIZE]
        batch = [item for item in batch if code_key in item and isinstance(item[code_key], str)]
        if not batch:
            continue

        prompts = [build_prompt(item[code_key][:1000]) for item in batch]
        langs = [item.get("language") or detect_language(item[code_key]) for item in batch]

        with torch.inference_mode(), autocast(device_type="cuda"):
            inputs = tokenizer(prompts, return_tensors="pt", padding=True, truncation=True, max_length=512).to(device)
            outputs = model.generate(inputs.input_ids, max_new_tokens=64, do_sample=False, num_beams=1)
            decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)

        for j, item in enumerate(batch):
            reference = item.get(reference_key, "")
            prediction = decoded[j].strip()
            item["docstring"] = prediction
            item["model_used"] = MODEL_TAG
            item["language"] = langs[j]
            results.append(item)

            if reference.strip():
                r = rouge.compute(predictions=[prediction], references=[reference])
                try:
                    if len(reference.split()) > 0:
                        b = bleu.compute(predictions=[prediction], references=[reference])
                        bleu_scores.append(b["bleu"])
                except ZeroDivisionError:
                    pass
                rouge_scores.append(r["rougeL"])
                lang_scores[langs[j]].append(r["rougeL"])

        with open(cache_path, "a", encoding="utf-8") as f:
            for item in batch:
                f.write(json.dumps(item) + "\n")

    if os.path.exists(cache_path):
        os.replace(cache_path, output_path)
        print(f"Saved to: {output_path}")

    with open("data/reports/all_repos_model_scores.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Average"])
        if rouge_scores:
            writer.writerow(["ROUGE-L", round(sum(rouge_scores) / len(rouge_scores), 4)])
        if bleu_scores:
            writer.writerow(["BLEU", round(sum(bleu_scores) / len(bleu_scores), 4)])

    with open("data/reports/all_repos_language_model_scores.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Language", "Avg_ROUGE_L"])
        for lang, scores in lang_scores.items():
            avg = round(sum(scores) / len(scores), 4) if scores else 0
            writer.writerow([lang, avg])

if __name__ == "__main__":
    import sys
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    process_all_repos(input_file, output_file)
