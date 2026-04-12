from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Root
ROOT_DIR = Path(__file__).parent

# Data paths
RAW_PDF = ROOT_DIR / "data" / "raw" / "aspice.pdf"
EXTRACTED_JSON = ROOT_DIR / "data" / "extracted" / "aspice_tables.json"
CHUNKS_JSON = ROOT_DIR / "data" / "chunked" / "Ch4_chunks.json"
CH3_CHUNKS_JSON = ROOT_DIR / "data" / "chunked" / "Ch3_chunks.json"
CH5_CHUNKS_JSON = ROOT_DIR / "data" / "chunked" / "Ch5_chunks.json"
ALL_CHUNKS_JSON = ROOT_DIR / "data" / "chunked" / "aspice_all_chunks.json"
EMBEDDINGS_JSON = ROOT_DIR / "data" / "processed" / "aspice_embeddings.json"
VECTORSTORE_DIR = str(ROOT_DIR / "data" / "vectorstore")
OUTPUT_DIR = ROOT_DIR / "data" / "processed"

# Embedding
EMBEDDING_MODEL = "nomic-ai/nomic-embed-text-v1.5"
EMBEDDING_PREFIX_DOC = "search_document: "
EMBEDDING_PREFIX_QUERY = "search_query: "

# Vectorstore
COLLECTION_NAME = "aspice_processes"

# Retrieval
BM25_WEIGHT = 0.5
DENSE_WEIGHT = 0.5
RRF_K = 60
TOP_K = 10

# Reranking
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
RERANKER_TOP_N = 5

# Generation
GROQ_MODEL = 'llama-3.3-70b-versatile'