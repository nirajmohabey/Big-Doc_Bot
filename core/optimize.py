import torch
from transformers import PreTrainedModel, PreTrainedTokenizer

def run_batch_generation(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    prompts: list[str],
    max_tokens: int = 256,
    batch_size: int = 4,
    device: str = None
) -> list[str]:
    """
    Run batched generation with AMP optimization.

    Args:
        - `model` (PreTrainedModel): Hugging Face model.
        - `tokenizer` (PreTrainedTokenizer): Corresponding tokenizer.
        - `prompts` (list[str]): List of input prompts.
        - `max_tokens` (int): Max new tokens to generate per output.
        - `batch_size` (int): Number of prompts processed per batch.
        - `device` (str): Optional device override (e.g. "cuda").

    Returns:
        - `list[str]`: Generated completions per prompt.
    """
    model.eval()
    device = device or (model.device if hasattr(model, 'device') else ("cuda" if torch.cuda.is_available() else "cpu"))
    device_str = str(device)
    all_outputs = []

    for i in range(0, len(prompts), batch_size):
        batch = prompts[i:i + batch_size]
        inputs = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=512)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.inference_mode(), torch.amp.autocast(device_type="cuda" if "cuda" in device_str else "cpu"):
            outputs = model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs.get("attention_mask"),
                max_new_tokens=max_tokens,
                do_sample=True,
                top_p=0.95,
                pad_token_id=tokenizer.eos_token_id
            )

        decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        all_outputs.extend(decoded)

    return all_outputs

def clean_output(raw_outputs: list[str], prompts: list[str]) -> list[str]:
    """
    Clean generated outputs by removing prompt echoes and standard prefixes.

    Args:
        - `raw_outputs` (list[str]): Raw model outputs.
        - `prompts` (list[str]): Original prompts.

    Returns:
        - `list[str]`: Cleaned output strings.
    """
    cleaned = []
    for out, prompt in zip(raw_outputs, prompts):
        text = out.replace(prompt, "").strip()
        for intro in [
            "Summary:", "Docstring:",
            "Summarize this Python code:",
            "Generate a Python docstring for the following code:"
        ]:
            if text.lower().startswith(intro.lower()):
                text = text[len(intro):].strip()
        cleaned.append(text)
    return cleaned
