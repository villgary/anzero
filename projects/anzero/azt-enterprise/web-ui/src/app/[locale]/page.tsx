import { getTranslations } from 'next-intl/server';
import styles from './page.module.css';

export default async function DashboardPage() {
  const t = await getTranslations('dashboard');

  return (
    <div className={styles.dashboard}>
      <h1>{t('title')}</h1>
      <div className={styles.statsGrid}>
        <StatCard title={t('activeAgents')} value="24" />
        <StatCard title={t('threatsBlocked')} value="12" severity="danger" />
        <StatCard title={t('avgTrustScore')} value="78" severity="success" />
        <StatCard title={t('pendingApprovals')} value="3" severity="warning" />
      </div>
    </div>
  );
}

function StatCard({ title, value, severity }: { title: string; value: string; severity?: string }) {
  return (
    <div className={`${styles.statCard} ${severity ? styles[severity] : ''}`}>
      <div className={styles.statTitle}>{title}</div>
      <div className={styles.statValue}>{value}</div>
    </div>
  );
}