'use client';

import { useState } from 'react';
import styles from './ApprovalQueue.module.css';

interface ApprovalRequest {
  id: string;
  agentId: string;
  action: string;
  tool: string;
  reason: string;
  requestedAt: string;
}

interface ApprovalQueueProps {
  requests: ApprovalRequest[];
}

export function ApprovalQueue({ requests }: ApprovalQueueProps) {
  const [localRequests, setLocalRequests] = useState(requests);

  const handleApprove = (id: string) => {
    setLocalRequests(localRequests.filter((r) => r.id !== id));
    alert(`Approved request ${id}`);
  };

  const handleDeny = (id: string) => {
    setLocalRequests(localRequests.filter((r) => r.id !== id));
    alert(`Denied request ${id}`);
  };

  if (localRequests.length === 0) {
    return (
      <div className={styles.empty}>
        <p>No pending approvals</p>
      </div>
    );
  }

  return (
    <div className={styles.queue}>
      {localRequests.map((req) => (
        <div key={req.id} className={styles.request}>
          <div className={styles.header}>
            <span className={styles.agent}>{req.agentId}</span>
            <span className={styles.time}>
              {new Date(req.requestedAt).toLocaleString()}
            </span>
          </div>
          <div className={styles.action}>
            {req.action} - {req.tool}
          </div>
          <div className={styles.reason}>{req.reason}</div>
          <div className={styles.actions}>
            <button
              onClick={() => handleApprove(req.id)}
              className={styles.approveBtn}
            >
              Approve
            </button>
            <button
              onClick={() => handleDeny(req.id)}
              className={styles.denyBtn}
            >
              Deny
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}