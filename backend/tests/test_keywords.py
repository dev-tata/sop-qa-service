
from app.keywords import extract_keywords, build_keyword_index

def test_extract_keywords_basic():
    text = "Decommission software and preserve documentation. Decommissioning requires documentation."
    kws = extract_keywords(text, top_k=5)
    assert isinstance(kws, list)
    assert len(kws) > 0

def test_build_keyword_index():
    chunks = [
        {"chunk_id":"a", "section_title":"1 PURPOSE", "text":"quality system integrity", "page_start":1,"page_end":1,"source_file":"x.pdf"},
        {"chunk_id":"b", "section_title":"4.8 DECOMMISSION SOFTWARE", "text":"decommissioning documentation archive", "page_start":5,"page_end":5,"source_file":"x.pdf"},
    ]
    chunks2, inv = build_keyword_index(chunks, per_chunk_k=5)
    assert len(chunks2) == 2
    assert isinstance(inv, dict)
