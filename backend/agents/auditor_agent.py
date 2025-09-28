"""
===============================================================================
 File Name   : auditor_agent.py
 Description : Autonomous Security Auditor Agent file containing two agents 
               Audit and Remediate for Kong Konnect configurations.
 Author      : Sachin Ghumbre
 Created On  : 2025-09-26
 Version     : v1.0.0
 License     : Proprietary
 Tags        : kong, konnect, genai, audit, langgraph, agentic ai
===============================================================================
"""

import os
import json
import requests
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from typing import Dict, Any, List

# Load environment variables
load_dotenv()

# Constants
KONG_ADMIN_API = os.getenv("KONG_ADMIN_API")
KONG_ADMIN_TOKEN = os.getenv("KONG_ADMIN_TOKEN")
KONG_AI_PROXY_HOSTNAME = os.getenv("KONG_AI_PROXY_HOSTNAME")
KONG_API_KEY = os.getenv("KONG_API_KEY")


# === Audit Agent Nodes ===

def fetch_kong_data(endpoint: str) -> List[Dict[str, Any]]:
    headers = {"kong-admin-token": KONG_ADMIN_TOKEN}
    try:
        response = requests.get(f"{KONG_ADMIN_API}/{endpoint}", headers=headers, verify=False)
        response.raise_for_status()
        return response.json().get("data", [])
    except Exception as e:
        print(f"[Error] Failed to fetch {endpoint}: {e}")
        return []


def perceive_kong(state: Dict[str, Any]) -> Dict[str, Any]:
    print("[AuditAgent] Perception: Fetching Kong configs...")

    services = fetch_kong_data("services")
    plugins = fetch_kong_data("plugins")

    service_plugins_map = {}

    for plugin in plugins:
        service = plugin.get("service")
        if service:
            service_id = service["id"]
            service_plugins_map.setdefault(service_id, []).append(plugin["name"])

    kong_data = []

    for service in services:
        service_id = service["id"]
        service_name = service["name"]
        plugin_names = service_plugins_map.get(service_id, [])

        routes = fetch_kong_data(f"services/{service_id}/routes")
        for route in routes:
            route_id = route["id"]
            route_plugins = fetch_kong_data(f"routes/{route_id}/plugins")
            plugin_names.extend([plugin["name"] for plugin in route_plugins])

        kong_data.append({
            "service_name": service_name,
            "service_id": service_id,
            "service_plugins": list(set(plugin_names))
        })

    state["kong_data"] = kong_data

    with open("filtered_kong_data.json", "w") as f:
        json.dump(kong_data, f, indent=2)

    return state


def reason_audit(state: Dict[str, Any]) -> Dict[str, Any]:
    print("[AuditAgent] Reasoning: Evaluating policy compliance...")

    audit_report = {}
    kong_data_list = state.get("kong_data", [])

    for kong_data in kong_data_list:
        service_name = kong_data.get("service_name", "unknown_service")
        service_plugins = kong_data.get("service_plugins", [])

        print(f"Auditing service: {service_name} with plugins: {service_plugins}")

        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"I have fetched Kong service and its plugin configurations from Kong gateway. "
                        f"The service name is {service_name} and plugins are {service_plugins}"
                    )
                }
            ]
        }

        try:
            response = requests.post(
                f"{KONG_AI_PROXY_HOSTNAME}/api/v1/agents/auditor",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": KONG_API_KEY
                },
                json=payload
            )
            response.raise_for_status()
            audit_report_key = f"{service_name}:policy:{service_name}"
            audit_report[audit_report_key] = response.json()
        except Exception as e:
            audit_report[audit_report_key] = {"error": f"Failed to parse response: {str(e)}"}

    state["audit_report"] = audit_report
    return state


def plan_audit(state: Dict[str, Any]) -> Dict[str, Any]:
    print("[AuditAgent] Planning: Finalizing audit report...")
    return state


def action_audit(state: Dict[str, Any]) -> Dict[str, Any]:
    print("[AuditAgent] Action: Saving audit report...")
    with open("langgraph_audit_report.json", "w") as f:
        json.dump(state.get("audit_report", {}), f, indent=2)
    return state


