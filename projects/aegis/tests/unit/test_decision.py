import pytest
from app.countermeasure.decision.decision_tree import DecisionTree


@pytest.fixture
def tree():
    return DecisionTree()


def test_green_automatic_execution():
    tree = DecisionTree()
    decision = tree.decide(confidence=0.45, attack_type="scan")
    assert decision.level == "green"
    assert decision.approval_required is False


def test_red_requires_ciso_approval():
    tree = DecisionTree()
    decision = tree.decide(confidence=0.92, attack_type="rce")
    assert decision.level == "red"
    assert decision.approval_required is True
    assert decision.approver == "ciso"