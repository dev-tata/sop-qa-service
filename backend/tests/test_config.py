
from app.config import load_config, AppConfig
from pathlib import Path

def test_load_config_none_defaults():
    cfg = load_config(None)
    assert isinstance(cfg, AppConfig)
    assert cfg.model_name

def test_load_config_from_yaml(tmp_path: Path):
    p = tmp_path / "cfg.yaml"
    p.write_text("pdf_path: data/pdfs/x.pdf\nembedding_batch_size: 7\nunknown_key: 1\n", encoding="utf-8")
    cfg = load_config(str(p))
    assert cfg.pdf_path == "data/pdfs/x.pdf"
    assert cfg.embedding_batch_size == 7
