from flask import Flask, request, jsonify
from auditor_agent import audit_state, rem_state, audit_app, rem_app
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/v1/ai-agents/audit', methods=['POST'])
def run_audit():
    input_data = request.json or {}
    try:
        result = audit_app.invoke(input_data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/ai-agents/remediate', methods=['POST'])
def run_remediation():
    input_data = request.json or {}
    if "audit_report" not in input_data:
        return jsonify({"error": "Missing 'audit_report' in request body"}), 400
    try:
        result = rem_app.invoke({"audit_report": input_data["audit_report"]})
        remediation_plan = result.get("remediation_plan", [])       
        return jsonify(remediation_plan), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
