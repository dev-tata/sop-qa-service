from __future__ import annotations
from fastapi import FastAPI, HTTPException
from .config import load_config, AppConfig
from .schemas import BuildRequest, SearchRequest, QARequest
from .pipeline import QAPipeline
from .logging_utils import get_logger

logger = get_logger(__name__)
app = FastAPI(title="PDF FAISS API Service", version="1.0.0")

CFG: AppConfig = load_config(None)
PIPE = QAPipeline(CFG)

@app.get("/health")
def health():
    return {"status": "ok", "ready": PIPE.ready(), "index_dir": CFG.index_dir}

@app.post("/build")
def build(req: BuildRequest):
    try:
        PIPE.build(req.pdf_path, persist=req.persist)
        return {"status": "built", "chunks": len(PIPE.chunks), "index_dir": CFG.index_dir}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/load")
def load():
    try:
        PIPE.load()
        return {"status": "loaded", "chunks": len(PIPE.chunks), "index_dir": CFG.index_dir}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/search")
def search(req: SearchRequest):
    try:
        hits = PIPE.search(req.query, keywords=req.keywords, top_k=req.top_k, pool_k=req.pool_k)
        return [{
            "score": score,
            "chunk_id": ch["chunk_id"],
            "section_title": ch["section_title"],
            "page_start": ch["page_start"],
            "page_end": ch["page_end"],
            "keywords": ch.get("keywords", [])[:12],
        } for score, ch in hits]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/qa")
def qa(req: QARequest):
    try:
        return PIPE.answer_extractive(req.question, top_k=req.top_k)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/chunks/{chunk_id}")
def get_chunk(chunk_id: str):
    if not PIPE.ready():
        raise HTTPException(status_code=400, detail="Pipeline not ready. Build or load first.")
    for ch in PIPE.chunks:
        if ch["chunk_id"] == chunk_id:
            return ch
    raise HTTPException(status_code=404, detail="Chunk not found")
