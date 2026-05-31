import { ApprovalQueue } from '@/components/approvals/ApprovalQueue';
import { api } from '@/lib/api';
import styles from './page.module.css';

export default async function ApprovalsPage() {
  let requests: Array<{
    id: string;
    agentId: string;
    action: string;
    tool: string;
    reason: string;
    requestedAt?: string;
  }> = [];

  try {
    const data = await api.approvals.list();
    requests = data.approvals;
  } catch (error) {
    console.error('Failed to fetch approvals:', error);
  }

  return (
    <div className={styles.page}>
      <h1>Approval Queue</h1>
      <ApprovalQueue requests={requests} />
    </div>
  );
}
