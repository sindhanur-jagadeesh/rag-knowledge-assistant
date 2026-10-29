
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from backend.config import TOP_K
from backend.generator import generate_answer
from backend.ingestor import ingest_pdf
from backend.retriever import Retriever

app = FastAPI(
    title="RAG Legal Compliance API",
    description="Semantic search and context-grounded answers for legal documents.",
    version="1.0.0",
)

retriever = Retriever()


class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=TOP_K, ge=1, le=10)


class IngestRequest(BaseModel):
    pdf_path: str = Field(min_length=1)


@app.get("/")
def root():
    return {
        "name": "RAG Legal Compliance API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "chunks": retriever.count(),
    }


@app.get("/stats")
def stats():
    return {
        "total_chunks": retriever.count(),
        "collection": "legal_documents",
    }


@app.post("/query")
def query(req: QueryRequest):
    question = req.query.strip()
    if not question:
        raise HTTPException(status_code=422, detail="Query cannot be empty.")

    chunks = retriever.query(question, req.top_k)
    if not chunks:
        raise HTTPException(
            status_code=404,
            detail="No indexed documents found. Ingest a PDF first.",
        )

    try:
        result = generate_answer(question, chunks)
        result["retrieved_chunks"] = chunks
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Answer generation failed. Check the server configuration "
                "and logs."
            ),
        ) from exc


@app.post("/ingest")
def ingest(req: IngestRequest):
    raw_dir = Path(__file__).resolve().parent.parent / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    supplied_path = Path(req.pdf_path)
    if not supplied_path.is_absolute():
        supplied_path = Path.cwd() / supplied_path

    pdf_path = supplied_path.resolve()

    try:
        pdf_path.relative_to(raw_dir.resolve())
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="PDF must be located inside the project's data/raw directory.",
        ) from exc

    if not pdf_path.is_file() or pdf_path.suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="A valid PDF file inside data/raw is required.",
        )

    try:
        chunks = ingest_pdf(str(pdf_path))
        retriever.add_chunks(chunks)
        return {
            "status": "success",
            "chunks_added": len(chunks),
            "total_chunks": retriever.count(),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Document ingestion failed. Check the server logs.",
        ) from exc
