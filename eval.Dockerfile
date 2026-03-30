FROM python:3.8-slim

# Install git and wget
RUN apt-get update && apt-get install -y --no-install-recommends \
    git build-essential wget && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clone the repo
RUN git clone https://github.com/soni-sarvesh/archehr-qa-2026.git .

# Install Python dependencies
RUN pip install --no-cache-dir -r evaluation/requirements.txt

RUN pip install quickumls

WORKDIR /app/evaluation

# Pre-download NLTK data
RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('punkt_tab')"

# Pre-download spaCy model (required by MEDCON scorer)
RUN python -m spacy download en_core_web_sm

# Pre-download evaluate metric scripts (BLEU, ROUGE, SARI, BERTScore)
RUN python -c "\
import evaluate; \
evaluate.load('bleu'); \
evaluate.load('rouge'); \
evaluate.load('sari'); \
evaluate.load('bertscore'); \
"

# Pre-download BERTScore model (bert-base-uncased)
RUN python -c "\
from transformers import AutoTokenizer, AutoModel; \
AutoTokenizer.from_pretrained('bert-base-uncased'); \
AutoModel.from_pretrained('bert-base-uncased'); \
"

# Pre-download distilbert-base-uncased (default model used by BERTScore scorer)
RUN python -c "\
from transformers import AutoTokenizer, AutoModel; \
AutoTokenizer.from_pretrained('distilbert-base-uncased'); \
AutoModel.from_pretrained('distilbert-base-uncased'); \
"

# Pre-download roberta-base (used by both BERTScore and AlignScore)
RUN python -c "\
from transformers import AutoTokenizer, AutoModel; \
AutoTokenizer.from_pretrained('roberta-base'); \
AutoModel.from_pretrained('roberta-base'); \
"

# Pre-download AlignScore checkpoint (~1.83 GB)
RUN mkdir -p /root/.cache/torch/hub/checkpoints && \
    wget -q --show-progress \
    -O /root/.cache/torch/hub/checkpoints/AlignScore-base.ckpt \
    https://huggingface.co/yzha/AlignScore/resolve/main/AlignScore-base.ckpt

# Warm up BERTScore with all models it may use to populate its internal cache
RUN python -c "\
from bert_score import BERTScorer; \
BERTScorer(model_type='distilbert-base-uncased', lang='en'); \
BERTScorer(model_type='roberta-base', lang='en'); \
"

# Lock down HuggingFace to offline mode — all models are pre-cached above.
# This prevents any runtime network calls to the HF hub.
ENV TRANSFORMERS_OFFLINE=1
ENV HF_HUB_OFFLINE=1

# Default command - show help for scoring script
CMD ["python", "scoring.py", "--help"]
