import { getTranslations } from 'next-intl/server';
import { AlertFeed } from '@/components/dashboard/AlertFeed';
import { QuickActions } from '@/components/dashboard/QuickActions';
import styles from './page.module.css';

const mockAlerts = [
  { id: '1', severity: 'critical' as const, message: 'Prompt injection attempt - agent-42', agentId: 'agent-42', timestamp: '2024-01-15T10:30:00Z' },
  { id: '2', severity: 'high' as const, message: 'Unusual tool sequence - agent-17', agentId: 'agent-17', timestamp: '2024-01-15T10:25:00Z' },
];

export default async function DashboardPage() {
  const t = await getTranslations('dashboard');

  return (
    <div className={styles.dashboard}>
      <h1>{t('title')}</h1>
      <div className={styles.statsGrid}>
        <StatCard title={t('activeAgents')} value={24} />
        <StatCard title={t('threatsBlocked')} value={12} severity="danger" />
        <StatCard title={t('avgTrustScore')} value={78} severity="success" />
        <StatCard title={t('pendingApprovals')} value={3} severity="warning" />
      </div>
      <div className={styles.widgets}>
        <AlertFeed alerts={mockAlerts} />
        <QuickActions />
      </div>
    </div>
  );
}

function StatCard({ title, value, severity }: { title: string; value: number; severity?: string }) {
  return (
    <div className={`${styles.statCard} ${severity ? styles[severity] : ''}`}>
      <div className={styles.statTitle}>{title}</div>
      <div className={styles.statValue}>{value}</div>
    </div>
  );
}