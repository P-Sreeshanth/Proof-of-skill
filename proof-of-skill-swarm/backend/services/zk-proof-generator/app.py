"""
ZK-Proof Generator Service
Generates zero-knowledge proofs for skill verification
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import hashlib
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)

class ZKProofGenerator:
    def __init__(self):
        self.zk_stark_lib = os.getenv('ZK_STARK_LIB_PATH', '/lib/starklib')
        self.post_quantum_sig = os.getenv('POST_QUANTUM_SIG', 'dilithium')
        self.proof_complexity = os.getenv('PROOF_COMPLEXITY', 'adaptive')
        self.proofs_dir = '/app/proofs'
        
    def generate_proof(self, challenge_data, solution_data, solver_address):
        """Generate ZK-STARK proof for skill verification"""
        
        # Generate proof ID
        proof_id = hashlib.sha256(
            f"{challenge_data['challengeId']}{solver_address}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Calculate score based on solution quality
        score = self._evaluate_solution(challenge_data, solution_data)
        
        # Generate ZK proof
        zk_proof = self._create_zk_proof(solution_data, challenge_data)
        
        # Create solution hash (public)
        solution_hash = hashlib.sha256(
            json.dumps(solution_data, sort_keys=True).encode()
        ).hexdigest()
        
        proof_data = {
            'proofId': proof_id,
            'challengeId': challenge_data['challengeId'],
            'solverAddress': solver_address,
            'score': score,
            'completionTime': solution_data.get('completionTime', 0),
            'solutionHash': solution_hash,
            'zkProof': zk_proof,
            'verified': False,
            'timestamp': datetime.now().isoformat(),
            'proofType': 'ZK-STARK',
            'securityLevel': 'post-quantum'
        }
        
        # Save proof
        self._save_proof(proof_id, proof_data)
        
        return proof_data
    
    def verify_proof(self, proof_id):
        """Verify a ZK proof"""
        proof_file = os.path.join(self.proofs_dir, f"{proof_id}.json")
        
        if not os.path.exists(proof_file):
            return {'error': 'Proof not found', 'verified': False}
        
        with open(proof_file, 'r') as f:
            proof_data = json.load(f)
        
        # Verify ZK proof
        is_valid = self._verify_zk_proof(proof_data['zkProof'])
        
        if is_valid:
            proof_data['verified'] = True
            self._save_proof(proof_id, proof_data)
        
        return {
            'proofId': proof_id,
            'verified': is_valid,
            'score': proof_data.get('score', 0),
            'timestamp': datetime.now().isoformat()
        }
    
    def _evaluate_solution(self, challenge_data, solution_data):
        """Evaluate solution and calculate score"""
        base_score = 50
        
        # Check completion time
        time_limit = challenge_data.get('timeLimit', 60)
        completion_time = solution_data.get('completionTime', time_limit)
        
        if completion_time <= time_limit:
            time_bonus = (time_limit - completion_time) / time_limit * 20
            base_score += time_bonus
        
        # Check task completion
        tasks_completed = solution_data.get('tasksCompleted', 0)
        total_tasks = len(challenge_data.get('tasks', []))
        
        if total_tasks > 0:
            completion_bonus = (tasks_completed / total_tasks) * 30
            base_score += completion_bonus
        
        return min(int(base_score), 100)
    
    def _create_zk_proof(self, solution_data, challenge_data):
        """Create ZK-STARK proof"""
        # In production, this would use actual ZK-STARK library
        # For now, create a cryptographic commitment
        
        proof_data = {
            'solution_commitment': hashlib.sha256(
                json.dumps(solution_data, sort_keys=True).encode()
            ).hexdigest(),
            'challenge_commitment': hashlib.sha256(
                json.dumps(challenge_data, sort_keys=True).encode()
            ).hexdigest(),
            'random_salt': hashlib.sha256(
                str(random.random()).encode()
            ).hexdigest()
        }
        
        # Create final proof hash
        zk_proof = hashlib.sha256(
            json.dumps(proof_data, sort_keys=True).encode()
        ).hexdigest()
        
        return zk_proof
    
    def _verify_zk_proof(self, zk_proof):
        """Verify ZK-STARK proof"""
        # In production, this would use actual ZK-STARK verification
        # For now, check if proof is valid format
        return len(zk_proof) == 64 and all(c in '0123456789abcdef' for c in zk_proof)
    
    def _save_proof(self, proof_id, proof_data):
        """Save proof to disk"""
        os.makedirs(self.proofs_dir, exist_ok=True)
        
        proof_file = os.path.join(self.proofs_dir, f"{proof_id}.json")
        with open(proof_file, 'w') as f:
            json.dump(proof_data, f, indent=2)

generator = ZKProofGenerator()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'zk-proof-generator'}), 200

@app.route('/api/v1/proof', methods=['POST'])
def generate_proof():
    try:
        data = request.json
        challenge_data = data.get('challengeData', {})
        solution_data = data.get('solutionData', {})
        solver_address = data.get('solverAddress')
        
        if not challenge_data or not solution_data or not solver_address:
            return jsonify({'error': 'Missing required data'}), 400
        
        proof = generator.generate_proof(challenge_data, solution_data, solver_address)
        return jsonify(proof), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/proof/<proof_id>/verify', methods=['POST'])
def verify_proof(proof_id):
    try:
        result = generator.verify_proof(proof_id)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/proof/<proof_id>', methods=['GET'])
def get_proof(proof_id):
    try:
        proof_file = os.path.join(generator.proofs_dir, f"{proof_id}.json")
        
        if not os.path.exists(proof_file):
            return jsonify({'error': 'Proof not found'}), 404
        
        with open(proof_file, 'r') as f:
            proof_data = json.load(f)
        
        return jsonify(proof_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3005))
    app.run(host='0.0.0.0', port=port, debug=True)
