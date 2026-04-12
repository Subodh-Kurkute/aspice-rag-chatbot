import json
import numpy as np
from config import EMBEDDINGS_JSON

def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def test_embedding_quality():
    with open(EMBEDDINGS_JSON, "r", encoding="utf-8") as f:
        embedded = json.load(f)

    errors = []
    texts = {e["chunk_id"]: e["embedding"] for e in embedded}

    # no zero vectors
    for e in embedded:
        if np.linalg.norm(e["embedding"]) == 0:
            errors.append(f"[{e['chunk_id']}] zero vector")

    # related vs unrelated similarity check
    # SYS.1 and SYS.2 are both system engineering — should be similar
    # SYS.1 and MAN.3 are unrelated — should be dissimilar
    pairs = [("SWE.6", "SYS.5", "SYS.4"), ("SWE.2", "SWE.1", "MAN.3")]
    for a, related, unrelated in pairs:
        missing = [k for k in [a, related, unrelated] if k not in texts]
        if missing:
            print(f"[EMBEDDINGS] SKIP similarity check — missing chunk IDs: {missing}")
            continue
        sim_related = cosine_similarity(texts[a], texts[related])
        sim_unrelated = cosine_similarity(texts[a], texts[unrelated])
        print(f"[EMBEDDINGS] {a} vs {related} (related):   {sim_related:.3f}")
        print(f"[EMBEDDINGS] {a} vs {unrelated} (unrelated): {sim_unrelated:.3f}")
        if sim_related <= sim_unrelated:
            errors.append(f"{a} vs {related} not scoring higher than {a} vs {unrelated}")

    print(f"\n{'='*40}")
    print(f"[EMBEDDINGS] Errors: {len(errors)}")
    if errors:
        for e in errors:
            print(f"  ✗ {e}")
    else:
        print("[EMBEDDINGS] All tests passed.")

if __name__ == "__main__":
    test_embedding_quality()