import { notFound } from 'next/navigation';
import Link from 'next/link';
import styles from './page.module.css';

interface Props {
  params: Promise<{ id: string }>;
}

export default async function AgentDetailPage({ params }: Props) {
  const { id } = await params;

  if (!id) {
    notFound();
  }

  // Mock data - in real app would fetch from API
  const agent = {
    id,
    name: 'Email Agent',
    trustScore: 72,
    status: 'active',
    lastActivity: '2024-01-15T10:30:00Z',
    factors: {
      identity: 80,
      history: 75,
      time: 70,
      anomaly: 65,
      frequency: 70,
    },
  };

  return (
    <div className={styles.page}>
      <Link href="/agents" className={styles.backLink}>&larr; Back to Agents</Link>
      <h1>Agent: {id}</h1>
      <div className={styles.detailGrid}>
        <div className={styles.card}>
          <h3>Overview</h3>
          <div className={styles.stat}>
            <span>Name:</span> {agent.name}
          </div>
          <div className={styles.stat}>
            <span>Status:</span> {agent.status}
          </div>
          <div className={styles.stat}>
            <span>Last Activity:</span> {new Date(agent.lastActivity).toLocaleString()}
          </div>
        </div>
        <div className={styles.card}>
          <h3>Trust Score: {agent.trustScore}</h3>
          <div className={styles.factors}>
            <div>Identity: {agent.factors.identity}</div>
            <div>History: {agent.factors.history}</div>
            <div>Time: {agent.factors.time}</div>
            <div>Anomaly: {agent.factors.anomaly}</div>
            <div>Frequency: {agent.factors.frequency}</div>
          </div>
        </div>
      </div>
    </div>
  );
}