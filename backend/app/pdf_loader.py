from __future__ import annotations
from pathlib import Path
from pypdf import PdfReader
import re
import time
from .logging_utils import get_logger

logger = get_logger(__name__)

def cleanup_keep_newlines(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()

def extract_pdf_pages(pdf_path: str, progress_interval: int = 10) -> list[dict]:
    p = Path(pdf_path)
    if not p.exists():
        raise FileNotFoundError(f"PDF not found: {p}")
    safe_name = p.name.replace(" ", "_")
    logger.info(f"Opening PDF: {p.name}")
    t0 = time.time()
    reader = PdfReader(str(p))
    num_pages = len(reader.pages)
    logger.info(f"Total pages: {num_pages}")

    pages: list[dict] = []
    empty_pages = 0
    error_pages: list[tuple[int,str]] = []
    step = max(1, num_pages // max(1, progress_interval))

    for i, page in enumerate(reader.pages, start=1):
        if i == 1 or i % step == 0 or i == num_pages:
            logger.info(f"  Page {i}/{num_pages}...")
        try:
            text = page.extract_text() or ""
            text = cleanup_keep_newlines(text)
            if text:
                pages.append({"page": i, "text": text, "source_file": safe_name})
            else:
                empty_pages += 1
        except Exception as e:
            error_pages.append((i, str(e)))

    elapsed = time.time() - t0
    empty_ratio = empty_pages / num_pages if num_pages else 0.0
    logger.info(f"Extraction complete ({elapsed:.2f}s)")
    logger.info(f"  Non-empty pages: {len(pages)}")
    logger.info(f"  Empty pages: {empty_pages} ({empty_ratio*100:.1f}%)")
    if error_pages:
        logger.warning(f"  Extraction errors on pages: {[p for p,_ in error_pages]}")
    if empty_ratio > 0.3:
        logger.warning("  High empty page ratio - likely scanned/image PDF")
    return pages
