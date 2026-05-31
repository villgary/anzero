import { AlertList } from '@/components/alerts/AlertList';
import styles from './page.module.css';

const mockAlerts = [
  { id: '1', severity: 'critical' as const, message: 'Prompt injection attempt', agentId: 'agent-42', analyzer: 'prompt_injection', createdAt: '2024-01-15T10:30:00Z' },
  { id: '2', severity: 'high' as const, message: 'Unusual tool sequence', agentId: 'agent-17', analyzer: 'model_abuse', createdAt: '2024-01-15T10:25:00Z' },
  { id: '3', severity: 'medium' as const, message: 'Elevated request rate', agentId: 'agent-99', analyzer: 'rate_limit', createdAt: '2024-01-15T10:20:00Z' },
];

export default function AlertsPage() {
  return (
    <div className={styles.page}>
      <h1>Alerts</h1>
      <AlertList alerts={mockAlerts} />
    </div>
  );
}