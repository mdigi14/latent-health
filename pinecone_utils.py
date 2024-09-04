import dotenv
import json
import os
import uuid
from pinecone import Pinecone, ServerlessSpec

INDEX_NAME = 'latent-health-index'

def write_embeddings(url: str, embeddings: dict):
    dotenv.load_dotenv()

    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # if len(pc.list_indexes().indexes) != 0:
    #     pc.create_index(
    #         name=INDEX_NAME,
    #         dimension=1536,  # Replace with your model dimensions
    #         metric="cosine",  # Replace with your model metric
    #         spec=ServerlessSpec(
    #             cloud="aws",
    #             region="us-east-1"
    #         )
    #     )
    # else:
    #     print(f"Index '{INDEX_NAME}' already exists.")

    index = pc.Index(INDEX_NAME)

    vectors = []
    for chunk,embedding in embeddings.items():
        vectors.append(
            {
                "id": str(uuid.uuid4()),
                "values": embedding,
                "metadata": {
                    "url": url,
                    "text": chunk
                }
            }
        )

    index.upsert(
        vectors=vectors
    )
    print(f"Embeddings {embeddings.keys()} written to index '{INDEX_NAME}'")