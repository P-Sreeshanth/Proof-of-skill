"""
Challenge Completion Logger Service
Logs challenge completions for analytics and verification
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

class CompletionLogger:
    def __init__(self):
        self.logs_dir = '/app/logs'
        os.makedirs(self.logs_dir, exist_ok=True)
        
    def log_completion(self, completion_data):
        """Log a challenge completion"""
        log_id = f"{completion_data.get('challengeId')}_{completion_data.get('solverAddress')}_{int(datetime.now().timestamp())}"
        
        log_entry = {
            'logId': log_id,
            'timestamp': datetime.now().isoformat(),
            **completion_data
        }
        
        # Save to file
        log_file = os.path.join(self.logs_dir, f"{log_id}.json")
        with open(log_file, 'w') as f:
            json.dump(log_entry, f, indent=2)
        
        # Also append to daily log
        daily_log = os.path.join(self.logs_dir, f"completions_{datetime.now().strftime('%Y%m%d')}.jsonl")
        with open(daily_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        return log_id

logger = CompletionLogger()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'challenge-completion-logger'}), 200

@app.route('/api/v1/log', methods=['POST'])
def log_completion():
    try:
        data = request.json
        log_id = logger.log_completion(data)
        return jsonify({'logId': log_id, 'status': 'logged'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/logs', methods=['GET'])
def get_logs():
    try:
        date = request.args.get('date', datetime.now().strftime('%Y%m%d'))
        daily_log = os.path.join(logger.logs_dir, f"completions_{date}.jsonl")
        
        if not os.path.exists(daily_log):
            return jsonify({'logs': []}), 200
        
        logs = []
        with open(daily_log, 'r') as f:
            for line in f:
                logs.append(json.loads(line))
        
        return jsonify({'logs': logs}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3011))
    app.run(host='0.0.0.0', port=port, debug=True)
