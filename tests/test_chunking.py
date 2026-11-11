from app.knowledge import chunk_text


def test_empty_text_returns_no_chunks():
    assert chunk_text("   ") == []


def test_short_text_is_one_chunk():
    assert chunk_text("hello support team") == ["hello support team"]


def test_long_text_is_split_and_preserves_content():
    text = "word " * 500
    chunks = chunk_text(text, chunk_size=200, overlap=30)
    assert len(chunks) > 1
    assert all(chunks)
    assert all(len(chunk) <= 200 for chunk in chunks)
