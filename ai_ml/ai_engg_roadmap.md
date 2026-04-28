# Machine Learning / AI Complete Roadmap

---

## 1. Mathematics Foundations

### Linear Algebra
- Vectors & matrices  
- Eigenvalues & eigenvectors  
- Singular Value Decomposition (SVD)  
- Principal Component Analysis (PCA)  
- Matrix decompositions  

### Calculus
- Partial derivatives  
- Chain rule  
- Gradient descent mechanics  
- Jacobians & Hessians  

### Probability & Statistics
- Probability distributions  
- Maximum Likelihood Estimation (MLE)  
- Maximum A Posteriori (MAP)  
- Hypothesis testing  
- Confidence intervals  

### Bayesian Inference
- Bayes' theorem  
- Priors & posteriors  
- Markov Chain Monte Carlo (MCMC)  
- Variational inference  

### Information Theory
- Entropy  
- KL divergence  
- Cross-entropy loss  
- Mutual information  

### Numerical Methods
- Floating point precision  
- Numerical stability  
- Optimization landscapes  

### Python Libraries
- NumPy  
- Pandas  
- Matplotlib  

---

## 2. Core Machine Learning Algorithms

### Supervised Learning
- Linear regression  
- Logistic regression  
- Support Vector Machines (SVM)  
- Decision trees  
- K-Nearest Neighbors (KNN)  
- Naive Bayes  

### Unsupervised Learning
- K-Means  
- DBSCAN  
- Hierarchical clustering  
- Gaussian Mixture Models (GMMs)  
- Independent Component Analysis (ICA)  
- Autoencoders  

### Ensemble Methods
- Random forests  
- Gradient boosting (XGBoost, LightGBM, CatBoost)  
- Bagging & stacking  
- AdaBoost  

### Reinforcement Learning
- Markov Decision Processes (MDPs)  
- Q-learning  
- Policy gradients  
- Proximal Policy Optimization (PPO)  
- Actor-Critic methods  

### Neural Network Basics
- CNNs / RNNs / LSTMs  
- Transformers  
- Graph Neural Networks (GNNs)  
- Diffusion models  

### Core Concepts
- Loss functions  
- Regularization (L1, L2, dropout)  
- Evaluation metrics (accuracy, precision, recall, F1, ROC-AUC)  

---

## 3. Deep Learning

### Fundamentals
- Backpropagation (from scratch)  
- Activation functions  
- Weight initialization strategies  
- Batch normalization / Layer normalization  

### Convolutional Neural Networks (CNNs)
- Convolution & pooling  
- Feature maps  
- Architectures: ResNet, EfficientNet  
- Transfer learning  

### Sequence Models
- RNNs / LSTMs / GRUs  
- Vanishing & exploding gradients  
- Sequence modeling  
- Bidirectional RNNs  

### Transformers
- Self-attention (from scratch)  
- Multi-head attention  
- Positional encoding (RoPE, ALiBi)  
- Architectures: BERT, GPT, T5  

### Diffusion Models
- Forward & reverse diffusion  
- DDPM / DDIM  
- Score matching  
- Classifier-free guidance  

### Graph Neural Networks
- Message passing  
- GCN / GAT / GraphSAGE  
- Graph-level tasks  

### Tools
- PyTorch  
- Scikit-learn  
- Hugging Face (Transformers, Datasets, PEFT)  
- ONNX Runtime  

---

## 4. LLM Internals & Advanced Topics

### Quantization
- INT8 / INT4 / FP16 / BF16  
- Post-Training Quantization (PTQ) vs Quantization-Aware Training (QAT)  
- GPTQ / AWQ / GGUF formats  
- Quantization-aware fine-tuning  

### KV Cache & Context Optimization
- KV cache mechanics  
- Sliding window attention  
- Long-context strategies (Ring, chunked attention)  
- PagedAttention (vLLM)  

### Structured Outputs
- Constrained decoding  
- JSON / grammar-constrained generation  
- Tools: Outlines, Guidance, LM-Format-Enforcer  
- Function calling internals  

### Multimodal Models
- Vision encoders (ViT, CLIP)  
- Cross-attention fusion  
- Architectures: LLaVA, Flamingo  
- Audio tokenization (Whisper)  
- Unified token streams  

