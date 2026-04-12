import json, re
from rank_bm25 import BM25Okapi
from config import ALL_CHUNKS_JSON
from rank_bm25 import BM25Okapi

def tokenize(text):
    return re.sub(r'[^\w\s]', '', text.lower()).split()

def build_bm25_index(chunks: list[dict]):
    corpus_ids   = [c['chunk_id'] for c in chunks]
    corpus_texts = [c['text'] for c in chunks]
    tokenized    = [tokenize(t) for t in corpus_texts]
    print(f"BM25 index built over {len(corpus_texts)} chunks")
    bm25 = BM25Okapi(tokenized)
    return bm25, corpus_ids


def load_chunks(path=ALL_CHUNKS_JSON) -> list[dict]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)