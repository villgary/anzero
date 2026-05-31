import { getTranslations } from 'next-intl/server';
import { AlertFeed } from '@/components/dashboard/AlertFeed';
import { QuickActions } from '@/components/dashboard/QuickActions';
import { api } from '@/lib/api';
import styles from './page.module.css';

export default async function DashboardPage() {
  const t = await getTranslations('dashboard');

  let stats = { activeAgents: 0, threatsBlocked: 0, avgTrustScore: 0, pendingApprovals: 0 };
  let alerts: Array<{ id: string; severity: 'critical' | 'high' | 'medium' | 'low'; message: string; agentId: string }> = [];

  try {
    stats = await api.dashboard.getStats();
    const alertsData = await api.alerts.list();
    alerts = alertsData.alerts.map(a => ({
      id: a.id,
      severity: a.severity,
      message: a.message,
      agentId: a.agentId,
    }));
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error);
  }

  return (
    <div className={styles.dashboard}>
      <h1>{t('title')}</h1>
      <div className={styles.statsGrid}>
        <StatCard title={t('activeAgents')} value={stats.activeAgents} />
        <StatCard title={t('threatsBlocked')} value={stats.threatsBlocked} severity="danger" />
        <StatCard title={t('avgTrustScore')} value={stats.avgTrustScore} severity="success" />
        <StatCard title={t('pendingApprovals')} value={stats.pendingApprovals} severity="warning" />
      </div>
      <div className={styles.widgets}>
        <AlertFeed alerts={alerts} />
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
