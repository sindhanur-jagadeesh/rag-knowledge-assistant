import os
from dotenv import load_dotenv
load_dotenv()

EMBED_MODEL       = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")
GROQ_API_KEY      = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
CHUNK_SIZE        = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP     = int(os.getenv("CHUNK_OVERLAP", 50))
TOP_K = 5
