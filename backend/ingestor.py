import json, re
from pathlib import Path
from PyPDF2 import PdfReader
from backend.config import CHUNK_SIZE, CHUNK_OVERLAP

def extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def chunk_text(text: str, source: str) -> list[dict]:
    text = re.sub(r'\s+', ' ', text).strip()
    chunks, start, idx = [], 0, 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        chunks.append({
            "id": f"{source}_chunk_{idx}",
            "text": chunk,
            "metadata": {"source": source, "chunk_id": idx}
        })
        start += CHUNK_SIZE - CHUNK_OVERLAP
        idx += 1
    return chunks

def ingest_pdf(pdf_path: str, output_dir: str = "data/processed") -> list[dict]:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    text = extract_text_from_pdf(pdf_path)
    source = Path(pdf_path).stem
    chunks = chunk_text(text, source)
    out_path = f"{output_dir}/{source}.json"
    with open(out_path, "w") as f:
        json.dump(chunks, f, indent=2)
    print(f"[ingestor] {len(chunks)} chunks saved to {out_path}")
    return chunks
