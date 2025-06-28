import os
import pandas as pd

def read_code_files(repo_root: str, extensions=(".py", ".js")):
    """
    Recursively walks through all repos under repo_root and collects code files.
    Returns a list of dictionaries with file_path and code content.
    """
    code_files = []

    for repo_name in os.listdir(repo_root):
        repo_path = os.path.join(repo_root, repo_name)
        if not os.path.isdir(repo_path):
            continue

        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.lower().endswith(extensions):
                    full_path = os.path.join(root, file)
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read().strip()
                            if content:
                                code_files.append({
                                    "repo": repo_name,
                                    "file_path": full_path,
                                    "content": content
                                })
                    except Exception as e:
                        print(f"[SKIP] {full_path} due to error: {e}")

    return code_files


if __name__ == "__main__":
    raw_dir = "data/raw"
    output_path = "data/processed/all_repos_code.json"

    print(f"Scanning all code in: {raw_dir}")
    data = read_code_files(raw_dir)
    print(f"Extracted {len(data):,} code files.")

    # Save to disk
    os.makedirs("data/processed", exist_ok=True)
    df = pd.DataFrame(data)
    df.to_json(output_path, orient="records", lines=True)

    print(f"Saved extracted code to: {output_path}")
