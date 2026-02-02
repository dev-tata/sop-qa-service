from __future__ import annotations
import numpy as np
from sentence_transformers import SentenceTransformer
from .logging_utils import get_logger

logger = get_logger(__name__)
_model: SentenceTransformer | None = None

def get_model(model_name: str) -> SentenceTransformer:
    global _model
    if _model is None or _model.get_sentence_embedding_dimension() is None:
        logger.info(f"Loading embedding model: {model_name}...")
        # TODO: Replace SentenceTransformer with OpenAI embeddings when switching providers.
        _model = SentenceTransformer(model_name)
    return _model

def embed_texts(texts: list[str], model: SentenceTransformer, batch_size: int = 32) -> np.ndarray:
    # TODO: Update this to call OpenAI embeddings (and handle rate limits) in the future.
    emb = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        normalize_embeddings=True
    )
    return np.asarray(emb, dtype="float32")
