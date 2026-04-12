import chromadb
from config import VECTORSTORE_DIR, COLLECTION_NAME, OUTPUT_DIR
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from pathlib import Path
from src.generation import client



def sanity_checks():
    # Connect to ChromaDB and get collection
    client = chromadb.PersistentClient(path=str(VECTORSTORE_DIR))
    collection = client.get_collection(COLLECTION_NAME)
    # Basic sanity checks
    print(f"Total chunks: {collection.count()}")
    print(f"Sample IDs: {collection.get(limit=5)['ids']}")
    if collection.count() == 0:
        raise ValueError(f"[VECTORSTORE] No chunks found in collection.")
    # Fetch a sample chunk by ID
    else:
        result = collection.get(
                ids=["ACQ.4"],
                include=["documents", "metadatas", "embeddings"]
            )
        if not result['ids']:
            raise ValueError("[VECTORSTORE] Warning: Sample ID 'ACQ.4' not found in collection.")
        else:
            print(result['metadatas'])
            print(result['documents'][0][:300])
            print(f"Embedding dim: {len(result['embeddings'][0])}")
        if len(result['embeddings'][0]) != 768:
            raise ValueError(f"[VECTORSTORE] Warning: Embedding dimension is {len(result['embeddings'][0])}, expected 768.")
  
# Visualize embeddings with PCA
def plot_PCA():
    client = chromadb.PersistentClient(path=str(VECTORSTORE_DIR))
    collection = client.get_collection(COLLECTION_NAME)
    all_data = collection.get(include=["embeddings", "metadatas"])
    embeddings = np.array(all_data['embeddings'])
    labels = [m['process_group'] for m in all_data['metadatas']]
    ids = [m['chunk_id'] for m in all_data['metadatas']]

    pca = PCA(n_components=2)
    reduced = pca.fit_transform(embeddings)

    plt.figure(figsize=(12, 8))
    groups = list(set(labels))
    colors = plt.cm.tab10(np.linspace(0, 1, len(groups)))

    for group, color in zip(groups, colors):
        mask = [l == group for l in labels]
        plt.scatter(reduced[mask, 0], reduced[mask, 1], label=group, color=color, s=100)

    for i, pid in enumerate(ids):
        plt.annotate(pid, (reduced[i, 0], reduced[i, 1]), fontsize=7)

    plt.legend()
    plt.title("ASPICE Process Embeddings (PCA 2D)")
    plt.tight_layout()
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "aspice_pca.png"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"Plot saved to: {output_file}")
    plt.show()

if __name__ == "__main__":
    sanity_checks()
    plot_PCA()
    