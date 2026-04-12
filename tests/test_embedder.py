from src.ingestion.embedder import embed_document, embed_query

def test_model_loads():
    doc_emb = embed_document("test document text")
    query_emb = embed_query("test query text")

    assert len(doc_emb) == 768, f"Expected 768 dims, got {len(doc_emb)}"
    assert len(query_emb) == 768, f"Expected 768 dims, got {len(query_emb)}"
    assert doc_emb != query_emb, "Doc and query embeddings should differ"

    print(f"[EMBEDDER] Dim: {len(doc_emb)}")
    print("[EMBEDDER] All tests passed.")

if __name__ == "__main__":
    test_model_loads()