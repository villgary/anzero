import pytest
from app.countermeasure.decision.decision_tree import DecisionTree, ResponseLevel
from app.countermeasure.decision.approval import ApprovalWorkflow, ApprovalStatus


@pytest.fixture
def tree():
    return DecisionTree()


@pytest.fixture
def workflow():
    return ApprovalWorkflow()


def test_green_automatic_execution(tree):
    decision = tree.decide(0.45, "scan")
    assert decision.level == ResponseLevel.GREEN
    assert decision.approval_required is False
    assert decision.approver is None
    assert decision.countermeasures == ["C-01", "C-04"]


def test_red_requires_ciso_approval(tree):
    decision = tree.decide(0.92, "rce")
    assert decision.level == ResponseLevel.RED
    assert decision.approval_required is True
    assert decision.approver == "ciso"
    assert decision.countermeasures == ["C-18", "C-22", "C-24"]


def test_observe_level(tree):
    decision = tree.decide(0.15, "scan")
    assert decision.level == ResponseLevel.GREEN  # Using GREEN as placeholder
    assert decision.approval_required is False
    assert decision.countermeasures == []


def test_yellow_requires_soc_approval(tree):
    decision = tree.decide(0.70, "scan")
    assert decision.level == ResponseLevel.YELLOW
    assert decision.approval_required is True
    assert decision.approver == "soc"
    assert decision.countermeasures == ["C-13", "C-25"]


def test_boundary_30_observe(tree):
    decision = tree.decide(0.30, "scan")
    assert decision.level == ResponseLevel.GREEN
    assert decision.approval_required is False
    assert decision.countermeasures == ["C-01", "C-04"]


def test_boundary_60_green(tree):
    decision = tree.decide(0.59, "scan")
    assert decision.level == ResponseLevel.GREEN
    assert decision.approval_required is False
    assert decision.countermeasures == ["C-01", "C-04"]


def test_boundary_85_yellow(tree):
    decision = tree.decide(0.85, "scan")
    assert decision.level == ResponseLevel.RED


def test_invalid_confidence_negative(tree):
    with pytest.raises(ValueError):
        tree.decide(-0.1, "scan")


def test_invalid_confidence_over_1(tree):
    with pytest.raises(ValueError):
        tree.decide(1.1, "scan")


# ApprovalWorkflow tests

def test_request_approval_returns_id(workflow, tree):
    decision = tree.decide(0.70, "scan")  # YELLOW level
    approval_id = workflow.request_approval(decision, "analyst1")
    assert approval_id is not None
    assert len(approval_id) == 8


def test_request_approval_no_approval_required(workflow, tree):
    decision = tree.decide(0.45, "scan")  # GREEN level, no approval
    with pytest.raises(ValueError):
        workflow.request_approval(decision, "analyst1")


def test_approve_success(workflow, tree):
    decision = tree.decide(0.70, "scan")  # YELLOW level
    approval_id = workflow.request_approval(decision, "analyst1")
    result = workflow.approve(approval_id, "soc")
    assert result is True


def test_approve_wrong_approver(workflow, tree):
    decision = tree.decide(0.70, "scan")  # YELLOW level
    approval_id = workflow.request_approval(decision, "analyst1")
    result = workflow.approve(approval_id, "ciso")  # Wrong role
    assert result is False


def test_reject_success(workflow, tree):
    decision = tree.decide(0.70, "scan")  # YELLOW level
    approval_id = workflow.request_approval(decision, "analyst1")
    result = workflow.reject(approval_id, "soc", "Not enough evidence")
    assert result is True


def test_reject_wrong_approver(workflow, tree):
    decision = tree.decide(0.70, "scan")  # YELLOW level
    approval_id = workflow.request_approval(decision, "analyst1")
    result = workflow.reject(approval_id, "ciso", "Too risky")
    assert result is False


def test_get_status_pending(workflow, tree):
    decision = tree.decide(0.70, "scan")  # YELLOW level
    approval_id = workflow.request_approval(decision, "analyst1")
    status = workflow.get_status(approval_id)
    assert status["approval_id"] == approval_id
    assert status["status"] == "pending"
    assert status["requester"] == "analyst1"
    assert status["approver"] is None


def test_get_status_after_approval(workflow, tree):
    decision = tree.decide(0.70, "scan")
    approval_id = workflow.request_approval(decision, "analyst1")
    workflow.approve(approval_id, "soc")
    status = workflow.get_status(approval_id)
    assert status["status"] == "approved"
    assert status["approver"] == "soc"


def test_get_status_after_rejection(workflow, tree):
    decision = tree.decide(0.70, "scan")
    approval_id = workflow.request_approval(decision, "analyst1")
    workflow.reject(approval_id, "soc", "Insufficient data")
    status = workflow.get_status(approval_id)
    assert status["status"] == "rejected"
    assert status["reason"] == "Insufficient data"


def test_get_status_not_found(workflow):
    status = workflow.get_status("nonexistent")
    assert status == {}


def test_red_approval_requires_ciso(workflow, tree):
    decision = tree.decide(0.92, "rce")  # RED level
    approval_id = workflow.request_approval(decision, "analyst1")
    # soc cannot approve red
    result = workflow.approve(approval_id, "soc")
    assert result is False
    # only ciso can approve
    result = workflow.approve(approval_id, "ciso")
    assert result is True