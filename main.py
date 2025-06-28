import os
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    AutoModelForSeq2SeqLM
)
from transformers import BitsAndBytesConfig


@torch.inference_mode()
def load_doc_model(model_dir: str):
    """
    Load a transformer model (Causal or Seq2Seq) and tokenizer from local path.
    Automatically uses GPU if available. Supports DeepSeek-1.3B and CodeT5p.
    """
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)

        use_cuda = torch.cuda.is_available()
        device_map = "auto" if use_cuda else "cpu"
        dtype = torch.float16 if use_cuda else torch.float32

        if "1.3b" in model_dir.lower():
            model = AutoModelForCausalLM.from_pretrained(
                model_dir,
                device_map=device_map,
                torch_dtype=dtype,
                local_files_only=True
            )
        else:
            model = AutoModelForSeq2SeqLM.from_pretrained(
                model_dir,
                device_map=device_map,
                torch_dtype=dtype,
                local_files_only=True
            )

        model.eval()
        return tokenizer, model

    except Exception as e:
        print(f"[ERROR] Failed to load model from {model_dir}: {e}")
        return None
