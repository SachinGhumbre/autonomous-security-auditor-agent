from fileinput import filename
from click import prompt
from langgraph.graph import StateGraph
import os
from dotenv import load_dotenv
import requests
import redis
import json

# Load environment variables
load_dotenv()
KONG_ADMIN_API = os.getenv("KONG_ADMIN_API")
KONG_ADMIN_TOKEN = os.getenv("KONG_ADMIN_TOKEN")

# === Audit Agent Nodes ===

def perceive_kong(state: dict) -> dict:
    print("[AuditAgent] Perception: Fetching Kong configs...")

    headers = {"kong-admin-token": KONG_ADMIN_TOKEN}

    # Fetch services, routes, and plugins
    services = requests.get(f"{KONG_ADMIN_API}/services", headers=headers, verify=False).json().get("data", [])
    ##routes = requests.get(f"{KONG_ADMIN_API}/routes", headers=headers, verify=False).json().get("data", [])
    plugins = requests.get(f"{KONG_ADMIN_API}/plugins", headers=headers, verify=False).json().get("data", [])

    # Organize plugins by service and route
    service_plugins = {}
    ##route_plugins = {}

    for plugin in plugins:
        if plugin.get("service") is not None:
            service_id = plugin["service"]["id"]
            service_plugins.setdefault(service_id, []).append(plugin["name"]) # Store plugin names directly

    # Build structured kong_data
    kong_data = []
    for service in services:
        service_id = service["id"]        
        service_name = service["name"]
        service_plugins_list = service_plugins.get(service_id, [])
        
        # Fetch routes for the current service
        routes = requests.get(f"{KONG_ADMIN_API}/services/{service_id}/routes", headers=headers, verify=False).json().get("data", [])
        
        # Fetch plugins for each route of the current service
        for route in routes:
            route_id = route["id"]
            route_plugins = requests.get(f"{KONG_ADMIN_API}/routes/{route_id}/plugins", headers=headers, verify=False).json().get("data", [])
            for plugin in route_plugins:
                service_plugins_list.append(plugin["name"])

        # Ensure unique plugin names
        service_plugins_list = list(set(service_plugins_list))

        kong_data.append({
            "service_name": service_name,
            "service_id": service_id,
            "service_plugins": service_plugins.get(service_id, []) # List of plugin names
        })

    state["kong_data"] = kong_data

    # Optional: Save to file for debugging
    with open("filtered_kong_data.json", "w") as f:
        json.dump(kong_data, f, indent=2)

    return state

def reason_audit(state: dict) -> dict:
    import json
    import requests

    print("[AuditAgent] Reasoning: Sending Kong service data to Azure API for policy compliance evaluation...")

    audit_report = {}
    kong_data_list = state.get("kong_data", [])
    KONG_AI_PROXY_HOSTNAME = os.getenv("KONG_AI_PROXY_HOSTNAME")

    for kong_data in kong_data_list:
        service_name = kong_data.get("service_name", "unknown_service")
        service_plugins = kong_data.get("service_plugins", [])
        print(f"Auditing service: {service_name} with plugins: {service_plugins}")
        
        # Call the Kong AI Proxy API
        response = requests.post(
            f'{KONG_AI_PROXY_HOSTNAME}/api/v1/agents/auditor', headers={"Content-Type": "application/json","x-api-key": os.getenv("KONG_API_KEY")},    
            json={
                    "messages": [
                        {
                            "role": "user",
                            "content": f" I have fetched Kong service and its plugin configurations from Kong gateway. The service name is {service_name} and plugins are {service_plugins}"
                        }
                    ]
                }
        )
        audit_report_key = f"{service_name}:policy:{service_name}"
        try:
            audit_report[audit_report_key] = response.json()
        except Exception:
            audit_report[audit_report_key] = {"error": "Failed to parse response"}

    state["audit_report"] = audit_report
    return state

def plan_audit(state: dict) -> dict:
    print("[AuditAgent] Planning: Finalizing audit report...")
    return state

def action_audit(state: dict) -> dict:
    print("[AuditAgent] Action: Saving audit report...")
    with open("langgraph_audit_report.json", "w") as f:
        json.dump(state["audit_report"], f, indent=2)
    return state

# === Remediation Agent Nodes ===

def perceive_issues(state: dict) -> dict:
    print("[RemediationAgent] Perception: Reading audit report...")
    return state

def reason_remediation(state: dict) -> dict:
    print("[RemediationAgent] Reasoning: Generating remediation plan...")
    # Prepare audit context for LLM
    KONG_AI_PROXY_HOSTNAME = os.getenv("KONG_AI_PROXY_HOSTNAME")
    remediation_input = []

    severity_map = {
        "Authentication": "Critical",
        "Rate Limiting": "High",
        "Request Size Limiting": "Medium",
        "Logging": "Medium",
        "IP Restriction": "Low",
        "Request Transformation": "Low"
    }

    for service_key, service_data in state["audit_report"].items():
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

    # Construct the prompt
    prompt = (
            "You are an API security expert. Based on the following audit report, "
            "generate a remediation plan in JSON format. "
            "Each item should include: serviceName, policyName, issue, missingPlugin, "
            "recommendedAction, severity, owner, estimatedEffort, impact, "
            "and securityStandardReference (e.g., OWASP, GDPR, NIST, ISO 27001, etc.)."
            "Please ensure the output is a valid JSON array and does not contain any extra text or explanation.\n\n"
            f"Audit Report:\n{remediation_input_json}"
        )

    # Call the Kong AI Proxy API
    response = requests.post(
            f'{KONG_AI_PROXY_HOSTNAME}/api/v1/agents/remediate',
            headers={
                "Content-Type": "application/json",
                "x-api-key": os.getenv("KONG_API_KEY")
            },
            json={
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
    )


    # Safe response handling
    if response.status_code == 200:
        try:
            remediation_plan = response.json()
            print("LLM API response:", json.dumps(remediation_plan, indent=2))
            state["remediation_plan"] = remediation_plan
        except ValueError:
            print("Error: Response is not valid JSON.")
            print("Raw response:", response.text)
            state["remediation_plan"] = []
    else:
        print(f"LLM API call failed with status {response.status_code}")
        print("Raw response:", response.text)
        state["remediation_plan"] = []

    ##state["remediation_plan"] = remediation_plan 
    return state

def plan_remediation(state: dict) -> dict:
    print("[RemediationAgent] Planning: Structuring remediation steps...")
    # Future enhancement: group by service, prioritize by severity
    return state

def action_remediation(state: dict) -> dict:
    print("[RemediationAgent] Action: Saving remediation plan...")
    with open("langgraph_remediation_plan.json", "w") as f:
        json.dump(state["remediation_plan"], f, indent=2)
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