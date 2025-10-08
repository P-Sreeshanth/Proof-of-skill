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
import requests

app = Flask(__name__)
CORS(app)

class ChallengeGenerator:
    def __init__(self):
        self.model_path = os.getenv('MODEL_PATH', '/models/codellama-13b')
        self.complexity = os.getenv('CHALLENGE_COMPLEXITY', 'adaptive')
        self.challenges_dir = '/app/challenges'
        # LLM config (optional)
        self.llm_provider = os.getenv('LLM_PROVIDER', '').lower()  # 'gemini' supported
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.gemini_model = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
        
        # Challenge templates by domain
        self.challenge_templates = {
            'sql': [
                {
                    'title': 'SQL Aggregation and Joins',
                    'description': 'Write SQL queries to compute KPIs using joins, grouping, and filtering',
                    'template_type': 'implementation',
                    'base_difficulty': 5,
                    'problem': {
                        'id': 'sql-top-customers',
                        'title': 'Top Customers by Revenue',
                        'statement': (
                            'Given tables customers(id, name), orders(id, customer_id, created_at), '
                            'order_items(id, order_id, product_id, quantity, price), write a SQL query that returns '
                            'the top 3 customers by total revenue in the last 90 days with columns (customer_id, name, revenue).'
                        ),
                        'language': 'sql',
                        'functionName': 'SQL_QUERY',
                        'signature': '/* Write a single SQL query */',
                        'starterCode': 'SELECT c.id AS customer_id, c.name, SUM(oi.quantity * oi.price) AS revenue\nFROM customers c\nJOIN orders o ON o.customer_id = c.id\nJOIN order_items oi ON oi.order_id = o.id\nWHERE o.created_at >= CURRENT_DATE - INTERVAL \'90 days\'\nGROUP BY c.id, c.name\nORDER BY revenue DESC\nLIMIT 3;',
                        'tests': []
                    }
                },
                {
                    'title': 'Window Functions Challenge',
                    'description': 'Use window functions to compute rolling metrics',
                    'template_type': 'implementation',
                    'base_difficulty': 6,
                    'problem': {
                        'id': 'sql-rolling-sum',
                        'title': '7-Day Rolling Revenue',
                        'statement': 'Given sales(date, amount), compute 7-day rolling sum per day.',
                        'language': 'sql',
                        'functionName': 'SQL_QUERY',
                        'signature': '/* Write a single SQL query */',
                        'starterCode': 'SELECT date, SUM(amount) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_7d\nFROM sales;',
                        'tests': []
                    }
                }
            ],
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
        
        # If LLM provider configured, try dynamic generation
        template = None
        llm_error = None
        used_source = 'static'
        if self.llm_provider == 'gemini' and self.gemini_api_key:
            try:
                template = self._llm_generate_template(domain, difficulty, processed_intent)
                if template:
                    used_source = 'gemini'
            except Exception as e:
                llm_error = str(e)
                template = None

        # Fallback to static templates
        if template is None:
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
            # Add a real-world, structured coding problem with starter code and tests
            'problem': template.get('problem') or self._generate_problem_spec(domain, template, difficulty),
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
            'createdAt': datetime.now().isoformat(),
            'source': used_source
        }
        
        # Save challenge
        self._save_challenge(challenge_id, challenge)
        
        if llm_error:
            challenge['llmError'] = llm_error
        return challenge

    def _llm_generate_template(self, domain, difficulty, processed_intent):
        """Use Gemini API to produce a dynamic challenge template with a problem and tests.
        Expects env GEMINI_API_KEY. Uses REST JSON API format.
        """
        # Prompt crafted for structured JSON output
        prompt = (
            "You are a challenge generator. Create a concise, real-world coding challenge as JSON with keys: "
            "title, description, template_type (implementation|debug|optimization), base_difficulty (1-10), "
            "problem { id, title, statement, language (javascript|python), functionName, signature, starterCode, tests: [{inputs, output}] }. "
            f"Domain: {domain}. Difficulty: {difficulty}. Intent: {processed_intent}."
        )

        # Minimal Gemini endpoint (generativelanguage.googleapis.com)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent?key={self.gemini_api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        headers = {"Content-Type": "application/json"}
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        # Extract text and parse JSON (Gemini often returns text; we attempt to find JSON)
        text = ''
        try:
            text = data['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            pass

        # Try to locate a JSON block
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            jtxt = text[start:end+1]
            obj = json.loads(jtxt)
        else:
            # As a fallback, return None so static path is used
            return None

        # Normalize to our template shape
        tmpl = {
            'title': obj.get('title', 'LLM Challenge'),
            'description': obj.get('description', 'Solve the problem.'),
            'template_type': obj.get('template_type', 'implementation'),
            'base_difficulty': int(obj.get('base_difficulty', difficulty)),
        }

        problem = obj.get('problem', {})
        if problem:
            tmpl['problem'] = {
                'id': problem.get('id', 'llm-problem'),
                'title': problem.get('title', tmpl['title']),
                'statement': problem.get('statement', ''),
                'functionName': problem.get('functionName', ''),
                'signature': problem.get('signature', ''),
                'language': problem.get('language', 'javascript'),
                'starterCode': problem.get('starterCode', ''),
                'tests': problem.get('tests', [])
            }

        return tmpl

    def _generate_problem_spec(self, domain, template, difficulty):
        """Return a structured coding problem with starter code and tests.
        We default to a language of JavaScript so it can run in-browser.
        """
        # A small pool of real-world style problems
        problems = [
            {
                'id': 'two-sum',
                'title': 'Two Sum',
                'statement': (
                    'Given an array of integers nums and an integer target, return indices of the '
                    'two numbers such that they add up to target. Assume exactly one solution.'
                ),
                'functionName': 'twoSum',
                'signature': 'function twoSum(nums, target) { /* your code */ }',
                'language': 'javascript',
                'starterCode': (
                    'function twoSum(nums, target) {\n'
                    '  // Return an array [i, j] such that nums[i] + nums[j] === target\n'
                    '  const map = new Map();\n'
                    '  for (let i = 0; i < nums.length; i++) {\n'
                    '    const complement = target - nums[i];\n'
                    '    if (map.has(complement)) return [map.get(complement), i];\n'
                    '    map.set(nums[i], i);\n'
                    '  }\n'
                    '  return [];\n'
                    '}\n'
                ),
                'tests': [
                    {'inputs': [[2,7,11,15], 9], 'output': [0,1]},
                    {'inputs': [[3,2,4], 6], 'output': [1,2]},
                    {'inputs': [[3,3], 6], 'output': [0,1]}
                ]
            },
            {
                'id': 'valid-parentheses',
                'title': 'Valid Parentheses',
                'statement': (
                    'Given a string s containing just the characters "()[]{}", determine if the input string is valid.'
                ),
                'functionName': 'isValid',
                'signature': 'function isValid(s) { /* your code */ }',
                'language': 'javascript',
                'starterCode': (
                    'function isValid(s) {\n'
                    '  const stack = [];\n'
                    '  const pairs = { \')\': \'(\', \'}\': \'{\', \'\']\': \'[\' };\n'
                    '  for (const ch of s) {\n'
                    '    if (ch === \'(\' || ch === \'{\' || ch === \'[\') stack.push(ch);\n'
                    '    else if (pairs[ch]) {\n'
                    '      if (stack.pop() !== pairs[ch]) return false;\n'
                    '    }\n'
                    '  }\n'
                    '  return stack.length === 0;\n'
                    '}\n'
                ),
                'tests': [
                    {'inputs': ['()'], 'output': True},
                    {'inputs': ['()[]{}'], 'output': True},
                    {'inputs': ['(]'], 'output': False}
                ]
            }
        ]

        # Bias problem choice by difficulty; otherwise pick randomly
        problem = random.choice(problems)

        return {
            'id': problem['id'],
            'title': problem['title'],
            'statement': problem['statement'],
            'functionName': problem['functionName'],
            'signature': problem['signature'],
            'language': problem['language'],
            'starterCode': problem['starterCode'],
            'tests': problem['tests']
        }
    
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
