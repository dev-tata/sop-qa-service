
import numpy as np
import pytest
faiss = pytest.importorskip("faiss")

from app.config import AppConfig
from app.pipeline import QAPipeline

def test_pipeline_build_with_mocks(tmp_path, monkeypatch, dummy_model):
    cfg = AppConfig(pdf_path="x.pdf", index_dir=str(tmp_path))

    monkeypatch.setattr("app.pipeline.extract_pdf_pages", lambda *a, **k: [
        {"page": 1, "source_file": "x.pdf", "text": "1 PURPOSE\nHello world"}
    ])
    monkeypatch.setattr("app.pipeline.chunk_pages", lambda pages: [
        {"page_start":1,"page_end":1,"section_id":"1","section_title":"1 PURPOSE","text":"Hello world","source_file":"x.pdf","chunk_id":"abc"}
    ])
    monkeypatch.setattr("app.pipeline.build_keyword_index", lambda chunks: (chunks, {"hello":["abc"]}))
    monkeypatch.setattr("app.pipeline.get_model", lambda name: dummy_model)
    monkeypatch.setattr("app.pipeline.embed_texts", lambda texts, model, batch_size=32: np.eye(8, dtype="float32")[:len(texts)])

    pipe = QAPipeline(cfg)
    pipe.build(pdf_path="x.pdf", persist=True)
    assert pipe.ready()
    results = pipe.search("hello", top_k=1, pool_k=5)
    assert len(results) == 1
