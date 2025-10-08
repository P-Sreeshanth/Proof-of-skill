"""
Quantum Intent Processor Service
Captures user intent and translates to actionable challenges
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import hashlib
from datetime import datetime
import numpy as np

app = Flask(__name__)
CORS(app)

class QuantumIntentProcessor:
    def __init__(self):
        self.penrose_framework = os.getenv('PENROSE_FRAMEWORK', 'enabled')
        self.quantum_simulation = os.getenv('QUANTUM_SIMULATION', 'true') == 'true'
        self.nlp_model = os.getenv('NATURAL_LANGUAGE_MODEL', 'mistral-7b-instruct')
        self.quantum_state_dir = '/app/quantum-state'
        
    def capture_intent(self, intent_text, context=None):
        """Capture and process user intent using quantum-inspired methods"""
        
        # Generate unique intent ID
        intent_id = hashlib.sha256(
            f"{intent_text}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Extract key concepts from intent
        concepts = self._extract_concepts(intent_text)
        
        # Create quantum superposition of possible interpretations
        quantum_state = self._create_quantum_state(concepts)
        
        # Collapse to most probable interpretation
        processed_intent = self._collapse_interpretation(quantum_state, concepts)
        
        # Store quantum state
        self._save_quantum_state(intent_id, quantum_state)
        
        return {
            'intentId': intent_id,
            'originalIntent': intent_text,
            'processedIntent': processed_intent,
            'concepts': concepts,
            'quantumState': {
                'dimensions': len(quantum_state),
                'entropy': float(self._calculate_entropy(quantum_state)),
                'coherence': float(np.mean(quantum_state))
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _extract_concepts(self, text):
        """Extract key concepts from intent text"""
        # Simplified concept extraction
        keywords = ['prove', 'demonstrate', 'show', 'skill', 'ability', 'knowledge']
        
        concepts = {
            'action': 'prove',
            'domain': self._extract_domain(text),
            'skill_level': self._estimate_skill_level(text),
            'urgency': 'normal',
            'context': text
        }
        
        return concepts
    
    def _extract_domain(self, text):
        """Extract domain from text"""
        domains = {
            'react': ['react', 'jsx', 'component'],
            'python': ['python', 'django', 'flask'],
            'javascript': ['javascript', 'js', 'node'],
            'sql': ['sql', 'mysql', 'postgres', 'postgresql', 'sqlite', 'query', 'database', 'sql query'],
            'debug': ['debug', 'fix', 'error', 'bug'],
            'design': ['design', 'ui', 'ux', 'interface']
        }
        
        text_lower = text.lower()
        for domain, keywords in domains.items():
            if any(kw in text_lower for kw in keywords):
                return domain
        
        return 'general'
    
    def _estimate_skill_level(self, text):
        """Estimate desired skill level from text"""
        if any(word in text.lower() for word in ['advanced', 'expert', 'master']):
            return 'advanced'
        elif any(word in text.lower() for word in ['intermediate', 'moderate']):
            return 'intermediate'
        else:
            return 'beginner'
    
    def _create_quantum_state(self, concepts):
        """Create quantum superposition state"""
        # Create a quantum-inspired state vector
        state_dim = 16
        state = np.random.random(state_dim) + 1j * np.random.random(state_dim)
        
        # Normalize
        state = state / np.linalg.norm(state)
        
        return state.tolist()
    
    def _collapse_interpretation(self, quantum_state, concepts):
        """Collapse quantum state to most probable interpretation"""
        return {
            'type': 'skill_verification',
            'domain': concepts['domain'],
            'target_skill': concepts['domain'],
            'difficulty': self._map_skill_to_difficulty(concepts['skill_level']),
            'format': 'challenge',
            'evaluation_criteria': ['correctness', 'efficiency', 'best_practices']
        }
    
    def _map_skill_to_difficulty(self, skill_level):
        """Map skill level to difficulty score"""
        mapping = {
            'beginner': 3,
            'intermediate': 6,
            'advanced': 9
        }
        return mapping.get(skill_level, 5)
    
    def _calculate_entropy(self, state):
        """Calculate entropy of quantum state"""
        state_array = np.array(state)
        probabilities = np.abs(state_array) ** 2
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        return entropy
    
    def _save_quantum_state(self, intent_id, quantum_state):
        """Save quantum state to disk"""
        os.makedirs(self.quantum_state_dir, exist_ok=True)
        
        state_file = os.path.join(self.quantum_state_dir, f"{intent_id}.json")
        with open(state_file, 'w') as f:
            # Convert complex numbers to dict format
            state_data = [{'real': float(np.real(s)), 'imag': float(np.imag(s))} 
                         for s in quantum_state]
            json.dump({
                'intent_id': intent_id,
                'state': state_data,
                'timestamp': datetime.now().isoformat()
            }, f)

processor = QuantumIntentProcessor()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'quantum-intent-processor'}), 200

@app.route('/api/v1/intent', methods=['POST'])
def process_intent():
    try:
        data = request.json
        intent = data.get('intent')
        context = data.get('context', {})
        
        if not intent:
            return jsonify({'error': 'Intent text required'}), 400
        
        result = processor.capture_intent(intent, context)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/intent/<intent_id>', methods=['GET'])
def get_intent(intent_id):
    try:
        state_file = os.path.join(processor.quantum_state_dir, f"{intent_id}.json")
        
        if not os.path.exists(state_file):
            return jsonify({'error': 'Intent not found'}), 404
        
        with open(state_file, 'r') as f:
            data = json.load(f)
        
        return jsonify(data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3001))
    app.run(host='0.0.0.0', port=port, debug=True)
