from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import yaml

@dataclass
class AppConfig:
    pdf_path: str = "data/pdfs/document.pdf"
    model_name: str = "all-MiniLM-L6-v2"
    embedding_batch_size: int = 32
    top_k_search: int = 5
    pool_k_search: int = 25
    progress_interval: int = 10
    index_dir: str = "data/index"

def load_config(path: str | None) -> AppConfig:
    if not path:
        return AppConfig()
    p = Path(path)
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    cfg = AppConfig(**{k: v for k, v in data.items() if hasattr(AppConfig, k)})
    return cfg
