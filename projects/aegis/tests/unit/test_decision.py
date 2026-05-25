import pytest
from app.countermeasure.decision.decision_tree import DecisionTree


@pytest.fixture
def tree():
    return DecisionTree()


def test_green_automatic_execution():
    tree = DecisionTree()
    decision = tree.decide(0.45, "scan")
    assert decision.level == "green"
    assert decision.approval_required is False


def test_red_requires_ciso_approval():
    tree = DecisionTree()
    decision = tree.decide(0.92, "rce")
    assert decision.level == "red"
    assert decision.approval_required is True
    assert decision.approver == "ciso"


def test_observe_level():
    tree = DecisionTree()
    decision = tree.decide(0.15, "scan")
    assert decision.level == "observe"
    assert decision.approval_required is False


def test_yellow_requires_soc_approval():
    tree = DecisionTree()
    decision = tree.decide(0.70, "scan")
    assert decision.level == "yellow"
    assert decision.approval_required is True
    assert decision.approver == "soc"


def test_boundary_60_green():
    tree = DecisionTree()
    decision = tree.decide(0.59, "scan")
    assert decision.level == "green"


def test_boundary_85_red():
    tree = DecisionTree()
    decision = tree.decide(0.85, "scan")
    assert decision.level == "red"


def test_invalid_confidence_negative():
    tree = DecisionTree()
    with pytest.raises(ValueError):
        tree.decide(-0.1, "scan")


def test_invalid_confidence_over_1():
    tree = DecisionTree()
    with pytest.raises(ValueError):
        tree.decide(1.1, "scan")