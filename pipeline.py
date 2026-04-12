# Edit queries in pipeline.py and run this to test the entire pipeline end-to-end

import json
from pathlib import Path
from datetime import datetime
from config import OUTPUT_DIR
from src.generation.generator import rag
import time
STORE_RESULTS = True  # Set to False to skip saving results to JSON

QUERIES = [
    
    "BPs of SWE.6",
    "software unit verification"
]
'''
# Further QUERIES for evaluation - feel free to modify or expand this list as needed
QUERIES = [
    "What is the capital of france?",
    "What are the base practices of SWE.6?",
    "corrective action document",
    "what is Process Reference Model",
    "SWE.2 output work products",
    "Generic practices level 2"
]
'''

OUTPUT_FILE = Path(OUTPUT_DIR) / "rag_results.json"

def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    results = []

    for query in QUERIES:
        answer, retrieved, token_info = rag(query, top_k=2)  # use top_k=2 for more concise output in evaluation

        results.append({
            "query": query,
            "answer": answer,
            "token_info": token_info,
            "retrieved_chunks": [
                {
                    "chunk_id": r.get("chunk_id"),
                    "title": r.get("title"),
                    "type": r.get("type"),
                    "rrf_score": r.get("rrf_score"),
                    "text": r.get("text"),
                    "text_preview": r.get("text_preview"),
                    "page_number": r.get("page_number")
                }
                for r in retrieved
            ]
        })
        time.sleep(20)  # brief pause between queries to avoid rate limits

    payload = {
        "created_at": datetime.now().isoformat(),
        "num_queries": len(QUERIES),
        "results": results,
    }
    if STORE_RESULTS:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        DIVIDER = "-" * 60
        print(f"\n{DIVIDER}")
        print(f"Saved RAG results to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()