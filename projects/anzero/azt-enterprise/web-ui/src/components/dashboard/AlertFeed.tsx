import styles from './AlertFeed.module.css';

interface Alert {
  id: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  message: string;
  agentId: string;
  timestamp: string;
}

interface AlertFeedProps {
  alerts: Alert[];
}

const severityColors = {
  critical: '#dc3545',
  high: '#fd7e14',
  medium: '#ffc107',
  low: '#28a745',
};

export function AlertFeed({ alerts }: AlertFeedProps) {
  return (
    <div className={styles.feed}>
      <h3>Recent Alerts</h3>
      {alerts.map((alert) => (
        <div key={alert.id} className={styles.alert}>
          <span
            className={styles.badge}
            style={{ background: severityColors[alert.severity] }}
          >
            {alert.severity.toUpperCase()}
          </span>
          <span className={styles.message}>{alert.message}</span>
        </div>
      ))}
    </div>
  );
}