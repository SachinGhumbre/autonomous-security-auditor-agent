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

import os
import uuid
import time
import numpy as np
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import AzureOpenAI
import redis
from redis.commands.search.field import TagField, VectorField, TextField
from redis.commands.search.index_definition import IndexDefinition, IndexType
import json

# Load environment variables
load_dotenv()

# Flask App Initialization
app = Flask(__name__)
CORS(app)

# Constants
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
VECTOR_DIMENSIONS = int(os.getenv("VECTOR_DIMENSIONS", 1536))
CHUNK_SIZE = 300
INDEX_NAME = os.getenv("INDEX_NAME", "security_auditor_index")
KNOWLEDGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "knowledge_base"))

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")

# Initialize Redis and Azure OpenAI
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=False)
openai_client = AzureOpenAI(
    api_version=AZURE_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY
)


def get_embedding(text: str) -> list:
    """Generate an embedding for the given text using Azure OpenAI."""
    response = openai_client.embeddings.create(
        input=[text],
        model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT
    )
    return response.data[0].embedding


def create_vector_index(r: redis.Redis) -> None:
    """Create Redis vector index if it doesn't exist."""
    try:
        r.ft(INDEX_NAME).info()
    except Exception:
        schema = (
            TextField("content"),
            VectorField("vector", "FLAT", {
                "TYPE": "FLOAT32",
                "DIM": VECTOR_DIMENSIONS,
                "DISTANCE_METRIC": "COSINE"
            }),
            TagField("metadata")
        )
        definition = IndexDefinition(prefix=["embedding:"], index_type=IndexType.HASH)
        r.ft(INDEX_NAME).create_index(schema, definition=definition)


@app.route('/api/v1/knowledge/ingest', methods=['POST'])
def ingest_knowledge_base() -> tuple:
    """Ingest knowledge base files into Redis vector DB."""
    if not os.path.exists(KNOWLEDGE_DIR):
        return jsonify({"error": "Directory not found"}), 404

    create_vector_index(redis_client)

    ingested_chunks = []

    for filename in os.listdir(KNOWLEDGE_DIR):
        file_path = os.path.join(KNOWLEDGE_DIR, filename)
        if not os.path.isfile(file_path):
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        chunks = [content[i:i + CHUNK_SIZE] for i in range(0, len(content), CHUNK_SIZE)]

        for chunk in chunks:
            try:
                embedding = get_embedding(chunk)
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

            redis_key = f"embedding:{chunk_id}"
            vector_bytes = np.array(embedding, dtype=np.float32).tobytes()

            redis_client.hset(redis_key, mapping={
                "content": chunk,
                "vector": vector_bytes,
                "metadata": str(metadata)
            })

            ingested_chunks.append(chunk_id)

    chunk_details = []
    for chunk_id in ingested_chunks:
        redis_key = f"embedding:{chunk_id}"
        data = redis_client.hgetall(redis_key)

        vector = np.frombuffer(data.get(b"vector", b""), dtype=np.float32).tolist()
        chunk_details.append({
            "chunk_id": chunk_id,
            "content": data.get(b"content", b"").decode("utf-8") if data.get(b"content") else "",
            "vector": vector,
            "metadata": data.get(b"metadata", b"").decode("utf-8") if data.get(b"metadata") else ""
        })

    return jsonify({
        "message": "Ingestion complete",
        "chunks": chunk_details,
        "index_name": INDEX_NAME
    }), 200

@app.route('/api/v1/knowledge/get_all_embeddings', methods=['GET'])
def get_all_embeddings():
    try:
        # Use FT.SEARCH to get all documents from the index
        query = "*"
        result = redis_client.ft(INDEX_NAME).search(query)

        embeddings = []
        for doc in result.docs:
            embeddings.append({
                "id": doc.id,
                "embedding": json.loads(doc.embedding),  # assuming embedding is stored as JSON string
                "metadata": {k: v for k, v in doc.__dict__.items() if k not in ['id', 'embedding']}
            })

        return jsonify({"count": len(embeddings), "embeddings": embeddings})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == '__main__':
    app.run(debug=True, port=5001)