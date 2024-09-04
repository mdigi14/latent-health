from confluent_kafka import Producer
import dotenv
import json
import random
import time
import os
from fastapi import FastAPI
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec

dotenv.load_dotenv()

INDEX_NAME = 'latent-health-index'

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
pc = Pinecone(api_key=PINECONE_API_KEY)

app = FastAPI()

@app.get("/call_openai")
def get_response(query: str = None):
    client = OpenAI()

    res = client.embeddings.create(
        input=query,
        model="text-embedding-ada-002"
        
    )

    # retrieve from Pinecone
    xq = res.data[0].embedding

    # get relevant contexts (including the questions)
    index = pc.Index(INDEX_NAME)        
    res = index.query(vector=xq, top_k=3, include_metadata=True)
    print(f"Raw Pinecone results: {json.dumps(res.to_dict(), indent=4)}")
    print(f"Type of Pinecone results: {type(res)}")

    # Convert QueryResponse tp dict
    res = res.to_dict()

    # Extract context from the RAG results
    rag_context = [item for item in res['matches']]
    print(f"RAG context: {rag_context}")

    # Create the completion request with the RAG context
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=100,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"Context: {rag_context}\n\nQuery: {query}"
            }
        ]
    )

    msg = completion.choices[0].message
    return {        
        "timestamp": time.time(),
        "query": query,
        "rag_context": rag_context,
        "message": msg
    }


@app.post("/create_embedding")
def post_file(url: str):
    TOPIC_NAME = "raw_html"

    # Write to Kafka topic here
    conf = {
        'bootstrap.servers': 'localhost:9092',  # Kafka broker address
    }

    # Produce the message
    producer = Producer(conf)
    value = {
        "url": url,
        "timestamp": time.time(),
    }
    producer.produce(TOPIC_NAME, value=json.dumps(value))
    producer.flush()
    

    return {        
        "status": "success",
        "message": f"Will create embeddings for {url}",
    }