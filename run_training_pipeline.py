import os

# Step 1: Extract code from raw GitHub repositories
print("\n[STEP 1] Extracting code from 'data/raw/' ...")
os.system("python scripts/repo_reader.py")

# Step 2: Summarize each code block to generate training data
print("\n[STEP 2] Summarizing code into natural language descriptions ...")
os.system("python scripts/train_summarizer.py")

# Step 3: Generate docstrings using both models
for model in ["codet5p", "deepseek"]:
    print(f"\n[STEP 3] Generating docstrings using model: {model}")
    output_json = f"data/doc_output/all_repos_docstrings_{model}.json"
    os.system(
        f"python scripts/train_doc_generator.py data/processed/all_repos_code_summarized.json {output_json} --model {model}"
    )

print("\nPipeline complete!")
print("Generated files:")
print("  - data/processed/all_repos_code.json")
print("  - data/processed/all_repos_code_summarized.json")
print("  - data/doc_output/all_repos_docstrings_codet5p.json")
print("  - data/doc_output/all_repos_docstrings_deepseek.json")
print("  - data/reports/*.csv")
