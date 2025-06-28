import os
import json
import tempfile
import subprocess
import ast

def run_pylint_on_code(code: str) -> dict:
    """
    Run Pylint on a Python snippet and return quality metrics.

    Args:
        code (str): Python source code.

    Returns:
        dict: Includes `tool`, `num_issues`, `raw_output`.
    """
    # Catch syntax errors first
    try:
        ast.parse(code)
    except SyntaxError as e:
        return {
            "tool": "pylint",
            "num_issues": 1,
            "raw_output": f"[AST Parse Error] {e.msg} ({e.filename or '<unknown>'}, line {e.lineno})"
        }

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tmp:
        wrapped = "def main():\n"
        for line in code.splitlines():
            wrapped += f"    {line}\n" if line.strip() else "\n"
        wrapped += "\nif __name__ == '__main__':\n    main()\n"
        tmp.write(wrapped)
        tmp.flush()
        temp_path = tmp.name

    try:
        result = subprocess.run(
            ["pylint", temp_path, "--disable=all", "--enable=E,W", "--score=n", "--output-format=text"],
            capture_output=True, text=True, timeout=10
        )
        stdout = result.stdout.strip()
        issues = [line for line in stdout.splitlines() if ": warning" in line or ": error" in line]

    except Exception as e:
        stdout = f"[Pylint Runtime Error] {e}"
        issues = []

    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    return {
        "tool": "pylint",
        "num_issues": len(issues),
        "raw_output": stdout
    }


def run_eslint_on_code(code: str) -> dict:
    """
    Run ESLint on a JavaScript snippet and return quality metrics.

    Args:
        code (str): JavaScript code.

    Returns:
        dict: Includes `tool`, `num_issues`, `raw_output`.
    """
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as tmp:
        tmp.write(code)
        tmp.flush()
        temp_path = tmp.name

    try:
        result = subprocess.run(
            ["eslint", temp_path, "--format", "json"],
            capture_output=True, text=True, timeout=10
        )
        stdout = result.stdout.strip()
        try:
            parsed = json.loads(stdout)
            issues = parsed[0].get("messages", []) if parsed else []
        except json.JSONDecodeError:
            issues = []

    except Exception as e:
        stdout = f"[ESLint Runtime Error] {e}"
        issues = []

    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    return {
        "tool": "eslint",
        "num_issues": len(issues),
        "raw_output": stdout
    }


def run_code_quality(code: str, language: str) -> dict:
    """
    Dispatch to the appropriate linter based on language.

    Args:
        code (str): Code snippet.
        language (str): 'python' or 'javascript'.

    Returns:
        dict: Linter results.
    """
    if language == "python":
        return run_pylint_on_code(code)
    elif language == "javascript":
        return run_eslint_on_code(code)
    else:
        return {
            "tool": "unsupported",
            "num_issues": 0,
            "raw_output": "Unsupported language"
        }
