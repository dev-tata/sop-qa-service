from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import faiss
from .logging_utils import get_logger

logger = get_logger(__name__)

def build_index(emb: np.ndarray) -> faiss.Index:
    dim = emb.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(emb)
    logger.info("FAISS index ready")
    logger.info(f"  • Dimension: {dim}")
    logger.info(f"  • Vectors stored: {index.ntotal}")
    return index

def save_artifacts(index_dir: str, index: faiss.Index, chunks: list[dict], kw_to_chunks: dict[str, list[str]]):
    d = Path(index_dir)
    d.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(d / "index.faiss"))
    (d / "chunks.json").write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    (d / "keywords.json").write_text(json.dumps(kw_to_chunks, ensure_ascii=False, indent=2), encoding="utf-8")

def load_artifacts(index_dir: str):
    d = Path(index_dir)
    idx_path = d / "index.faiss"
    if not idx_path.exists():
        raise FileNotFoundError(f"Missing FAISS index at {idx_path}")
    index = faiss.read_index(str(idx_path))
    chunks = json.loads((d / "chunks.json").read_text(encoding="utf-8"))
    kw_to_chunks = json.loads((d / "keywords.json").read_text(encoding="utf-8"))
    return index, chunks, kw_to_chunks
