def format_summary_blocks(summaries: list[str]) -> list[dict]:
    """
    Convert raw summary strings into structured blocks.

    Args:
        summaries (list[str]): List of summary texts.

    Returns:
        list[dict]: List of summary blocks with 'summary' key.
    """
    return [{"summary": s.strip()} for s in summaries if s.strip()]


def format_docstring_blocks(docstrings: list[str]) -> list[dict]:
    """
    Convert model-generated docstrings into structured documentation entries.

    Args:
        docstrings (list[str]): Generated docstrings.

    Returns:
        list[dict]: List of docstring blocks with 'summary' key.
    """
    return [{"summary": d.strip()} for d in docstrings if d.strip()]


def format_quality_result(results: list[dict]) -> list[dict]:
    """
    Structure code quality analysis results.

    Args:
        results (list[dict]): Raw quality results from linters.

    Returns:
        list[dict]: Cleaned quality blocks with essential metrics.
    """
    return [
        {
            "tool": r.get("tool", "unknown"),
            "num_issues": r.get("num_issues", 0),
            "raw_output": r.get("raw_output", "")
        }
        for r in results
    ]
