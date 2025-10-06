"""
===============================================================================
 File Name   : init_auditor.py
 Description : Autonomous Security Auditor Agent Init file containing two Flask
               routes for two agents Audit and Remediate.
 Author      : Sachin Ghumbre
 Created On  : 2025-09-26
 Version     : v1.0.0
 License     : Proprietary
 Tags        : kong, konnect, genai, audit, langgraph, agentic ai
===============================================================================
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from auditor_agent import audit_app, rem_app
import json

# Constants
AUDIT_ROUTE = '/api/v1/ai-agents/audit'
REMEDIATE_ROUTE = '/api/v1/ai-agents/remediate'

# Flask App Initialization
app = Flask(__name__)
CORS(app)


@app.route(AUDIT_ROUTE, methods=['POST'])
def run_audit() -> tuple:
    """Invoke the Audit Agent with input data."""
    input_data = request.get_json(force=True) or {}
    ##print("input_Data: ", input_data)
    try:
        result = audit_app.invoke(input_data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route(REMEDIATE_ROUTE, methods=['POST'])
def run_remediation() -> tuple:
    """Invoke the Remediation Agent with audit report."""
    input_data = request.get_json(force=True) or {}
    audit_report = input_data.get("audit_report")

    if not audit_report:
        return jsonify({"error": "Missing 'audit_report' in request body"}), 400

    try:
        result = rem_app.invoke({"audit_report": audit_report})
        remediation_plan = result.get("remediation_plan", [])
        return jsonify(remediation_plan), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)