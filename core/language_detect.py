import re
from pygments.lexers import guess_lexer
from pygments.util import ClassNotFound


def _heuristic_score(code: str, language: str) -> int:
    """
    Compute language-specific pattern score for heuristic detection.

    Args:
        code (str): Code snippet.
        language (str): 'python' or 'javascript'.

    Returns:
        int: Number of matched patterns.
    """
    patterns = {
        "python": [
            r'\bdef\b', r'\bclass\b', r'\bself\b', r'\bimport\b',
            r':\s*(#.*)?\n\s+', r'\bprint\s*\(', r'^\s*@\w+',
            r'^\s*if __name__ == ["\']__main__["\']'
        ],
        "javascript": [
            r'\bfunction\b', r'\bconst\b', r'\blet\b', r'\bvar\b',
            r'=>', r'\bconsole\.log\b', r';\s*$', r'^\s*import\s+.*\s+from\s+["\']'
        ]
    }

    return sum(bool(re.search(pattern, code, re.MULTILINE)) for pattern in patterns[language])


def detect_language(code: str) -> str:
    """
    Detect the programming language from a code snippet.

    Uses heuristics and Pygments as fallback.

    Args:
        code (str): Raw code snippet.

    Returns:
        str: 'python', 'javascript', or 'unknown'
    """
    code = code.strip()
    if not code:
        return "unknown"

    # Apply heuristic detection first
    scores = {
        "python": _heuristic_score(code, "python"),
        "javascript": _heuristic_score(code, "javascript")
    }

    best_match = max(scores, key=scores.get)
    if scores[best_match] >= 2:
        return best_match

    # Fallback to Pygments if no clear winner
    try:
        lexer = guess_lexer(code)
        name = lexer.name.lower()
        if "python" in name:
            return "python"
        elif "javascript" in name or "js" in name:
            return "javascript"
    except ClassNotFound:
        pass

    return "unknown"
