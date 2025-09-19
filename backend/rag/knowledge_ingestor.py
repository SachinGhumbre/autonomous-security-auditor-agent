from flask import Flask, jsonify
import os
import redis
import uuid
import time
import google.generativeai as genai

app = Flask(__name__)

# Configuration
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
VECTOR_DIMENSIONS = int(os.getenv("VECTOR_DIMENSIONS", "768"))  # Set default or adjust as per Gemini model
CHUNK_SIZE = 300  # characters per chunk

# Initialize Redis
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Initialize Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Directory to ingest
KNOWLEDGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "knowledge_base", "api_policies"))

@app.route('/ingest', methods=['POST'])
def ingest_knowledge_base():
    if not os.path.exists(KNOWLEDGE_DIR):
        return jsonify({"error": "Directory not found"}), 404

    ingested_chunks = []
    for filename in os.listdir(KNOWLEDGE_DIR):
        file_path = os.path.join(KNOWLEDGE_DIR, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Chunk the content
            chunks = [content[i:i+CHUNK_SIZE] for i in range(0, len(content), CHUNK_SIZE)]

            for chunk in chunks:
                # Generate embedding using Gemini
                try:
                    # Use the embeddings API directly
                    embedding_response = genai.embed_content(
                        model="models/embedding-001",
                        content=chunk,
                        task_type="retrieval_document"
                    )
                    embedding = embedding_response['embedding']
                except Exception as e:
                    return jsonify({"error": f"Embedding failed for {filename}: {str(e)}"}), 500

                # Validate dimensions
                if len(embedding) != VECTOR_DIMENSIONS:
                    return jsonify({"error": f"Embedding dimension mismatch for {filename}"}), 500

                # Metadata for Kong RAG Injector
                chunk_id = str(uuid.uuid4())
                metadata = {
                    "filename": filename,
                    "chunk_id": chunk_id,
                    "timestamp": time.time(),
                    "source": "api_policies"
                }

                # Store in Redis
                redis_key = f"embedding:{chunk_id}"
                redis_client.hset(redis_key, mapping={
                    "content": chunk,
                    "vector": str(embedding),
                    "metadata": str(metadata)
                })
                ingested_chunks.append(chunk_id)

    return jsonify({"message": "Ingestion complete", "chunks": ingested_chunks}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)