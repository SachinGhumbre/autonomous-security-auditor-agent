
import pytest
from langgraph_agents import RemediationState, perceive_issues, reason_remediation, plan_remediation, action_remediation

@pytest.fixture
def rem_state():
    return RemediationState({'test': 'issue'})

def test_perceive_issues(rem_state):
    state = perceive_issues(rem_state)
    assert 'test' in state.audit_report

def test_reason_remediation(rem_state):
    state = reason_remediation(rem_state)
    assert 'test' in state.remediation_plan

def test_plan_remediation(rem_state):
    rem_state.remediation_plan = {'test': 'fix'}
    state = plan_remediation(rem_state)
    assert 'test' in state.remediation_plan

def test_action_remediation(rem_state):
    rem_state.remediation_plan = {'test': 'fix'}
    state = action_remediation(rem_state)
    assert os.path.exists("langgraph_remediation_plan.json")
