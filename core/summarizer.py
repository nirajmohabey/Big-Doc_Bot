import torch
from transformers import PreTrainedTokenizer, PreTrainedModel
from core.optimize import run_batch_generation, clean_output


def clean_code(code: str) -> str:
    """
    Remove comments and blank lines from a code snippet.

    Args:
        code (str): Raw code string.

    Returns:
        str: Cleaned code with comments and empty lines removed.
    """
    lines = code.splitlines()
    cleaned = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith(('#', '//')):
            cleaned.append(line)
    return "\n".join(cleaned).strip()


def build_prompt(code: str, model_name: str) -> str:
    """
    Build an instruction prompt tailored to the specified model.

    Args:
        code (str): Code to summarize.
        model_name (str): One of `"CodeT5p"` or `"DeepSeek-1.3B"`.

    Returns:
        str: Prompt string suitable for the model.
    """
    code = clean_code(code)
    if "codet5p" in model_name.lower():
        return f"Summarize this Python code:\n{code}\n\nSummary:"
    else:
        return f"### Code:\n{code}\n\n### Summary:"


def generate_summary(
    code_snippets: list[str],
    tokenizer: PreTrainedTokenizer,
    model: PreTrainedModel,
    model_tag: str = "CodeT5p",
    batch_size: int = 4
) -> list[str]:
    """
    Generate summaries for a list of code snippets using a transformer model.

    Args:
        code_snippets (list[str]): Code blocks to summarize.
        tokenizer (PreTrainedTokenizer): Tokenizer for the selected model.
        model (PreTrainedModel): The loaded transformer model.
        model_tag (str): Model identifier string (e.g., "CodeT5p").
        batch_size (int): Number of prompts to batch per forward pass.

    Returns:
        list[str]: Cleaned natural language summaries for each snippet.
    """
    prompts = [build_prompt(code, model_tag) for code in code_snippets]
    raw_outputs = run_batch_generation(
        model=model,
        tokenizer=tokenizer,
        prompts=prompts,
        max_tokens=128,
        batch_size=batch_size
    )
    return clean_output(raw_outputs, prompts)
