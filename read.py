import boto3
import json
import os
import urllib.request
import time
import traceback
from confluent_kafka import Consumer
from parsing_utils import extract_text_from_html, split_text_into_chunks, get_embeddings
from pinecone_utils import write_embeddings

# Configuration for Kafka consumer
conf = {
    'bootstrap.servers': 'localhost:9092',  # Kafka broker address
    'group.id': 'my-consumer-group',        # Consumer group ID
    'auto.offset.reset': 'latest'         # Start reading at the latest
}

def create_session():
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_DEFAULT_REGION')

    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region
    )

    dynamodb = session.resource('dynamodb', region_name=aws_region)

    table = dynamodb.Table("articles")
    return table

# Continuously consume messages and print to console
def consume(id: int):
    # Create dynamodb 
    table = create_session()

    # Create a Consumer instance
    print(f"Starting consumer {id}")
    consumer = Consumer(conf)

    # Subscribe to the 'test' topic
    consumer.subscribe(['raw_html'])

    # Create a URL opener
    opener = urllib.request.FancyURLopener({})
    
    while True:
        try:
            msg = consumer.poll()  # Poll for new messages
            if msg is not None and not msg.error():
                msg = json.loads(msg.value().decode('utf-8'))
                

                
                start = time.time()
                url = msg["url"]
                print(f"Processed via consumer {id}: {url}")  # Print the message value

                f = opener.open(url)                
                content = f.read()
                text = extract_text_from_html(content)
                chunks = split_text_into_chunks(text)
                embeddings = get_embeddings(chunks)
                
                item = {
                    "url": url,
                    "embeddings": str(embeddings)
                }
                
                write_embeddings(url, embeddings)

                table.put_item(Item=item)
                finish = time.time()
                print(f"Job took: {finish - start} seconds")
                
                
            else:
                print(f"Process {id} queried topic")
        except Exception as e:
            print(f"Consumer {id} encountered an error: {e}")
            traceback.print_exc()

consume(1)