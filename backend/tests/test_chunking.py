
from app.chunking import chunk_pages

def test_chunk_pages_with_headings():
    pages = [{
        "page": 1,
        "source_file": "x.pdf",
        "text": "1 PURPOSE\nThis is the purpose.\n\n2 SCOPE\nThis is the scope."
    }]
    chunks = chunk_pages(pages)
    titles = [c["section_title"] for c in chunks]
    assert any("PURPOSE" in t for t in titles)
    assert any("SCOPE" in t for t in titles)
    assert all("chunk_id" in c for c in chunks)

def test_chunk_pages_full_page_fallback():
    pages = [{"page": 1, "source_file": "x.pdf", "text": "No headings here, just text."}]
    chunks = chunk_pages(pages)
    assert len(chunks) == 1
    assert chunks[0]["section_title"] == "FULL_PAGE"
