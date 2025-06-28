import torch
from transformers import PreTrainedModel, PreTrainedTokenizer
from core.optimize import run_batch_generation, clean_output


def clean_code(code: str) -> str:
    """
    Clean a code block by removing comments and blank lines.

    Args:
        code (str): Raw source code.

    Returns:
        str: Cleaned code string with comments and blank lines removed.
    """
    lines = code.splitlines()
    cleaned = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith(("#", "//")):
            cleaned.append(line)
    return "\n".join(cleaned)


def build_prompt(code: str, model_tag: str = "CodeT5p") -> str:
    """
    Construct a docstring-generation prompt based on model type.

    Args:
        code (str): Cleaned code to generate a docstring for.
        model_tag (str): Identifier of the model (e.g., "CodeT5p", "DeepSeek-1.3B").

    Returns:
        str: Prompt string formatted for the specified model.
    """
    code = clean_code(code)
    if "codet5p" in model_tag.lower():
        return f"Generate a Python docstring for the following code:\n{code}\n\nDocstring:"
    else:
        return f"### Code:\n{code}\n\n### Docstring:"


def generate_docstring(
    code_snippets: list[str],
    tokenizer: PreTrainedTokenizer,
    model: PreTrainedModel,
    model_tag: str = "CodeT5p",
    batch_size: int = 4
) -> list[str]:
    """
    Generate Python-style docstrings for a list of code snippets.

    Args:
        code_snippets (list[str]): List of code strings.
        tokenizer (PreTrainedTokenizer): Tokenizer for the model.
        model (PreTrainedModel): Preloaded model for generation.
        model_tag (str): Model identifier string for prompt selection.
        batch_size (int): Number of prompts to batch per generation run.

    Returns:
        list[str]: Generated docstrings for the input code blocks.
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
