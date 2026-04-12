import json
from config import EMBEDDINGS_JSON
from src.retrieval.vectorstore import ingest

def ingest_vectorstore():
    with open(EMBEDDINGS_JSON, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    ingest(chunks)