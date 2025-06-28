import os

# Base directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")
REPORT_DIR = os.path.join(DATA_DIR, "reports")
RAW_REPO_DIR = os.path.join(DATA_DIR, "raw")

# Local model mappings
MODEL_PATHS = {
    "CodeT5p": os.path.join(MODEL_DIR, "codet5p-770m"),
    "DeepSeek-1.3B": os.path.join(MODEL_DIR, "deepseek-coder-1.3b-instruct")
}

# Data output paths
DOC_OUTPUT_PATH = os.path.join(DATA_DIR, "doc_output")
PROCESSED_PATH = os.path.join(DATA_DIR, "processed")

# Report template (optional if using Jinja)
TEMPLATE_PATH = os.path.join(BASE_DIR, "report_builder", "templates", "report_template.md")
