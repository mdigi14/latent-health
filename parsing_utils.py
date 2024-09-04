import json
import openai
import tiktoken
from bs4 import BeautifulSoup

URL = "graham_essay.html"

def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Remove script and style elements
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()
    text = soup.get_text(separator=' ')
    return text

def split_text_into_chunks(text):
    # TODO: Can come back here and make chunks based on max token count
    sentences = text.split('. ')
    chunks = []

    cnt = 0
    for sentence in sentences:
        print(f"{cnt}: {sentence}")
        cnt += 1
        chunks.append(sentence)
    
    print(f"Number of chunks: {len(chunks)}")
    return chunks

def get_embeddings(chunks):    
    client = openai.Client()
    embeddings = {}

    # TODO: Do entire dataset
    for chunk in chunks[:10]:
        print(f'Starting embedding for chunk: {hash(chunk)}')
        response = client.embeddings.create(
            input=chunk,
            model="text-embedding-ada-002"
            
        )
        embeddings[chunk] = response.data[0].embedding
    return embeddings


def process_html_for_embeddings(html_file_path):
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    text = extract_text_from_html(html_content)
    chunks = split_text_into_chunks(text)
    embeddings = get_embeddings(chunks)
    
    return embeddings
