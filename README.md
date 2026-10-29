# RAG Legal Compliance Assistant

A Retrieval-Augmented Generation (RAG) application for exploring Indian company-law and business-compliance documents using semantic search and context-grounded AI responses.

## Overview

The RAG Legal Compliance Assistant retrieves relevant passages from indexed documents and uses a large language model to generate answers grounded in the retrieved context.

The project combines a FastAPI backend, a persistent ChromaDB vector store, FastEmbed embeddings, Groq-powered answer generation, and a Streamlit interface.

## Features

- **Semantic retrieval:** Find relevant passages using vector embeddings.
- **Document ingestion:** Extract text from PDF files and split it into manageable chunks.
- **Persistent vector storage:** Store and retrieve document embeddings with ChromaDB.
- **AI-generated responses:** Generate context-grounded answers through the Groq API.
- **Interactive interface:** Ask questions and inspect retrieved passages through Streamlit.
- **REST API:** Access health, statistics, ingestion, and question-answering endpoints.

## Technology Stack

- Python
- FastAPI and Uvicorn
- Streamlit
- ChromaDB
- FastEmbed
- Groq API
- PyPDF2
- HTTPX

## Architecture

```text
User
 |
 v
Streamlit Frontend
 |
 v
FastAPI Backend
 |
 +--> FastEmbed
 |
 +--> ChromaDB Vector Store
 |
 +--> Groq LLM API
 |
 v
Answer + Source Labels + Retrieved Passages
```

## Project Structure

```text
rag-knowledge-assistant/
├── backend/
│   ├── hierarchical/
│   ├── config.py
│   ├── embedder.py
│   ├── generator.py
│   ├── ingestor.py
│   ├── main.py
│   └── retriever.py
├── frontend/
│   └── app.py
├── scripts/
├── data/
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.11
- A Groq API key
- Git

## Local Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd rag-knowledge-assistant
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```dotenv
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
EMBED_MODEL=BAAI/bge-small-en-v1.5
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

Never commit `.env` or publish API keys.

### 5. Add a document

Place a PDF you are authorized to process inside `data/raw/`.

The local ingestion endpoint accepts a path to a PDF within that directory. For example, use the following request in the API documentation:

```json
{
  "pdf_path": "data/raw/your-document.pdf"
}
```

### 6. Start the backend

From the project root:

```powershell
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

API documentation: http://127.0.0.1:8000/docs

Health check: http://127.0.0.1:8000/health

Statistics: http://127.0.0.1:8000/stats

### 7. Start the frontend

Open a second terminal, activate the same virtual environment, and run:

```powershell
python -m streamlit run frontend/app.py
```

Open the local URL displayed by Streamlit, typically http://localhost:8501.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API information |
| GET | `/health` | Health status and indexed chunk count |
| GET | `/stats` | Vector collection statistics |
| POST | `/ingest` | Ingest a local PDF |
| POST | `/query` | Retrieve passages and generate an answer |

## Configuration

| Variable | Purpose |
|---|---|
| `GROQ_API_KEY` | API key used for answer generation |
| `GROQ_MODEL` | Groq model identifier |
| `EMBED_MODEL` | Text embedding model |
| `CHUNK_SIZE` | Maximum characters per chunk |
| `CHUNK_OVERLAP` | Overlap between adjacent chunks |
| `CHROMA_PATH` | Optional persistent ChromaDB directory |

## Limitations and Responsible Use

- Generated answers can be incomplete or inaccurate. Verify important statements against the underlying legislation and authoritative sources.
- The application is intended for research and general information, not as a substitute for professional legal advice.
- Source attribution currently uses document-level labels; precise Act, section, and page citations require suitable source metadata.
- Only use documents that you are legally permitted to process and redistribute.
- Keep credentials and private documents out of public repositories.

## License

Add a license only after confirming that you have the rights to distribute this project and its included materials. Third-party documents may have separate licensing terms.