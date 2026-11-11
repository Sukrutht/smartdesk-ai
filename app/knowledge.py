from pathlib import Path
import chromadb
from pypdf import PdfReader
from app.config import settings
from app.ai import embed_text

_client = None
_collection = None


def collection():
    global _client, _collection
    if _collection is None:
        Path(settings.chroma_path).mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=settings.chroma_path)
        _collection = _client.get_or_create_collection(name="support_knowledge", metadata={"hnsw:space": "cosine"})
    return _collection


def extract_pdf_pages(file_path: str) -> list[tuple[int, str]]:
    reader = PdfReader(file_path)
    pages = []
    for page_no, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append((page_no, text))
    return pages


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 120) -> list[str]:
    text = " ".join(text.split())
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            boundary = text.rfind(" ", start, end)
            if boundary > start + chunk_size // 2:
                end = boundary
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


async def index_pdf(file_path: str, filename: str) -> int:
    col = collection()
    ids, docs, metas, vectors = [], [], [], []
    for page_no, page_text in extract_pdf_pages(file_path):
        for chunk_no, chunk in enumerate(chunk_text(page_text)):
            ids.append(f"{filename}:{page_no}:{chunk_no}")
            docs.append(chunk)
            metas.append({"document": filename, "page": page_no})
            vectors.append(await embed_text(chunk, "RETRIEVAL_DOCUMENT"))
    if not docs:
        raise ValueError("No extractable text found. Scanned/image-only PDFs are not supported in this version.")
    existing = col.get(where={"document": filename})
    if existing.get("ids"):
        col.delete(ids=existing["ids"])
    col.add(ids=ids, documents=docs, metadatas=metas, embeddings=vectors)
    return len(docs)


async def retrieve(question: str, top_k: int = 4) -> list[dict]:
    col = collection()
    if col.count() == 0:
        return []
    vector = await embed_text(question, "RETRIEVAL_QUERY")
    result = col.query(query_embeddings=[vector], n_results=min(top_k, col.count()), include=["documents", "metadatas", "distances"])
    matches = []
    for doc, meta, distance in zip(result["documents"][0], result["metadatas"][0], result["distances"][0]):
        matches.append({"text": doc, "document": meta["document"], "page": meta["page"], "distance": float(distance)})
    return matches
