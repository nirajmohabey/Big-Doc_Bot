import os
os.environ["USE_TF"] = "0"
import json
import torch
import logging
from tqdm import tqdm
from datetime import datetime
from datasets import load_from_disk
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Setup logging
os.makedirs("logs/summarizer", exist_ok=True)
log_file = f"logs/summarizer/summarizer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Configure device and speed settings
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
torch.set_float32_matmul_precision("high")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logging.info(f"Using device: {device}")

MODEL_NAME = "Salesforce/codet5-base-multi-sum"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
).to(device)
model.eval()

if torch.__version__ >= "2" and torch.cuda.is_available():
    model = torch.compile(model)

def generate_summary(batch, max_input_length=256, max_output_length=64):
    prompts = [f"summarize: {code}" for code in batch["code"]]
    inputs = tokenizer(
        prompts,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=max_input_length
    ).to(device)

    with torch.no_grad():
        outputs = model.generate(
            inputs.input_ids,
            num_beams=1,
            early_stopping=True,
            max_length=max_output_length
        )

    decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)
    return {"summary": [s.strip() for s in decoded]}

def summarize_hf_fast(input_dir, output_dir):
    if os.path.exists(output_dir):
        logging.info(f"Cached: {output_dir} already exists. Skipping...")
        return

    logging.info(f"Loading dataset from: {input_dir}")
    dataset = load_from_disk(input_dir)
    logging.info(f"Found {len(dataset)} samples")

    summarized = dataset.map(
        generate_summary,
        batched=True,
        batch_size=128,
        desc="Generating summaries"
    )

    os.makedirs(output_dir, exist_ok=True)
    summarized.save_to_disk(output_dir)
    logging.info(f"Saved summarized dataset to: {output_dir}")

def summarize_json(input_path, output_path, code_key="content", batch_size=128, max_input_length=256, max_output_length=64, resume=True):
    logging.info(f"Streaming and summarizing JSON from: {input_path}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cache_path = os.path.splitext(output_path)[0] + ".cache.json"
    completed_hashes = set()

    if resume and os.path.exists(cache_path):
        logging.info("Loading cache from: %s", cache_path)
        with open(cache_path, "r", encoding="utf-8") as f:
            try:
                completed_hashes = set(json.load(f))
            except:
                completed_hashes = set()

    batch_counter = 0
    with open(input_path, "r", encoding="utf-8") as infile, open(output_path, "a", encoding="utf-8") as outfile:
        buffer = []
        for line in tqdm(infile, desc="Processing JSON"):
            obj = json.loads(line)
            code_hash = hash(obj[code_key])

            if resume and code_hash in completed_hashes:
                continue

            buffer.append((code_hash, obj))

            if len(buffer) == batch_size:
                batch_counter += 1
                _process_and_write(buffer, outfile, code_key, max_input_length, max_output_length, completed_hashes)
                if batch_counter % 10 == 0:
                    with open(cache_path, "w", encoding="utf-8") as f:
                        json.dump(list(completed_hashes), f)
                buffer = []

        if buffer:
            _process_and_write(buffer, outfile, code_key, max_input_length, max_output_length, completed_hashes)
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(list(completed_hashes), f)

    logging.info(f"Saved summarized file to: {output_path}")

def _process_and_write(buffer, outfile, code_key, max_input_length, max_output_length, completed_hashes):
    code_snippets = [obj[code_key] for _, obj in buffer]
    prompts = [f"summarize: {code}" for code in code_snippets]

    inputs = tokenizer(
        prompts,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=max_input_length
    ).to(device)

    with torch.no_grad():
        outputs = model.generate(
            inputs.input_ids,
            num_beams=1,
            early_stopping=True,
            max_length=max_output_length
        )

    summaries = tokenizer.batch_decode(outputs, skip_special_tokens=True)
    for i, (code_hash, obj) in enumerate(buffer):
        obj["summary"] = summaries[i].strip()
        outfile.write(json.dumps(obj) + "\n")
        completed_hashes.add(code_hash)

if __name__ == "__main__":
    summarize_hf_fast(
        input_dir="data/processed/codesearchnet_python_train",
        output_dir="data/processed/codesearchnet_python_train_summarized"
    )

    summarize_hf_fast(
        input_dir="data/processed/codesearchnet_javascript_train",
        output_dir="data/processed/codesearchnet_javascript_train_summarized"
    )

    summarize_json(
        input_path="data/processed/all_repos_code.json",
        output_path="data/processed/all_repos_code_summarized.json"
    )