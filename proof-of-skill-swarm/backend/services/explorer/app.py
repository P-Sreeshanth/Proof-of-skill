"""
Explorer Service
Serves stored proofs from /app/proofs and exposes simple mock TBA endpoints.
"""

from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)

PROOFS_DIR = '/app/proofs'

@app.get('/health')
def health():
    return jsonify({"service": "explorer", "status": "healthy"})


@app.get('/proofs/<proof_id>')
def get_proof(proof_id):
    path = os.path.join(PROOFS_DIR, f"{proof_id}.json")
    if not os.path.exists(path):
        return jsonify({"error": "proof not found"}), 404
    with open(path, 'r') as f:
        data = json.load(f)
    return jsonify(data)


@app.get('/tba/create/<token_id>')
def create_tba(token_id):
    # Mock: derive a pseudo account address
    account = '0x' + (str(abs(hash(token_id)))[:38]).zfill(40)
    return jsonify({"tokenId": token_id, "account": account, "status": "created"})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 3013))
    app.run(host='0.0.0.0', port=port, debug=True)


