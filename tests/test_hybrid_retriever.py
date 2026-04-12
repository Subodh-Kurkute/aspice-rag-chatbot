from src.retrieval.hybrid import hybrid_search
import pandas as pd
from pathlib import Path
from config import OUTPUT_DIR

test_queries = [
    'What are the base practices of SWE.6?',
    'BPs of SWE.6',
    'software unit verification',
    'corrective action document',
    'what is Process Reference Model',     
    'SWE.2 output work products',
    'Generic practices level 2'
]

output_file = Path(OUTPUT_DIR) / "hybrid_results.txt"
output_file.parent.mkdir(parents=True, exist_ok=True)

with open(output_file, "w", encoding="utf-8") as f:
    for query in test_queries:
        results = hybrid_search(query, top_k=3)
        df = pd.DataFrame(results)[["chunk_id", "title", "type", "rrf_score"]]

        text = f"\n=== {query} ===\n" + df.to_string(index=False) + "\n"

        print(text)
        f.write(text)

print(f"Saved results to {output_file}")