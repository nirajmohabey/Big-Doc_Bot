import requests
import nbformat
from urllib.parse import urlparse

GITHUB_API_BASE = "https://api.github.com/repos"
RAW_BASE = "https://raw.githubusercontent.com"


def extract_code_from_notebook(notebook_str: str) -> str:
    """
    Extracts all code cells from a Jupyter notebook string.

    Args:
        notebook_str (str): Raw .ipynb JSON string.

    Returns:
        str: Concatenated code from all code cells.
    """
    try:
        nb = nbformat.reads(notebook_str, as_version=4)
        code_cells = [cell["source"] for cell in nb.cells if cell.cell_type == "code"]
        return "\n\n".join(code_cells)
    except Exception as e:
        print(f"[Notebook Parse Error] {e}")
        return ""


def fetch_python_and_js_files_from_repo(repo_url: str, include_ipynb: bool = True) -> list[str]:
    """
    Fetch .py, .js, and optionally .ipynb (code only) file contents from a public GitHub repo (main branch assumed).

    Args:
        repo_url (str): GitHub repo URL (e.g., https://github.com/user/repo)
        include_ipynb (bool): Whether to include Jupyter Notebook code.

    Returns:
        list[str]: List of code file contents (as strings)
    """
    if "github.com" not in repo_url:
        print("[Invalid URL] Must be a valid GitHub repo link.")
        return []

    parsed = urlparse(repo_url)
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 2:
        return []

    user, repo = parts[:2]
    base_raw_url = f"{RAW_BASE}/{user}/{repo}/main"
    tree_url = f"{GITHUB_API_BASE}/{user}/{repo}/git/trees/main?recursive=1"

    try:
        response = requests.get(tree_url)
        if response.status_code != 200:
            print(f"[GitHub API Error] Status {response.status_code}")
            return []

        code_files = []
        for item in response.json().get("tree", []):
            path = item.get("path", "")
            if path.endswith(".py") or path.endswith(".js") or (include_ipynb and path.endswith(".ipynb")):
                raw_url = f"{base_raw_url}/{path}"
                raw_response = requests.get(raw_url)
                if raw_response.status_code == 200:
                    if path.endswith(".ipynb"):
                        code = extract_code_from_notebook(raw_response.text)
                    else:
                        code = raw_response.text

                    if code.strip():
                        code_files.append(code)

        return code_files

    except Exception as e:
        print(f"[Error fetching repo files] {e}")
        return []
