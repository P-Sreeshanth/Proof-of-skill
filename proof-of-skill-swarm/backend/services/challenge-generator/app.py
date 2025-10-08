"""
Challenge Generator Service
Generates personalized skill challenges based on processed intent
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

class ChallengeGenerator:
    def __init__(self):
        self.model_path = os.getenv('MODEL_PATH', '/models/codellama-13b')
        self.complexity = os.getenv('CHALLENGE_COMPLEXITY', 'adaptive')
        self.challenges_dir = '/app/challenges'
        
        # Challenge templates by domain
        self.challenge_templates = {
            'react': [
                {
                    'title': 'React Component Debugging',
                    'description': 'Debug a React component that has rendering issues',
                    'template_type': 'debug',
                    'base_difficulty': 5
                },
                {
                    'title': 'State Management Challenge',
                    'description': 'Implement proper state management for a complex React app',
                    'template_type': 'implementation',
                    'base_difficulty': 7
                },
                {
                    'title': 'Performance Optimization',
                    'description': 'Optimize a React component for better performance',
                    'template_type': 'optimization',
                    'base_difficulty': 8
                }
            ],
            'python': [
                {
                    'title': 'Algorithm Implementation',
                    'description': 'Implement an efficient algorithm to solve a problem',
                    'template_type': 'implementation',
                    'base_difficulty': 6
                },
                {
                    'title': 'Data Structure Design',
                    'description': 'Design and implement a custom data structure',
                    'template_type': 'design',
                    'base_difficulty': 7
                },
                {
                    'title': 'Code Refactoring',
                    'description': 'Refactor legacy Python code to modern standards',
                    'template_type': 'refactoring',
                    'base_difficulty': 5
                }
            ],
            'debug': [
                {
                    'title': 'Bug Hunt Challenge',
                    'description': 'Find and fix multiple bugs in a codebase',
                    'template_type': 'debug',
                    'base_difficulty': 6
                },
                {
                    'title': 'Performance Bottleneck',
                    'description': 'Identify and resolve performance issues',
                    'template_type': 'optimization',
                    'base_difficulty': 8
                }
            ],
            'general': [
                {
                    'title': 'Problem Solving Challenge',
                    'description': 'Solve a complex technical problem',
                    'template_type': 'implementation',
                    'base_difficulty': 5
                }
            ]
        }
        
    def generate_challenge(self, processed_intent, personalization=None):
        """Generate a personalized challenge based on processed intent"""
        
        # Extract parameters from processed intent
        domain = processed_intent.get('domain', 'general')
        difficulty = processed_intent.get('difficulty', 5)
        
        # Select appropriate challenge template
        template = self._select_template(domain, difficulty)
        
        # Generate unique challenge ID
        challenge_id = hashlib.sha256(
            f"{domain}{difficulty}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Create challenge
        challenge = {
            'challengeId': challenge_id,
            'title': template['title'],
            'description': template['description'],
            'type': template['template_type'],
            'domain': domain,
            'difficulty': difficulty,
            'timeLimit': self._calculate_time_limit(difficulty),
            'reward': self._calculate_reward(difficulty),
            'tasks': self._generate_tasks(template, difficulty),
            'evaluationCriteria': [
                {
                    'criterion': 'correctness',
                    'weight': 0.4,
                    'description': 'Solution correctness and completeness'
                },
                {
                    'criterion': 'efficiency',
                    'weight': 0.3,
                    'description': 'Code efficiency and performance'
                },
                {
                    'criterion': 'best_practices',
                    'weight': 0.3,
                    'description': 'Following best practices and coding standards'
                }
            ],
            'startTime': datetime.now().isoformat(),
            'createdAt': datetime.now().isoformat()
        }
        
        # Save challenge
        self._save_challenge(challenge_id, challenge)
        
        return challenge
    
    def _select_template(self, domain, difficulty):
        """Select appropriate challenge template"""
        templates = self.challenge_templates.get(domain, self.challenge_templates['general'])
        
        # Filter templates by difficulty range
        suitable_templates = [
            t for t in templates 
            if abs(t['base_difficulty'] - difficulty) <= 2
        ]
        
        if not suitable_templates:
            suitable_templates = templates
        
        return random.choice(suitable_templates)
    
    def _calculate_time_limit(self, difficulty):
        """Calculate time limit based on difficulty (in minutes)"""
        base_time = 30
        return base_time + (difficulty * 10)
    
    def _calculate_reward(self, difficulty):
        """Calculate reward tokens based on difficulty"""
        base_reward = 100
        return base_reward * difficulty
    
    def _generate_tasks(self, template, difficulty):
        """Generate specific tasks for the challenge"""
        task_count = min(3 + (difficulty // 3), 7)
        
        task_types = {
            'debug': [
                'Identify the root cause of the issue',
                'Fix the identified bug',
                'Add tests to prevent regression',
                'Document the fix'
            ],
            'implementation': [
                'Design the solution architecture',
                'Implement core functionality',
                'Add error handling',
                'Write unit tests',
                'Optimize for performance'
            ],
            'optimization': [
                'Profile the current implementation',
                'Identify bottlenecks',
                'Implement optimizations',
                'Measure performance improvements',
                'Document optimization strategies'
            ],
            'design': [
                'Define requirements',
                'Design the architecture',
                'Implement the design',
                'Write documentation',
                'Create usage examples'
            ],
            'refactoring': [
                'Analyze existing code',
                'Identify improvement areas',
                'Refactor code structure',
                'Ensure backward compatibility',
                'Update tests'
            ]
        }
        
        template_type = template['template_type']
        available_tasks = task_types.get(template_type, task_types['implementation'])
        
        selected_tasks = random.sample(available_tasks, min(task_count, len(available_tasks)))
        
        return [
            {
                'id': i + 1,
                'description': task,
                'required': i < 3,  # First 3 tasks are required
                'points': 100 // task_count
            }
            for i, task in enumerate(selected_tasks)
        ]
    
    def _save_challenge(self, challenge_id, challenge):
        """Save challenge to disk"""
        os.makedirs(self.challenges_dir, exist_ok=True)
        
        challenge_file = os.path.join(self.challenges_dir, f"{challenge_id}.json")
        with open(challenge_file, 'w') as f:
            json.dump(challenge, f, indent=2)

generator = ChallengeGenerator()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'challenge-generator'}), 200

@app.route('/api/v1/challenge', methods=['POST'])
def generate_challenge():
    try:
        data = request.json
        processed_intent = data.get('processedIntent', {})
        personalization = data.get('personalization', {})
        
        if not processed_intent:
            return jsonify({'error': 'Processed intent required'}), 400
        
        challenge = generator.generate_challenge(processed_intent, personalization)
        return jsonify(challenge), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/challenge/<challenge_id>', methods=['GET'])
def get_challenge(challenge_id):
    try:
        challenge_file = os.path.join(generator.challenges_dir, f"{challenge_id}.json")
        
        if not os.path.exists(challenge_file):
            return jsonify({'error': 'Challenge not found'}), 404
        
        with open(challenge_file, 'r') as f:
            challenge = json.load(f)
        
        return jsonify(challenge), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3002))
    app.run(host='0.0.0.0', port=port, debug=True)
