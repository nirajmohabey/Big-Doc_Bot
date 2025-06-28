import os
import git
import requests
import concurrent.futures
from urllib.parse import urlparse

GITHUB_API_URL = "https://api.github.com/search/repositories"
HEADERS = {"Accept": "application/vnd.github.v3+json"}


def get_repo_name_from_url(repo_url: str) -> str:
    return os.path.splitext(os.path.basename(urlparse(repo_url).path))[0]


def clone_single_repo(repo_url: str, base_dir: str = "data/raw") -> str:
    repo_name = get_repo_name_from_url(repo_url)
    local_path = os.path.join(base_dir, repo_name)

    if os.path.exists(local_path):
        print(f"[SKIP] {repo_name} already exists.")
        return local_path

    print(f"[CLONE] {repo_url} -> {local_path}")
    try:
        os.makedirs(base_dir, exist_ok=True)
        git.Repo.clone_from(repo_url, local_path)
        print(f"[OK] {repo_name} cloned.")
    except Exception as e:
        print(f"[ERROR] Failed to clone {repo_url}: {e}")
        return None

    return local_path


def fetch_top_repos(language="python", max_repos=10):
    print(f"Searching top {max_repos} GitHub repos for language: {language}")
    params = {
        "q": f"language:{language}",
        "sort": "stars",
        "order": "desc",
        "per_page": max_repos
    }
    response = requests.get(GITHUB_API_URL, params=params, headers=HEADERS)
    response.raise_for_status()
    items = response.json()["items"]
    return [item["clone_url"] for item in items]


def clone_multiple_repos(repo_urls: list, base_dir: str = "data/raw", max_workers: int = 5):
    print(f"Cloning {len(repo_urls)} repositories with {max_workers} threads...\n")
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {
            executor.submit(clone_single_repo, url, base_dir): url for url in repo_urls
        }
        for future in concurrent.futures.as_completed(future_to_url):
            result = future.result()
            if result:
                results.append(result)

    print(f"\nFinished cloning {len(results)} repositories.")
    return results


if __name__ == "__main__":
    try:
        python_repos = fetch_top_repos(language="python", max_repos=10)
        javascript_repos = fetch_top_repos(language="javascript", max_repos=10)
        all_repos = python_repos + javascript_repos

        clone_multiple_repos(
            repo_urls=all_repos,
            base_dir="data/raw",
            max_workers=5
        )
    except Exception as e:
        print(f"Error: {e}")
