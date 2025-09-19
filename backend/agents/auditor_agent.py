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
    print("[AuditAgent] Reasoning: Evaluating policies...")

    audit_report = {}
    kong_data_list = state.get("kong_data", [])

    policy_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "knowledge_base", "api_policies"))

    for kong_data in kong_data_list:
        service_name = kong_data.get("service_name", "unknown_service")
        attached_plugins = kong_data.get("service_plugins", [])

        for filename in os.listdir(policy_dir):
            if filename.endswith(".txt"):
                with open(os.path.join(policy_dir, filename), 'r') as f:
                    policy_text = f.read()

                prompt = f"""You are an autonomous security auditor agent.
                            Your task is to evaluate Kong API Gateway service configurations against enterprise security policies and generate an audit report.
                            ### Inputs:
                            - **Policy Text**:
                            ```
                            {policy_text}
                            ```
                            - **Kong Service Data**:
                                "attached_plugins": {json.dumps(attached_plugins, indent=2)} 

                            ### Instructions:
                            1. Read the policy carefully and identify which plugins are **mandatory** for compliance.
                            2. Compare the plugins attached to the given Kong service against the mandatory plugins.
                            3. For each mandatory plugin:
                                - Check if it is present.
                                - Mark its compliance status as `"used"` or `"missing"`.
                            ### Output Format:
                            Return a JSON object with the following structure:
                            {{
                                "service_name": "{service_name}",
                                "policy_file": "{filename}",
                                "compliance": {{
                                    "plugin_name_1": "used/missing",
                                    "plugin_name_2": "used/missing",
                                    ...
                                }},
                                "summary": "Summary of compliance status."
                            }}
                            """

                print("PROMPT - ", prompt)
                response = requests.post('https://kong-30caf13d76ushgpgq.kongcloud.dev/api/v1/azure-test', json={"messages": [{"role": "user", "content": prompt}]})
                ##response = {"json": lambda: {"response": "Mocked response for testing purposes"}} # Mocked response for testing purposes

                key = f"{service_name}:{filename}"
                audit_report[key] = response.json() ##.get('response', 'No response received')

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
    remediation_plan = {}
    for key, value in state["audit_report"].items():
        remediation_plan[key] = f"Remediation for {key}: {value}"
    state["remediation_plan"] = remediation_plan
    return state

def plan_remediation(state: dict) -> dict:
    print("[RemediationAgent] Planning: Structuring remediation steps...")
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