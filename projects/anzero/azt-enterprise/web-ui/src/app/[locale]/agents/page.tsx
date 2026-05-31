import { AgentTable } from '@/components/agents/AgentTable';
import { api } from '@/lib/api';
import styles from './page.module.css';

export default async function AgentsPage() {
  let agents: Array<{
    id: string;
    name: string;
    trustScore: number;
    status: 'active' | 'inactive';
    lastActivity?: string;
  }> = [];

  try {
    const data = await api.agents.list();
    agents = data.agents;
  } catch (error) {
    console.error('Failed to fetch agents:', error);
  }

  return (
    <div className={styles.page}>
      <h1>Agents</h1>
      <AgentTable agents={agents} />
    </div>
  );
}
