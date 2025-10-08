"""
Simple Neural Network Service
Provides basic neural network capabilities for other services
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import os

app = Flask(__name__)
CORS(app)

class SimpleNeuralNetwork:
    def __init__(self):
        self.models_dir = '/app/models'
        
    def forward(self, input_data):
        """Simple forward pass"""
        # Simulate neural network processing
        output = np.tanh(np.array(input_data))
        return output.tolist()
    
    def embed(self, text):
        """Generate text embeddings"""
        # Simple hash-based embedding (in production, use real embeddings)
        hash_val = hash(text)
        np.random.seed(abs(hash_val) % (2**32))
        embedding = np.random.randn(768)
        embedding = embedding / np.linalg.norm(embedding)
        return embedding.tolist()

network = SimpleNeuralNetwork()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'neural-network'}), 200

@app.route('/api/v1/forward', methods=['POST'])
def forward():
    try:
        data = request.json
        input_data = data.get('input', [])
        
        output = network.forward(input_data)
        return jsonify({'output': output}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/embed', methods=['POST'])
def embed():
    try:
        data = request.json
        text = data.get('text', '')
        
        embedding = network.embed(text)
        return jsonify({'embedding': embedding}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3010))
    app.run(host='0.0.0.0', port=port, debug=True)
