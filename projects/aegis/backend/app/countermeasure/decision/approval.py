import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from app.countermeasure.decision.decision_tree import CountermeasureDecision


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class ApprovalRequest:
    approval_id: str
    decision: CountermeasureDecision
    requester: str
    status: ApprovalStatus
    approver: Optional[str] = None
    reason: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class ApprovalWorkflow:
    def __init__(self):
        self._approvals: dict[str, ApprovalRequest] = {}

    def request_approval(
        self, decision: CountermeasureDecision, requester: str
    ) -> str:
        """Request approval for a countermeasure decision.

        Returns:
            approval_id: Unique identifier for tracking this approval request
        """
        if not decision.approval_required:
            raise ValueError("Decision does not require approval")

        approval_id = str(uuid.uuid4())[:8]
        request = ApprovalRequest(
            approval_id=approval_id,
            decision=decision,
            requester=requester,
            status=ApprovalStatus.PENDING,
        )
        self._approvals[approval_id] = request
        return approval_id

    def approve(self, approval_id: str, approver: str) -> bool:
        """Approve a pending approval request.

        Returns:
            True if approved successfully, False if not found or not pending
        """
        request = self._approvals.get(approval_id)
        if not request or request.status != ApprovalStatus.PENDING:
            return False

        # Validate approver matches the required role
        if request.decision.approver and approver.lower() != request.decision.approver:
            return False

        request.status = ApprovalStatus.APPROVED
        request.approver = approver
        request.updated_at = datetime.utcnow()
        return True

    def reject(self, approval_id: str, approver: str, reason: str) -> bool:
        """Reject a pending approval request.

        Returns:
            True if rejected successfully, False if not found or not pending
        """
        request = self._approvals.get(approval_id)
        if not request or request.status != ApprovalStatus.PENDING:
            return False

        # Validate approver matches the required role
        if request.decision.approver and approver.lower() != request.decision.approver:
            return False

        request.status = ApprovalStatus.REJECTED
        request.approver = approver
        request.reason = reason
        request.updated_at = datetime.utcnow()
        return True

    def get_status(self, approval_id: str) -> dict:
        """Get the status of an approval request.

        Returns:
            dict with approval details, or empty dict if not found
        """
        request = self._approvals.get(approval_id)
        if not request:
            return {}

        return {
            "approval_id": request.approval_id,
            "status": request.status.value,
            "requester": request.requester,
            "approver": request.approver,
            "level": request.decision.level.value,
            "countermeasures": request.decision.countermeasures,
            "reason": request.reason,
            "created_at": request.created_at.isoformat(),
            "updated_at": request.updated_at.isoformat(),
        }