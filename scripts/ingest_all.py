import sys, os
sys.path.insert(0, os.path.abspath("."))

from pathlib import Path
from backend.ingestor import ingest_pdf
from backend.retriever import Retriever

retriever = Retriever()
pdf_dir = Path("data/raw")

for pdf_file in pdf_dir.glob("*.pdf"):
    print(f"\n[*] Ingesting: {pdf_file.name}")
    chunks = ingest_pdf(str(pdf_file))
    retriever.add_chunks(chunks)

print(f"\n✅ Total chunks in DB: {retriever.collection.count()}")
