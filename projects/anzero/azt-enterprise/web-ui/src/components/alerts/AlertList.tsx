'use client';

import styles from './AlertList.module.css';

interface Alert {
  id: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  message: string;
  agentId: string;
  analyzer: string;
  createdAt: string;
}

interface AlertListProps {
  alerts: Alert[];
}

const severityConfig = {
  critical: { color: '#dc3545', label: 'CRITICAL' },
  high: { color: '#fd7e14', label: 'HIGH' },
  medium: { color: '#ffc107', label: 'MEDIUM' },
  low: { color: '#28a745', label: 'LOW' },
};

export function AlertList({ alerts }: AlertListProps) {
  return (
    <div className={styles.list}>
      {alerts.map((alert) => {
        const config = severityConfig[alert.severity];
        return (
          <div key={alert.id} className={styles.alert}>
            <div className={styles.header}>
              <span className={styles.badge} style={{ background: config.color }}>
                {config.label}
              </span>
              <span className={styles.time}>
                {new Date(alert.createdAt).toLocaleString()}
              </span>
            </div>
            <div className={styles.message}>{alert.message}</div>
            <div className={styles.meta}>
              <span>Agent: {alert.agentId}</span>
              <span>Analyzer: {alert.analyzer}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}