# === Remediation Agent Nodes ===

def perceive_issues(state: Dict[str, Any]) -> Dict[str, Any]:
    print("[RemediationAgent] Perception: Reading audit report...")
    return state


def reason_remediation(state: Dict[str, Any]) -> Dict[str, Any]:
    print("[RemediationAgent] Reasoning: Generating remediation plan...")

    severity_map = {
        "Authentication": "Critical",
        "Rate Limiting": "High",
        "Request Size Limiting": "Medium",
        "Logging": "Medium",
        "IP Restriction": "Low",
        "Request Transformation": "Low"
    }

    remediation_input = []

    for service_key, service_data in state.get("audit_report", {}).items():
        service_name = service_data.get("serviceName", service_key)
        for policy in service_data.get("policies", []):
            comply = policy.get("comply", policy.get("comply_status", True))
            if not comply:
                policy_name = policy.get("policy_name", "Unknown Policy")
                severity = severity_map.get(policy_name.split()[0], "Medium")
                remediation_input.append({
                    "serviceName": service_name,
                    "policyName": policy_name,
                    "details": policy.get("details", "Non-compliance detected."),
                    "missingPlugins": policy.get("missing_plugins", []),
                    "severity": severity
                })

    remediation_input_json = json.dumps(remediation_input, indent=2)

    prompt = (
        "You are an API security expert. Based on the following audit report, "
        "generate a remediation plan in JSON format. "
        "Each item should include: serviceName, policyName, issue, missingPlugin, "
        "recommendedAction, severity, owner, estimatedEffort, impact, "
        "and securityStandardReference (e.g., OWASP, GDPR, NIST, ISO 27001, etc.). "
        "Ensure the output is a valid JSON array without extra text.\n\n"
        f"Audit Report:\n{remediation_input_json}"
    )

    try:
        response = requests.post(
            f"{KONG_AI_PROXY_HOSTNAME}/api/v1/agents/remediate",
            headers={
                "Content-Type": "application/json",
                "x-api-key": KONG_API_KEY
            },
            json={"messages": [{"role": "user", "content": prompt}]}
        )
        response.raise_for_status()
        state["remediation_plan"] = response.json()
    except Exception as e:
        print(f"Remediation API call failed: {e}")
        state["remediation_plan"] = []

    return state


def plan_remediation(state: Dict[str, Any]) -> Dict[str, Any]:
    print("[RemediationAgent] Planning: Structuring remediation steps...")
    return state


def action_remediation(state: Dict[str, Any]) -> Dict[str, Any]:
    print("[RemediationAgent] Action: Saving remediation plan...")
    with open("langgraph_remediation_plan.json", "w") as f:
        json.dump(state.get("remediation_plan", []), f, indent=2)
    return state


# === Build and Run Audit Agent Graph ===

audit_graph = StateGraph(dict)
audit_graph.add_node("perceive", perceive_kong)
audit_graph.add_node("reason", reason_audit)
audit_graph.add_node("plan", plan_audit)
audit_graph.add_node("act", action_audit)
audit_graph.set_entry_point("perceive")
audit_graph.add_edge("perceive", "reason")
audit_graph.add_edge("reason", "plan")
audit_graph.add_edge("plan", "act")
audit_app = audit_graph.compile()

audit_state = audit_app.invoke({})

# === Build and Run Remediation Agent Graph ===

rem_graph = StateGraph(dict)
rem_graph.add_node("perceive", perceive_issues)
rem_graph.add_node("reason", reason_remediation)
rem_graph.add_node("plan", plan_remediation)
rem_graph.add_node("act", action_remediation)
rem_graph.set_entry_point("perceive")
rem_graph.add_edge("perceive", "reason")
rem_graph.add_edge("reason", "plan")
rem_graph.add_edge("plan", "act")
rem_app = rem_graph.compile()

rem_state = rem_app.invoke({"audit_report": audit_state["audit_report"]})

print("✅ Audit and remediation completed successfully.")