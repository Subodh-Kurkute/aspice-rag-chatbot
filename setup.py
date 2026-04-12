import json
import sys
from pathlib import Path
from config import ALL_CHUNKS_JSON, EXTRACTED_JSON, VECTORSTORE_DIR, EMBEDDINGS_JSON, RAW_PDF
from src.ingestion.extractor import build_chunks, save_extracted
from src.ingestion.chunker import chunk_processes
from src.ingestion.ch3_chunker import chunk_ch3
from src.ingestion.ch5_chunker import chunk_ch5
from src.ingestion.chunk_unifier import main as unify_chunks
from scripts.generate_embeddings import main as generate_embeddings_script
from scripts.ingest_vectorstore import ingest_vectorstore
from tests.test_ingestion import test_extractor, test_chunker, test_chunk_lengths
from tests.test_embedder import test_model_loads
from tests.test_embeddings import test_embedding_quality
from tests.test_vectorstore import sanity_checks, plot_PCA
RUN_PCA = True

if not RAW_PDF.exists():
    print("Download the pdf file and save it to the specified path. url: https://vda-qmc.de/wp-content/uploads/2023/12/Automotive-SPICE-PAM-v40.pdf")
    print(f"Expected path: {RAW_PDF}")
    print("Expected filename: aspice.pdf")
    print("Exiting setup.")
    sys.exit(1)
else:
    print(f"Found PDF at {RAW_PDF}. Proceeding with setup.")

if (Path(VECTORSTORE_DIR) / "chroma.sqlite3").exists():
    print("Vectorstore already exists. Skipping setup.")
    sys.exit(0)

print("Starting RAG pipeline setup...")
print(40* "=")
print("STEP1: Starting text extraction and chunking...")
print(40* "=")

# Text extraction and chunking
chunks = build_chunks()
save_extracted(chunks)
print(40* "=")
print('Text extracted for chapter 4 and saved to JSON.')
print(40* "=")
with open(EXTRACTED_JSON, "r", encoding="utf-8") as f:
    extracted_chunks = json.load(f)
test_extractor(extracted_chunks)  # test raw extracted for chapter 4 JSON before chunking

print(40* "=")
print("STEP2: Parsing and chunking sections separately, then unifying.")
print(40* "=")

# Parse and chunk each section separately for better control and debugging
ch4_chunks = chunk_processes()
ch3_chunks = chunk_ch3()
ch5_chunks = chunk_ch5()
unify_chunks()
print(40* "=")
print("Test unified chunks") # test unified chunks
print(40* "=")
# after unify_chunks():
with open(ALL_CHUNKS_JSON, "r", encoding="utf-8") as f:
    all_chunks = json.load(f)

test_chunker(all_chunks)
test_chunk_lengths(all_chunks)

print(40* "=")
print("STEP3: Embedding generation and tests")
print(40* "=")

# Generate embeddings (run after chunking)
if not (Path(EMBEDDINGS_JSON).exists()):
    generate_embeddings_script()
    print("Embeddings generated.")
else:
    print("Embeddings already exist. Skipping.")

test_model_loads()
# embedding quality (run after generate_embeddings.py)
test_embedding_quality()

print(40* "=")
print("STEP4: Ingestion into vector store and sanity checks")
print(40* "=")

# Ingest into vector store (run after generate_embeddings.py)
ingest_vectorstore()
print("Data ingested into vector store.")

# Sanity checks on vector store ingestion
sanity_checks()  # sanity checks on vector store ingestion
if RUN_PCA:
    plot_PCA()  # visualize embeddings with PCA
print(80* "=")
print("RAG pipeline setup complete!")
print(80* "=")
