from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from uuid import uuid4
from config import QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME
import time

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

def initialize_collection():
    try:
        # Check if collection exists and delete it (to recreate with new dimensions)
        client.get_collection(COLLECTION_NAME)
        client.delete_collection(collection_name=COLLECTION_NAME)
        print(f"Deleted existing collection {COLLECTION_NAME}")
    except Exception:
        pass
    
    # Create new collection with OpenAI embedding dimensions (1536)
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
    )
    print(f"Created collection {COLLECTION_NAME} with 1536 dimensions")
    
    # Add index for filtering
    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="pdf_name",
        field_schema="keyword"
    )
    time.sleep(1)  # Allow index to be created

def store_embeddings(pdf_name, chunks, embeddings):
    points = []
    for chunk, embedding in zip(chunks, embeddings):
        points.append(PointStruct(
            id=str(uuid4()),
            vector=embedding,
            payload={
                "text": chunk,
                "pdf_name": pdf_name
            }
        ))
    
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    print(f"Stored {len(points)} chunks for {pdf_name}")

def get_pdf_list():
    # Get unique PDF names from payload
    result = client.scroll(
        collection_name=COLLECTION_NAME,
        with_payload=True,
        limit=10000
    )
    
    pdf_names = set()
    for point in result[0]:
        if "pdf_name" in point.payload:
            pdf_names.add(point.payload["pdf_name"])
    
    return list(pdf_names)

def search_documents(query_embedding, pdf_name, top_k=5):
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        query_filter=Filter(
            must=[FieldCondition(key="pdf_name", match=MatchValue(value=pdf_name))]
        ),
        limit=top_k
    )
    return results.points