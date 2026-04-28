# Multimodal Systems

## Core Idea

Multimodal systems process more than one data type.

Examples:

- text + image
- text + audio
- text + video
- document images + OCR + text

The goal is to map different input types into representations a model can reason over.

## Vision-Language Mental Model

A common architecture:

```text
Image
  |
  v
Vision encoder
  |
  v
Projected visual tokens
  |
  v
Language model
  |
  v
Text answer
```

The vision encoder converts image patches into embeddings. A projection layer maps those embeddings into the language model's token space.

## CLIP, ViT, and LLaVA

### ViT

Vision Transformer splits an image into patches and processes them like tokens.

### CLIP

CLIP learns aligned image and text embeddings so matching images and captions are close in embedding space.

### LLaVA

LLaVA-style models connect a vision encoder to an LLM so the language model can answer about images.

Strong interview answer:

```text
A vision-language model does not literally read pixels as words. It encodes the image into visual embeddings and projects them into a representation the language model can consume.
```

## Early Fusion vs Late Fusion

### Early Fusion

Combine modalities before or inside the model.

Useful when:

- reasoning depends on joint understanding
- image details and text interact deeply

### Late Fusion

Process modalities separately, then combine results.

Useful when:

- OCR or object detection can extract enough structure
- system needs modularity
- cheaper models can solve parts independently

Example late-fusion pipeline:

```text
image -> OCR -> extracted text
image -> object detector -> objects
text + objects -> LLM reasoning
```

## OCR vs Vision-Language Model

Use OCR when:

- document text is the main signal
- exact text matters
- you need searchable extracted content

Use VLM when:

- layout matters
- charts, diagrams, or visual relationships matter
- image understanding goes beyond text extraction

Often the best production system uses both.

## Audio Systems

Audio is often handled as:

```text
audio -> speech recognition -> text -> LLM
```

For deeper audio tasks, models may use acoustic tokens or audio embeddings.

Examples:

- transcription
- call summarization
- meeting analysis
- voice agents

Production issues:

- speaker diarization
- background noise
- latency
- accents
- personally identifiable information

## Multimodal RAG

Multimodal RAG retrieves evidence across modalities.

Examples:

- retrieve image by text query
- retrieve document page screenshot
- retrieve chart plus extracted table
- retrieve transcript segment plus audio timestamp

Design pattern:

```text
store raw asset + extracted text + embeddings + metadata
```

This lets the system ground answers and show evidence.

## Coding Example: Simple Multimodal Document Record

```python
from dataclasses import dataclass


@dataclass
class MultimodalDocument:
    document_id: str
    page_number: int
    ocr_text: str
    image_uri: str
    text_embedding: list[float]
    image_embedding: list[float]
    permissions: list[str]
```

In production, store embeddings in a vector index and store assets in object storage.

## Production Design Checklist

- preserve source asset links
- store extracted text separately
- store modality-specific embeddings
- keep page, timestamp, and bounding-box metadata
- apply access control before retrieval
- evaluate per modality
- handle large files asynchronously
- monitor extraction failure rate

## Common Failure Modes

- OCR misses text
- chart interpretation is wrong
- image crop removes important context
- model invents visual details
- cross-modal retrieval returns visually similar but semantically wrong assets
- permissions are applied to text but not images
- latency explodes for large PDFs or videos

## Cross Questions

### Why not convert everything to text?

Text extraction loses layout, visual relationships, diagrams, handwriting, colors, and spatial structure. It is useful but not always sufficient.

### Why not send every image page to the model?

It is expensive and slow. It can also add noise. Retrieval, OCR, page ranking, and selective image reasoning are usually better.

### How would you evaluate a multimodal QA system?

Measure answer correctness, evidence relevance, OCR accuracy, chart/table accuracy, citation quality, latency, and modality-specific failure cases.

### What is the biggest security risk?

Applying permissions inconsistently across extracted text, image assets, thumbnails, transcripts, and metadata.

