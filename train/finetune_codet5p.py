import os
import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, TrainingArguments, Trainer, DataCollatorForSeq2Seq
from peft import get_peft_model, LoraConfig, TaskType

# Paths
MODEL_ID = "Salesforce/codet5p-770m"
MODEL_DIR = "models/codet5p-770m"
DATA_PATH = "data/processed/all_repos_code_summarized.json"

# Load tokenizer and base model
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_ID, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32)

# Apply LoRA for lightweight fine-tuning
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.SEQ_2_SEQ_LM
)
model = get_peft_model(model, lora_config)

# Load and preprocess dataset
dataset = load_dataset("json", data_files={"train": DATA_PATH})["train"]

def preprocess(example):
    input = tokenizer(example["content"], padding="max_length", truncation=True, max_length=512)
    label = tokenizer(example["summary"], padding="max_length", truncation=True, max_length=128)
    input["labels"] = label["input_ids"]
    return input

dataset = dataset.map(preprocess, remove_columns=dataset.column_names)

# Training arguments
training_args = TrainingArguments(
    output_dir=MODEL_DIR,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    num_train_epochs=3,
    learning_rate=3e-4,
    fp16=True,
    save_strategy="epoch",
    logging_steps=50,
    save_total_limit=2,
    evaluation_strategy="no",
    report_to="none"
)

# Setup trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer,
    data_collator=DataCollatorForSeq2Seq(tokenizer, model=model)
)

# Train and save
trainer.train()
trainer.save_model(MODEL_DIR)
tokenizer.save_pretrained(MODEL_DIR)
