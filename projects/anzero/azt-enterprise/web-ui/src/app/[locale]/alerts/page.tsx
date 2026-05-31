import { AlertList } from '@/components/alerts/AlertList';
import { api } from '@/lib/api';
import styles from './page.module.css';

export default async function AlertsPage() {
  let alerts: Array<{
    id: string;
    severity: 'critical' | 'high' | 'medium' | 'low';
    message: string;
    agentId: string;
    analyzer?: string;
    createdAt?: string;
  }> = [];

  try {
    const data = await api.alerts.list();
    alerts = data.alerts.map(a => ({
      id: a.id,
      severity: a.severity,
      message: a.message,
      agentId: a.agentId,
    }));
  } catch (error) {
    console.error('Failed to fetch alerts:', error);
  }

  return (
    <div className={styles.page}>
      <h1>Alerts</h1>
      <AlertList alerts={alerts} />
    </div>
  );
}
