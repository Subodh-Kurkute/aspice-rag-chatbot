from sentence_transformers import SentenceTransformer
from config import EMBEDDINGS_JSON, EMBEDDING_MODEL, EMBEDDING_PREFIX_DOC, EMBEDDING_PREFIX_QUERY
import json

model = SentenceTransformer(EMBEDDING_MODEL, trust_remote_code=True)

def embed_document(text: str) -> list[float]:
    return model.encode(EMBEDDING_PREFIX_DOC + text).tolist()

def embed_query(text: str) -> list[float]:
    return model.encode(EMBEDDING_PREFIX_QUERY + text).tolist()

def embed_and_save(chunks, output_path=EMBEDDINGS_JSON):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    embedded = []
    for chunk in chunks:
        embedded.append({
            "chunk_id":  chunk["chunk_id"],
            "source":    chunk["source"],
            "type":      chunk["type"],
            "title":     chunk["title"],
            "text":      chunk["text"],
            'page_number': chunk.get("page_number"),
            "embedding": embed_document(chunk["text"])
        })
        print(f"{chunk['chunk_id']:<12} embedded")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(embedded, f, indent=2)
    print(f"\nSaved {len(embedded)} embeddings to {output_path}")
    return embedded