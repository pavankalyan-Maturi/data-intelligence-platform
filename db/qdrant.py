from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import os
from dotenv import load_dotenv

load_dotenv()

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "data_intel")
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 outputs 384-dimensional vectors

def get_qdrant_client():
    return QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

def init_qdrant_collection():
    client = get_qdrant_client()
    existing = [c.name for c in client.get_collections().collections]

    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE  # use cosine similarity
            )
        )
        print(f"✅ Qdrant collection '{COLLECTION_NAME}' created!")
    else:
        print(f"✅ Qdrant collection '{COLLECTION_NAME}' already exists!")

def store_embeddings(points: list[PointStruct]):
    client = get_qdrant_client()
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    print(f"✅ Stored {len(points)} embeddings in Qdrant!")

def search_similar(query_vector: list[float], top_k: int = 5):
    client = get_qdrant_client()
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k
    ).points
    return results