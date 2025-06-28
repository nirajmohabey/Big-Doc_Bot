import os
import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from peft import get_peft_model, LoraConfig, TaskType

# Paths
MODEL_ID = "deepseek-ai/deepseek-coder-1.3b"
MODEL_DIR = "models/deepseek-coder-1.3b"
DATA_PATH = "data/processed/all_repos_code_summarized.json"

# Load tokenizer and base model
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    trust_remote_code=True
)

# Apply LoRA for efficient fine-tuning
lora_config = LoraConfig(
    r=8,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)
model = get_peft_model(model, lora_config)

# Load dataset
dataset = load_dataset("json", data_files={"train": DATA_PATH})["train"]

def build_prompt(example):
    return f"### Code:\n{example['content']}\n\n### Summary:\n{example['summary']}"

def preprocess(example):
    prompt = build_prompt(example)
    tokenized = tokenizer(prompt, truncation=True, padding="max_length", max_length=1024)
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized

dataset = dataset.map(preprocess, remove_columns=dataset.column_names)

# Training configuration
training_args = TrainingArguments(
    output_dir=MODEL_DIR,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    num_train_epochs=3,
    learning_rate=2e-4,
    fp16=True,
    save_strategy="epoch",
    logging_steps=50,
    save_total_limit=2,
    evaluation_strategy="no",
    report_to="none"
)

# Use standard causal LM collator
collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# Trainer setup
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer,
    data_collator=collator
)

# Train and save
trainer.train()
trainer.save_model(MODEL_DIR)
tokenizer.save_pretrained(MODEL_DIR)
