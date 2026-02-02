from __future__ import annotations
import numpy as np
from .config import AppConfig
from .logging_utils import get_logger
from .pdf_loader import extract_pdf_pages
from .chunking import chunk_pages
from .keywords import build_keyword_index
from .embeddings import get_model, embed_texts
from .faiss_store import build_index, save_artifacts, load_artifacts

logger = get_logger(__name__)

class QAPipeline:
    def __init__(self, cfg: AppConfig):
        self.cfg = cfg
        # TODO: Replace with OpenAI embedding client when switching providers.
        self.model = get_model(cfg.model_name)
        self.index = None
        self.chunks: list[dict] = []
        self.keyword_to_chunks: dict[str, list[str]] = {}

    def build(self, pdf_path: str | None = None, persist: bool = True):
        pdf_path = pdf_path or self.cfg.pdf_path
        pages = extract_pdf_pages(pdf_path, progress_interval=self.cfg.progress_interval)
        chunks = chunk_pages(pages)
        chunks, kw_to_chunks = build_keyword_index(chunks)
        texts = [c["section_title"] + "\n" + c["text"] for c in chunks]
        emb = embed_texts(texts, self.model, batch_size=self.cfg.embedding_batch_size)
        index = build_index(emb)

        self.index = index
        self.chunks = chunks
        self.keyword_to_chunks = kw_to_chunks

        if persist:
            save_artifacts(self.cfg.index_dir, index, chunks, kw_to_chunks)

    def load(self):
        index, chunks, kw_to_chunks = load_artifacts(self.cfg.index_dir)
        self.index = index
        self.chunks = chunks
        self.keyword_to_chunks = kw_to_chunks

    def ready(self) -> bool:
        return self.index is not None and bool(self.chunks)
    
    def get_chunk(self, chunk_id: str) -> dict | None:
        """Return the full chunk dict by chunk_id, or None if not found."""
        if not self.ready():
            raise RuntimeError("Pipeline not ready. Call build() or load() first.")
        for ch in self.chunks:
            if ch.get("chunk_id") == chunk_id:
                return ch
        return None

    def search(self, query: str, keywords: list[str] | None = None, top_k: int | None = None, pool_k: int | None = None):
        if not self.ready():
            raise RuntimeError("Pipeline not ready. Call build() or load() first.")
        top_k = top_k or self.cfg.top_k_search
        pool_k = pool_k or self.cfg.pool_k_search
        pool_k = max(pool_k, top_k)
        keywords = [k.lower() for k in (keywords or [])]

        candidate_ids = None
        if keywords:
            sets = [set(self.keyword_to_chunks.get(kw, [])) for kw in keywords]
            candidate_ids = set.intersection(*sets) if sets else None
            if candidate_ids is not None and not candidate_ids:
                logger.warning(f"No chunks contain all keywords: {keywords}")

        q_emb = self.model.encode([query], normalize_embeddings=True)
        q_emb = np.asarray(q_emb, dtype="float32")
        scores, ids = self.index.search(q_emb, pool_k)
        scores, ids = scores[0], ids[0]

        results = []
        for score, idx in zip(scores, ids):
            if idx < 0 or idx >= len(self.chunks):
                continue
            ch = self.chunks[int(idx)]
            if candidate_ids is not None and ch["chunk_id"] not in candidate_ids:
                continue
            results.append((float(score), ch))
            if len(results) >= top_k:
                break
        return results

    def answer_extractive(self, question: str, top_k: int = 5) -> dict:
        hits = self.search(question, top_k=top_k)
        contexts = []
        for score, ch in hits:
            excerpt = ch["text"].split("\n\n")[0].strip()
            contexts.append({
                "score": score,
                "chunk_id": ch["chunk_id"],
                "section_title": ch["section_title"],
                "page_start": ch["page_start"],
                "page_end": ch["page_end"],
                "excerpt": excerpt[:800],
            })
        return {"question": question, "contexts": contexts}
