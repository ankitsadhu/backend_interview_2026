# End-to-End LoRA Training Workflow

## Goal

This file shows a practical LoRA fine-tuning workflow for an instruction-tuned causal language model.

The goal is not to memorize one exact script, but to understand the stages clearly enough to explain and implement them.

## End-to-End Flow

```text
Choose base model
   |
   v
Prepare dataset
   |
   v
Tokenize / format prompts
   |
   v
Load base model
   |
   v
Attach LoRA adapters
   |
   v
Train
   |
   v
Evaluate
   |
   v
Save adapter
   |
   v
Load adapter for inference
```

## Step 1: Choose the Base Model

Pick a model that matches:

- task type
- hardware budget
- licensing constraints
- context length requirements

Examples:

- smaller open model for experimentation
- 7B instruction-tuned model for practical SFT

Strong interview point:

Base model choice matters as much as the tuning method.

## Step 2: Prepare the Dataset

For instruction tuning, a common format is:

```json
{
  "instruction": "Classify the support ticket.",
  "input": "Customer says they were charged twice.",
  "output": "{\"label\": \"billing\"}"
}
```

The dataset should be:

- clean
- task-aligned
- consistent in output style
- realistic

## Step 3: Convert to Prompt Format

One common formatting function:

```python
def format_example(example):
    return (
        f"### Instruction:\n{example['instruction']}\n\n"
        f"### Input:\n{example['input']}\n\n"
        f"### Response:\n{example['output']}"
    )
```

## Step 4: Load Tokenizer and Model

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "gpt2"

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(model_name)
```

In practice you would often use a stronger instruction-tuned open model.

## Step 5: Attach LoRA

```python
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
```

This confirms only adapter parameters are trainable.

## Step 6: Tokenize the Dataset

```python
from datasets import Dataset

train_rows = [
    {
        "instruction": "Classify the support ticket.",
        "input": "Customer says they were charged twice.",
        "output": "{\"label\": \"billing\"}",
    },
    {
        "instruction": "Classify the support ticket.",
        "input": "Package has not arrived yet.",
        "output": "{\"label\": \"shipping\"}",
    },
]

dataset = Dataset.from_list(train_rows)

def tokenize_function(example):
    text = format_example(example)
    return tokenizer(
        text,
        truncation=True,
        max_length=256,
        padding="max_length",
    )

tokenized_dataset = dataset.map(tokenize_function)
```

## Step 7: Train

Using the standard Hugging Face `Trainer`:

```python
from transformers import TrainingArguments, Trainer

training_args = TrainingArguments(
    output_dir="./lora-output",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    num_train_epochs=3,
    logging_steps=10,
    save_steps=100,
    fp16=False,
    bf16=False,
    report_to="none",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
)

trainer.train()
```

For real instruction-tuning pipelines, `SFTTrainer` or custom collators are often more convenient.

## Step 8: Save Adapter

```python
model.save_pretrained("./support-lora-adapter")
tokenizer.save_pretrained("./support-lora-adapter")
```

This usually saves only the adapter-related artifacts, not a full giant copy of the base model.

## Step 9: Load for Inference

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

base_model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained("./support-lora-adapter")

inference_model = PeftModel.from_pretrained(
    base_model,
    "./support-lora-adapter",
)
```

Now inference uses the base model plus the trained adapter.

## Step 10: Generate

```python
prompt = """### Instruction:
Classify the support ticket.

### Input:
Customer says they were charged twice.

### Response:
"""

inputs = tokenizer(prompt, return_tensors="pt")
outputs = inference_model.generate(**inputs, max_new_tokens=50)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

## QLoRA Variant

If hardware is limited, the common change is:

1. load the base model in 4-bit
2. prepare it for k-bit training
3. add LoRA adapters
4. train adapters only

## Conceptual QLoRA Setup

```python
from transformers import BitsAndBytesConfig
from peft import prepare_model_for_kbit_training

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto",
)

model = prepare_model_for_kbit_training(model)
model = get_peft_model(model, lora_config)
```

## Important Training Knobs

For interviews, know these:

- learning rate
- batch size
- gradient accumulation
- number of epochs
- max sequence length
- LoRA rank
- target modules

Strong answer:

> For LoRA I usually tune learning rate, epochs, LoRA rank, and target modules first, while keeping the dataset and formatting under close review.

## Common Workflow Mistakes

### 1. Bad dataset formatting

If the model sees inconsistent prompt structure, output behavior often becomes inconsistent too.

### 2. No validation set

You end up tuning blindly.

### 3. Wrong target modules

LoRA attaches, but gains are weak.

### 4. Training on synthetic junk

Adapter learns artifacts instead of useful task behavior.

### 5. No strong baseline

You cannot prove LoRA actually helped.

## Real-World Example: Support Classifier

Use LoRA when:

- you need consistent structured labels
- prompt-only solution is brittle
- cost of full fine-tuning is not justified

Possible output:

```json
{"label": "billing", "priority": "high"}
```

This is a realistic backend-friendly use case.

## Real-World Example: Domain Summarization

Use LoRA when:

- model needs finance/legal/healthcare style adaptation
- outputs must be concise and domain-appropriate

But still use retrieval for dynamic facts if needed.

## MANG-Level Interview Insight

If asked "How would you actually implement LoRA fine-tuning?" a strong answer is:

> I would start with a strong base model and a clean instruction-style dataset, format the samples consistently, attach LoRA adapters with PEFT, train only the adapter parameters, validate against a held-out set, and save the adapter separately from the base model. If memory were tight, I would switch to QLoRA by loading the base model in 4-bit and training adapters on top.

## Summary

The practical LoRA workflow is:

- prepare clean data
- attach adapters
- train only adapters
- evaluate honestly
- save adapters separately
- serve base model + adapter together
