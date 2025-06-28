from datasets import load_dataset, Dataset
import os

try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda x: x


def load_codesearchnet_subsets(languages=["python", "javascript"], split="train", sample_limit=None):
    for lang in languages:
        print(f"\nLoading CodeSearchNet for '{lang}'...")

        try:
            dataset = load_dataset("code_search_net", name=lang, split=split, trust_remote_code=True)
        except Exception as e:
            print(f"ERROR: Failed to load dataset for {lang}: {e}")
            continue

        if sample_limit:
            dataset = dataset.select(range(min(sample_limit, len(dataset))))
            print(f"Limiting to {len(dataset)} samples")

        print(f"Available keys: {list(dataset[0].keys())}")

        # Preview first valid sample
        try:
            sample_preview = {
                "func_name": dataset[0].get("func_name", ""),
                "func_code_string": dataset[0].get("func_code_string", "")[:100] + "...",
                "func_documentation_string": dataset[0].get("func_documentation_string", "")[:100] + "..."
            }
            print("First sample preview (truncated):")
            print(str(sample_preview).encode('ascii', 'ignore').decode())
        except Exception as e:
            print(f"Preview failed: {e}")

        processed_samples = []
        for item in tqdm(dataset, desc=f"Processing {lang}"):
            func = item.get("func_code_string")
            doc = item.get("func_documentation_string")
            if func and doc:
                processed_samples.append({
                    "file_path": item.get("func_path_in_repository", ""),
                    "function_name": item.get("func_name", ""),
                    "code": func,
                    "docstring": doc,
                    "summary": "",
                    "quality_score": None
                })

        if not processed_samples:
            print(f"No valid examples found for {lang}. Skipping save.\n")
            continue

        hf_dataset = Dataset.from_list(processed_samples)
        output_dir = f"data/processed/codesearchnet_{lang}_{split}"
        os.makedirs(output_dir, exist_ok=True)
        hf_dataset.save_to_disk(output_dir)

        print(f"\nSaved {len(hf_dataset)} samples to {output_dir}")


if __name__ == "__main__":
    load_codesearchnet_subsets(
        languages=["python", "javascript"],
        split="train",
        sample_limit=None 
    )
