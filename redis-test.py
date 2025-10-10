import os
from flask import Flask, jsonify
from flask.cli import load_dotenv
from flask_cors import CORS
import redis

# Load environment variables
load_dotenv()

# Flask App Initialization
app = Flask(__name__)
CORS(app)

# Constants
REDIS_HOST = "REDIS_HOSTNAME"
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
VECTOR_DIMENSIONS = int(os.getenv("VECTOR_DIMENSIONS", 1536))
INDEX_NAME = os.getenv("INDEX_NAME", "security_auditor_index")

# Redis connection
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@app.route('/redis/all_embeddings', methods=['DELETE'])
def delete_all_embeddings():
    try:
        # Search all documents in the index
        result = redis_client.ft(INDEX_NAME).search("*")

        deleted_ids = []
        for doc in result.docs:
            doc_id = doc.id
            redis_client.delete(doc_id)
            deleted_ids.append(doc_id)

        return jsonify({
            "message": f"Deleted {len(deleted_ids)} embeddings.",
            "deleted_ids": deleted_ids
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)