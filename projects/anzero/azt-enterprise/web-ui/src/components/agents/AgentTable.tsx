import Link from 'next/link';
import styles from './AgentTable.module.css';

interface Agent {
  id: string;
  name: string;
  trustScore: number;
  status: 'active' | 'inactive';
  lastActivity: string;
}

interface AgentTableProps {
  agents: Agent[];
}

export function AgentTable({ agents }: AgentTableProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return '#28a745';
    if (score >= 60) return '#ffc107';
    return '#dc3545';
  };

  return (
    <table className={styles.table}>
      <thead>
        <tr>
          <th>Agent ID</th>
          <th>Trust Score</th>
          <th>Status</th>
          <th>Last Activity</th>
        </tr>
      </thead>
      <tbody>
        {agents.map((agent) => (
          <tr key={agent.id}>
            <td>
              <Link href={`/agents/${agent.id}`} className={styles.link}>
                {agent.id}
              </Link>
            </td>
            <td>
              <span style={{ color: getScoreColor(agent.trustScore), fontWeight: 'bold' }}>
                {agent.trustScore}
              </span>
            </td>
            <td>
              <span className={`${styles.badge} ${styles[agent.status]}`}>
                {agent.status}
              </span>
            </td>
            <td>{new Date(agent.lastActivity).toLocaleString()}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}