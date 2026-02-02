
import numpy as np
import pytest
faiss = pytest.importorskip("faiss")

from fastapi.testclient import TestClient
import app.main as mainmod

def test_health_endpoint():
    client = TestClient(mainmod.app)
    r = client.get("/health")
    assert r.status_code == 200
    assert "status" in r.json()

def test_build_and_search_endpoints(monkeypatch, tmp_path, dummy_model):
    mainmod.CFG.index_dir = str(tmp_path)

    monkeypatch.setattr("app.main.PIPE.build", lambda pdf_path, persist=True: None)

    # minimal in-memory index
    mainmod.PIPE.index = faiss.IndexFlatIP(8)
    mainmod.PIPE.index.add(np.eye(8, dtype="float32"))
    mainmod.PIPE.chunks = [{
        "chunk_id": "c0", "section_title": "T", "text": "Hello",
        "page_start": 1, "page_end": 1, "keywords": ["hello"]
    }]
    mainmod.PIPE.keyword_to_chunks = {"hello":["c0"]}
    mainmod.PIPE.model = dummy_model

    client = TestClient(mainmod.app)
    r = client.post("/build", json={"pdf_path":"data/pdfs/x.pdf","persist":False})
    assert r.status_code == 200

    r2 = client.post("/search", json={"query":"hello","keywords":["hello"],"top_k":1,"pool_k":5})
    assert r2.status_code == 200
    assert isinstance(r2.json(), list)


def test_get_chunk_endpoint(monkeypatch, tmp_path):
    mainmod.CFG.index_dir = str(tmp_path)
    # Make pipeline "ready"
    mainmod.PIPE.index = faiss.IndexFlatIP(8)
    mainmod.PIPE.chunks = [{
        "chunk_id": "cid", "section_title": "T", "text": "Hello",
        "page_start": 1, "page_end": 1, "keywords": ["hello"]
    }]
    client = TestClient(mainmod.app)
    r = client.get("/chunks/cid")
    assert r.status_code == 200
    assert r.json()["chunk_id"] == "cid"
