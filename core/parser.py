import ast
import re
from typing import List


def extract_python_code_blocks(code: str) -> List[str]:
    """
    Extract top-level function and class definitions from Python source code.

    Args:
        code (str): Raw Python code.

    Returns:
        List[str]: List of code blocks (functions or classes).
    """
    blocks = []
    try:
        tree = ast.parse(code)
        lines = code.splitlines()
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start_line = node.lineno - 1
                # For Python <3.8 fallback
                end_line = getattr(node, "end_lineno", node.body[-1].lineno if hasattr(node, "body") and node.body else node.lineno)
                snippet = "\n".join(lines[start_line:end_line])
                blocks.append(snippet)
    except Exception as e:
        print(f"[AST Parse Error] {e}")
    return blocks


def extract_javascript_functions(code: str) -> List[str]:
    """
    Extract basic function and arrow function blocks from JavaScript code.

    Args:
        code (str): Raw JavaScript code.

    Returns:
        List[str]: Extracted function blocks (as strings).
    """
    function_pattern = re.compile(r'(function\s+\w+\s*\([^)]*\)\s*{[^}]*})', re.DOTALL)
    arrow_function_pattern = re.compile(r'(\w+\s*=\s*\([^)]*\)\s*=>\s*{[^}]*})', re.DOTALL)
    return function_pattern.findall(code) + arrow_function_pattern.findall(code)


def clean_code_block(block: str) -> str:
    """
    Clean a code block by removing inline comments and excess whitespace.

    Args:
        block (str): Code block.

    Returns:
        str: Cleaned code.
    """
    lines = block.splitlines()
    cleaned = []
    in_multiline_comment = False

    for line in lines:
        line = line.strip()

        if not line:
            continue
        if line.startswith("#") or line.startswith("//"):
            continue
        if "/*" in line:
            in_multiline_comment = True
            continue
        if "*/" in line:
            in_multiline_comment = False
            continue
        if not in_multiline_comment:
            cleaned.append(line)

    return "\n".join(cleaned).strip()


def extract_code_snippets(code: str, language: str) -> List[str]:
    """
    Extract and clean meaningful code blocks from source code based on language.

    Args:
        code (str): Full source code.
        language (str): "python" or "javascript".

    Returns:
        List[str]: Cleaned function/class snippets.
    """
    if language == "python":
        blocks = extract_python_code_blocks(code)
    elif language == "javascript":
        blocks = extract_javascript_functions(code)
    else:
        return []

    return list({
        clean_code_block(b) for b in blocks if len(b.strip()) > 5
    })
