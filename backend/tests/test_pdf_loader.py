
import pytest
from pathlib import Path
from app.pdf_loader import cleanup_keep_newlines, extract_pdf_pages

def test_cleanup_keep_newlines():
    s = "Hello\r\n\n\nWorld   \n  Again"
    out = cleanup_keep_newlines(s)
    assert "Hello" in out and "World" in out
    assert "\r" not in out
    assert "\n\n\n" not in out

def test_extract_pdf_pages_file_not_found(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        extract_pdf_pages(str(tmp_path / "missing.pdf"))

def test_extract_pdf_pages_blank_pdf(tmp_path: Path):
    from pypdf import PdfWriter
    p = tmp_path / "blank.pdf"
    w = PdfWriter()
    w.add_blank_page(width=200, height=200)
    with p.open("wb") as f:
        w.write(f)
    pages = extract_pdf_pages(str(p), progress_interval=1)
    assert isinstance(pages, list)
    assert len(pages) == 0
