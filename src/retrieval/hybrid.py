from config import EMBEDDING_MODEL
from src.retrieval.vectorstore import semantic_search
from src.retrieval.bm25 import tokenize, build_bm25_index, load_chunks
import re

LEVEL_CHUNK_MAP = {'1': '5.2', '2': '5.3', '3': '5.4', '4': '5.5', '5': '5.6'}

# initialise once at import time
_chunks = load_chunks()
_bm25, corpus_ids = build_bm25_index(_chunks)
_embedding_model = EMBEDDING_MODEL

# embed all chunks once at import time for dense retrieval

def embed_query(text):
    # 'search_query:' prefix is required for nomic retrieval tasks
    return _embedding_model.encode('search_query: ' + text).tolist()

#  Calculate RRF score
def rrf_score(rank, k=60):
    return 1 / (k + rank)

# Extract process ID from query (e.g., "SWE.6" from "what are the base practices of SWE.6?")
def extract_process_id(query):
    match = re.search(r'\b([A-Z]+\.\d+)\b', query)
    return match.group(1) if match else None

# Extract capability level from query (e.g., "level 3" from "what are the requirements for level 3?")
def extract_capability_level(query):
    match = re.search(r'level\s*(\d)', query.lower())
    return match.group(1) if match else None

# Main hybrid search function
def hybrid_search(query, top_k=10):

    # --- Semantic ---
    sem_results = semantic_search(query, n_results=top_k)
    sem_ids = sem_results['ids'][0]

    # --- BM25 ---
    scores = _bm25.get_scores(tokenize(query))
    bm25_ranked = sorted(zip(corpus_ids, scores), key=lambda x: x[1], reverse=True)[:top_k]
    bm25_ids = [cid for cid, _ in bm25_ranked]

    # --- RRF Fusion (50-50) ---
    rrf = {}
    for rank, cid in enumerate(sem_ids):
        rrf[cid] = rrf.get(cid, 0) + 0.5 * rrf_score(rank)
    for rank, cid in enumerate(bm25_ids):
        rrf[cid] = rrf.get(cid, 0) + 0.5 * rrf_score(rank)

    ranked = sorted(rrf.items(), key=lambda x: x[1], reverse=True)[:top_k]

    # --- Process ID boost: move exact match to top -
    process_id = extract_process_id(query)  # e.g. "SWE.6"
    if process_id:
        ranked_ids = [cid for cid, _ in ranked]
        if process_id not in ranked_ids:
            ranked_ids.insert(0, process_id)
        else:
            ranked_ids.remove(process_id)
            ranked_ids.insert(0, process_id)
        ranked = [(cid, rrf.get(cid, 0)) for cid in ranked_ids[:top_k]]

    # --- Capability Level boost --- 
    level = extract_capability_level(query)
    if level and level in LEVEL_CHUNK_MAP:
        level_chunk = LEVEL_CHUNK_MAP[level]
        ranked_ids = [cid for cid, _ in ranked]
        if level_chunk not in ranked_ids:
            ranked_ids.insert(0, level_chunk)
        else:
            ranked_ids.remove(level_chunk)
            ranked_ids.insert(0, level_chunk)
        ranked = [(cid, rrf.get(cid, 0)) for cid in ranked_ids[:top_k]]

    # --- Fetch metadata for display ---
    id_to_meta = {c['chunk_id']: c for c in _chunks}
    results = []
    for cid, score in ranked:
        c = id_to_meta.get(cid, {})
        results.append({
            'chunk_id':  cid,
            'title':     c.get('title', ''),
            'type':      c.get('type', ''),
            'text':        c.get('text', ''),         # full text for LLM
            'text_preview': c.get('text', '')[:300],
            'rrf_score': score, # Added rrf_score here
            'page_number': c.get('page_number', '')
        })
    return results

