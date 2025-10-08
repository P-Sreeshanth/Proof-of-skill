"""
Python Runner Service (Sandboxed - demo level)
Runs user-submitted Python code against provided tests with a strict timeout.
This is a minimal demo and should not be used for untrusted code in production.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import tempfile
import os
import json

app = Flask(__name__)
CORS(app)

TIMEOUT_SECONDS = 3

@app.get('/health')
def health():
    return jsonify({"service": "python-runner", "status": "healthy"}), 200


@app.post('/run-tests')
def run_tests():
    try:
        data = request.get_json(force=True)
        code = data.get('code', '')
        tests = data.get('tests', [])
        function_name = data.get('functionName')

        if not code or not function_name:
            return jsonify({"error": "code and functionName required"}), 400

        # crude import guard (demo-only)
        forbidden = ['import os', 'import sys', 'subprocess', 'open(', 'socket', 'shutil', 'pathlib', 'pickle']
        for token in forbidden:
            if token in code:
                return jsonify({"error": f"Forbidden token detected: {token}"}), 400

        with tempfile.TemporaryDirectory() as tmp:
            test_file = os.path.join(tmp, 'runner.py')
            test_body = [
                'import json',
                '',
                code,
                '',
                'def _run_tests():',
                f'    fn = globals().get("{function_name}")',
                '    if fn is None:',
                '        return {"error": "function not found"}',
                f'    tests = {json.dumps(tests)}',
                '    results = {"passed": 0, "total": len(tests), "logs": []}',
                '    for idx, t in enumerate(tests, start=1):',
                '        inputs = t.get("inputs")',
                '        expected = t.get("output")',
                '        try:',
                '            if isinstance(inputs, list):',
                '                actual = fn(*inputs)',
                '            else:',
                '                actual = fn(inputs)',
                '        except Exception as e:',
                '            results["logs"].append(f"Test #{idx}: error: {str(e)}")',
                '            continue',
                '        ok = (actual == expected)',
                '        if ok:',
                '            results["passed"] += 1',
                '            results["logs"].append(f"Test #{idx}: passed")',
                '        else:',
                '            results["logs"].append(f"Test #{idx}: expected {expected}, got {actual}")',
                '    return results',
                '',
                'if __name__ == "__main__":',
                '    print(json.dumps(_run_tests()))'
            ]

            with open(test_file, 'w') as f:
                f.write("\n".join(test_body))

            proc = subprocess.run(
                ['python', test_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=TIMEOUT_SECONDS
            )

            if proc.returncode != 0:
                return jsonify({
                    "passed": 0,
                    "total": len(tests),
                    "logs": ["Runner error", proc.stderr.strip()]
                }), 200

            try:
                result = json.loads(proc.stdout.strip())
            except Exception:
                result = {"passed": 0, "total": len(tests), "logs": ["Invalid runner output", proc.stdout]}

            return jsonify(result), 200

    except subprocess.TimeoutExpired:
        return jsonify({"passed": 0, "total": len(request.json.get('tests', [])), "logs": ["Timeout"]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 3012))
    app.run(host='0.0.0.0', port=port, debug=True)


