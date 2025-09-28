"""
===============================================================================
 File Name   : knowledge_ingestor.py
 Description : Autonomous Security Auditor Knowledge Ingestor file helps to 
               ingest organization security policies into Redis vector database.
 Author      : Sachin Ghumbre
 Created On  : 2025-09-26
 Version     : v1.0.0
 License     : Proprietary
 Tags        : python, redis, kong, konnect, genai, audit, langgraph, agentic ai
===============================================================================
"""
from flask import Flask, jsonify
import os
import uuid
import time
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import redis
from redis.commands.search.field import TagField, VectorField, TextField
from redis.commands.search.index_definition import IndexDefinition, IndexType
import numpy as np
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
VECTOR_DIMENSIONS = int(os.getenv("VECTOR_DIMENSIONS"))
CHUNK_SIZE = 300  # characters per chunk

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_EMBEDDING_MODEL_NAME = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL_NAME")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")


# Initialize Redis
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_version=AZURE_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY
)

# Directory to ingest
KNOWLEDGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "knowledge_base"))

def get_embedding(text):
    """
    Generate an embedding for the given text using Azure OpenAI.
    """
    response = client.embeddings.create(
        input=[text],
        model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT
    )
    return response.data[0].embedding

@app.route('/api/v1/knowledge/ingest', methods=['POST'])
def ingest_knowledge_base():

    if not os.path.exists(KNOWLEDGE_DIR):
        return jsonify({"error": "Directory not found"}), 404

    # Connect to Redis
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=False)

    # Create Redis vector index if it doesn't exist
    index_name = os.getenv("INDEX_NAME", "security_auditor_index")
    try:
        # Try to fetch index info; if it doesn't exist, create the index
        try:
            r.ft(index_name).info()
        except Exception:
            schema = (
                TextField("content"),
                VectorField("vector",
                            "FLAT",  # or "HNSW"
                            {
                                "TYPE": "FLOAT32",
                                "DIM": VECTOR_DIMENSIONS,
                                "DISTANCE_METRIC": "COSINE"
                            }),
                TagField("metadata")
            )
            definition = IndexDefinition(prefix=["embedding:"], index_type=IndexType.HASH)
            r.ft(index_name).create_index(schema, definition=definition)
    except Exception as e:
        print(f"Index creation error: {e}")

    ingested_chunks = []
    for filename in os.listdir(KNOWLEDGE_DIR):
        file_path = os.path.join(KNOWLEDGE_DIR, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Chunk the content
            chunks = [content[i:i+CHUNK_SIZE] for i in range(0, len(content), CHUNK_SIZE)]

            for chunk in chunks:
                # Generate embedding using your existing embedding model
                try:
                    embedding = get_embedding(chunk)  # Replace with your embedding function
                except Exception as e:
                    return jsonify({"error": f"Embedding failed for {filename}: {str(e)}"}), 500

                if len(embedding) != VECTOR_DIMENSIONS:
                    return jsonify({"error": f"Embedding dimension mismatch for {filename}"}), 500

                chunk_id = str(uuid.uuid4())
                metadata = {
                    "filename": filename,
                    "chunk_id": chunk_id,
                    "timestamp": time.time(),
                    "source": "api_policies"
                }

                # Store in Redis with vector field as bytes (float32)
                redis_key = f"embedding:{chunk_id}"
                vector_bytes = np.array(embedding, dtype=np.float32).tobytes()
                r.hset(redis_key, mapping={
                    "content": chunk,
                    "vector": vector_bytes,
                    "metadata": str(metadata)
                })
                ingested_chunks.append(chunk_id)

    # Gather details of all ingested chunks from Redis
    chunk_details = []
    for chunk_id in ingested_chunks:
        redis_key = f"embedding:{chunk_id}"
        data = r.hgetall(redis_key)
        # Convert vector bytes back to list for readability (optional)
        vector = np.frombuffer(data.get(b"vector", b""), dtype=np.float32).tolist()
        chunk_details.append({
            "chunk_id": chunk_id,
            "content": data.get(b"content", "").decode("utf-8") if data.get(b"content") else "",
            "vector": vector,
            "metadata": data.get(b"metadata", "").decode("utf-8") if data.get(b"metadata") else ""
        })

    return jsonify({
        "message": "Ingestion complete",
        "chunks": chunk_details,
        "index_name": index_name
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)
