import { ApprovalQueue } from '@/components/approvals/ApprovalQueue';
import styles from './page.module.css';

const mockRequests = [
  { id: '1', agentId: 'agent-99', action: 'tool_call', tool: 'delete_database', reason: 'Database cleanup request from cron job', requestedAt: '2024-01-15T10:00:00Z' },
];

export default function ApprovalsPage() {
  return (
    <div className={styles.page}>
      <h1>Approval Queue</h1>
      <ApprovalQueue requests={mockRequests} />
    </div>
  );
}