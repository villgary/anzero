import { AgentTable } from '@/components/agents/AgentTable';
import styles from './page.module.css';

const mockAgents = [
  { id: 'agent-42', name: 'Email Agent', trustScore: 72, status: 'active' as const, lastActivity: '2024-01-15T10:30:00Z' },
  { id: 'agent-17', name: 'Search Agent', trustScore: 85, status: 'active' as const, lastActivity: '2024-01-15T10:25:00Z' },
  { id: 'agent-99', name: 'Data Agent', trustScore: 45, status: 'inactive' as const, lastActivity: '2024-01-14T15:00:00Z' },
];

export default function AgentsPage() {
  return (
    <div className={styles.page}>
      <h1>Agents</h1>
      <AgentTable agents={mockAgents} />
    </div>
  );
}