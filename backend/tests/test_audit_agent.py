
import pytest
from langgraph_agents import AuditState, perceive_kong, reason_audit, plan_audit, action_audit

@pytest.fixture
def audit_state():
    return AuditState()

def test_perceive_kong(audit_state):
    state = perceive_kong(audit_state)
    assert 'services' in state.kong_data

def test_reason_audit(audit_state):
    audit_state.kong_data = {'services': [], 'routes': [], 'plugins': [], 'consumers': []}
    state = reason_audit(audit_state)
    assert isinstance(state.audit_report, dict)

def test_plan_audit(audit_state):
    audit_state.audit_report = {'test': 'result'}
    state = plan_audit(audit_state)
    assert 'test' in state.audit_report

def test_action_audit(audit_state):
    audit_state.audit_report = {'test': 'result'}
    state = action_audit(audit_state)
    assert os.path.exists("langgraph_audit_report.json")
