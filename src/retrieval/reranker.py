# Reranker — cross-encoder/ms-marco-MiniLM-L-6-v2

def rerank(query: str, results: list[dict], top_n: int = 5) -> list[dict]:
    raise NotImplementedError("Reranker disabled — corpus too small. Enable at 150+ chunks.")