### Efficient Fine-tuning
- LoRA / QLoRA / DoRA  
- Prefix tuning  
- Adapter layers  

### Alignment & Training
- RLHF  
- DPO  
- PPO  

### Sampling & Decoding
- Temperature  
- Top-k / Top-p  
- Beam search  
- Greedy vs sampling trade-offs  
- Speculative decoding  

### LLM Inference & Generation Track
- See `ai_ml/05_llm_frameworks/llm_inference_and_generation/README.md`  
- Quantization from first principles  
- KV cache, prefill/decode, and context optimization  
- Structured outputs, schemas, function calling, constrained decoding  
- Multimodal systems: OCR, VLMs, audio, multimodal RAG  
- Serving tradeoffs: batching, streaming, routing, observability  

---

## 5. MLOps & Model Lifecycle

### Experiment Tracking
- MLflow (runs, artifacts, registry)  
- Weights & Biases (sweeps, dashboards)  

### Model Serving
- Triton Inference Server  
- BentoML  
- TorchServe  
- FastAPI + ONNX Runtime  

### Feature Stores
- Feast / Tecton  
- Online vs offline store  
- Feature versioning  

### Model Registry & Governance
- Versioning strategies  
- Lineage tracking  
- Approval workflows  

### Monitoring
- Data drift (PSI, KS test)  
- Concept drift  
- Prediction monitoring  
- Alerting  

### CI/CD for ML
- GitHub Actions for retraining  
- DVC for data versioning  
- Canary / shadow deployments  
- A/B testing  

---

## 6. Cloud & Infrastructure

### Managed ML Platforms
- AWS SageMaker  
- Azure ML + Databricks  
- Google Vertex AI  
- Databricks MLflow integration  

### GPU Compute
- A100 / H100 / V100 (use cases & differences)  
- Spot vs reserved instances  
- Multi-GPU topology (NVLink)  

### Distributed Training
- Data parallelism (DDP)  
- Model parallelism  
- Pipeline parallelism  
- FSDP / DeepSpeed ZeRO  

### Orchestration
- Kubernetes (KEDA, resource limits)  
- Kubeflow / Argo Workflows  
- Ray (Train, Tune, Serve)  

### Infrastructure as Code
- Terraform (Azure / AWS)  
- Modular ML cluster configurations  

---

## 7. Software Engineering for ML Systems

### Concurrency & Parallelism
- asyncio & event loop  
- Python multiprocessing  
- ThreadPoolExecutor  
- Async queues  

### Containerization
- Docker multi-stage builds  
- GPU-enabled containers (CUDA)  
- Docker Compose for local development  

### Messaging Systems
- Redis Streams / Pub-Sub  
- AWS SQS / SNS  
- Apache Kafka  

### APIs & Protocols
- REST API design  
- gRPC + Protocol Buffers  
- Streaming responses (SSE)  
- Webhooks  

### System Design for ML
- Batch vs real-time inference  
- Queue-based async ML systems  
- Rate limiting & load shedding  
- Vector database integration  
- RAG pipeline architecture  

### Testing ML Systems
- Unit tests for data transforms & features  
- Pytest fixtures for model testing  
- Golden dataset regression tests  
- Property-based testing (Hypothesis)  

---

## Notes / Missing Areas (Now Covered)
- Quantization ✅ `ai_ml/05_llm_frameworks/llm_inference_and_generation/01_quantization.md`  
- KV cache & context optimization ✅ `ai_ml/05_llm_frameworks/llm_inference_and_generation/02_kv_cache_and_context_optimization.md`  
- Structured outputs ✅ `ai_ml/05_llm_frameworks/llm_inference_and_generation/03_structured_outputs.md`  
- Multimodal systems ✅ `ai_ml/05_llm_frameworks/llm_inference_and_generation/04_multimodal_systems.md`  
- LLM serving, latency, batching, streaming, speculative decoding ✅ `ai_ml/05_llm_frameworks/llm_inference_and_generation/05_serving_latency_and_production_patterns.md`  
- MANG-style cross questions ✅ `ai_ml/05_llm_frameworks/llm_inference_and_generation/06_interview_questions.md`  

---
