import sys, json
from config import ALL_CHUNKS_JSON
from src.ingestion.embedder import embed_and_save


def main():
    with open(ALL_CHUNKS_JSON, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Loaded {len(chunks)} chunks from {ALL_CHUNKS_JSON}")
    embed_and_save(chunks)

if __name__ == "__main__":
    main()
