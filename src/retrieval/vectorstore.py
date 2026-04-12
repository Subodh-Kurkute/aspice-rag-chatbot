
import chromadb
from config import TOP_K, VECTORSTORE_DIR, COLLECTION_NAME
from src.ingestion.embedder import embed_query

def get_collection():
    client = chromadb.PersistentClient(path=VECTORSTORE_DIR)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

def ingest(chunks_with_embeddings):
    collection = get_collection()
    collection.add(
        ids=[c['chunk_id'] for c in chunks_with_embeddings],
        embeddings=[c['embedding'] for c in chunks_with_embeddings],
        documents=[c['text'] for c in chunks_with_embeddings],
        metadatas=[{
            "chunk_id":    c['chunk_id'],                        # "ACQ.4"
            "process_group": c['chunk_id'].split(".")[0],          # "ACQ"
            "process_name":  c['title'],                           # "Supplier Monitoring"
            "source":        c['source'],                          # "chapter4"
            "type":          c['type'],                            # "process"
            } for c in chunks_with_embeddings]
    )
    print(f"Inserted {collection.count()} chunks into ChromaDB")


def semantic_search(query, n_results=TOP_K):
    collection = get_collection()
    q_emb = embed_query(query)
    sem_results = collection.query(
        query_embeddings=[q_emb],
        n_results=n_results,
        include=['documents', 'metadatas', 'distances']
    )
    return sem_results