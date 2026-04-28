# Data Preparation and Training Setup

## Why Data Matters So Much

In fine-tuning, data quality often matters more than fancy training tricks.

Bad dataset:

- noisy labels
- inconsistent formatting
- duplicated examples
- narrow coverage

Result:

- weak generalization
- unstable training
- misleading evaluation

## Build the Right Dataset

A strong fine-tuning dataset should be:

- representative
- clean
- balanced enough for the task
- aligned with production inputs
- consistent in output style

## Dataset Types

### Classification datasets

```text
text -> label
```

### Seq2seq or generation datasets

```text
input -> target output
```

### Instruction-tuning datasets

```text
instruction + input -> response
```

### Preference datasets

```text
prompt + preferred response + rejected response
```

## Data Sources

Common sources:

- historical tickets
- manually annotated examples
- human-written gold outputs
- cleaned logs
- curated domain documents

Be careful with:

- PII
- copyrighted data
- weak labels
- generated synthetic data with no review

## Splits: Train / Validation / Test

This is basic but very important.

### Train set

Used to update model weights.

### Validation set

Used to tune hyperparameters and detect overfitting.

### Test set

Used only for final evaluation.

Strong interview point:

Do not repeatedly tune against the test set.

## Leakage

Data leakage is a common failure.

Examples:

- same user conversation appears in train and test
- near-duplicate samples across splits
- future data leaks into past predictions

Result:

- inflated evaluation
- weak real-world performance

## Formatting for LLM Fine-Tuning

Instruction-tuning examples are often formatted like:

```json
{
  "messages": [
    {"role": "system", "content": "You are a support classifier."},
    {"role": "user", "content": "Customer was charged twice."},
    {"role": "assistant", "content": "{\"label\": \"billing\"}"}
  ]
}
```

Consistency matters:

- same prompt style
- same output schema
- same policy wording

## Tokenization

Models do not see raw text directly. They see tokens.

Important consequences:

- longer text increases cost
- truncation may hide critical context
- token distribution affects training dynamics

## Sequence Length

You need to decide:

- max input length
- max output length
- truncation policy

Bad choices can:

- remove essential context
- waste memory
- make training unstable

## Example with Hugging Face Datasets and Tokenizer

```python
from datasets import Dataset
from transformers import AutoTokenizer

data = Dataset.from_list([
    {"input": "Classify: Customer was charged twice", "target": "billing"},
    {"input": "Classify: Package is delayed", "target": "shipping"},
])

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

def tokenize(batch):
    return tokenizer(batch["input"], truncation=True, padding="max_length", max_length=64)

tokenized = data.map(tokenize)
print(tokenized[0])
```

## Class Imbalance

Suppose 90% of tickets are "billing" and only 2% are "fraud."

If untreated:

- model may appear accurate
- minority classes perform badly

Mitigations:

- better sampling
- class weighting
- targeted data collection
- per-class metrics

## Data Cleaning Checklist

- remove duplicates
- fix broken labels
- standardize output format
- filter toxic or irrelevant samples
- audit class balance
- remove sensitive data where needed

## Hyperparameters You Should Know

For interviews, know at least:

- learning rate
- batch size
- number of epochs
- weight decay
- warmup steps
- max sequence length

Strong answer:

> I tune learning rate and epochs carefully because aggressive fine-tuning can overfit quickly, especially on small domain-specific datasets.

## Example Training Setup with Transformers Trainer

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import TrainingArguments, Trainer

model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)

training_args = TrainingArguments(
    output_dir="./results",
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    learning_rate=2e-5,
    num_train_epochs=3,
    evaluation_strategy="epoch",
    save_strategy="epoch",
)
```

## Real-World Problems

### Problem: model performs well offline, poorly in production

Cause:

- training data not representative

### Problem: model learns one annotation style, fails on another team’s data

Cause:

- inconsistent labeling standards

### Problem: model output format is unreliable

Cause:

- target outputs inconsistent during training

## MANG-Level Interview Insight

If asked "What matters most in fine-tuning?" a strong answer is:

> The most important thing is usually data quality and task alignment. If the dataset is noisy, inconsistent, or unrepresentative, better training tricks will not rescue the model. I would first make sure the training examples reflect the real production distribution and the exact output behavior I care about.

## Summary

Fine-tuning success starts with:

- clean data
- correct splits
- thoughtful formatting
- realistic evaluation setup
