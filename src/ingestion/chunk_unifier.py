import json
from config import ALL_CHUNKS_JSON
from src.ingestion.chunker import chunk_processes
from src.ingestion.ch5_chunker import chunk_ch5
from src.ingestion.ch3_chunker import chunk_ch3

def main():
    ch4 = chunk_processes()
    ch5 = chunk_ch5()
    ch3 = chunk_ch3()
    all_chunks = ch4 + ch5 + ch3
    print(f"Total: {len(all_chunks)} chunks")

    ALL_CHUNKS_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(ALL_CHUNKS_JSON, "w") as f:
        json.dump(all_chunks, f, indent=2)

    print(f"Saved to {ALL_CHUNKS_JSON}")

if __name__ == "__main__":
    main()
