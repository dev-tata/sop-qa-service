
import numpy as np
import pytest
faiss = pytest.importorskip("faiss")

from app.faiss_store import build_index, save_artifacts, load_artifacts

def test_build_save_load_artifacts(tmp_path):
    emb = np.eye(4, dtype="float32")
    index = build_index(emb)
    chunks = [{"chunk_id":"c1","section_title":"t","text":"x","page_start":1,"page_end":1,"source_file":"x.pdf"}]
    kw = {"x":["c1"]}
    save_artifacts(str(tmp_path), index, chunks, kw)
    idx2, chunks2, kw2 = load_artifacts(str(tmp_path))
    assert idx2.ntotal == 4
    assert chunks2[0]["chunk_id"] == "c1"
    assert "x" in kw2
