const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

async function fetchJSON<T>(endpoint: string): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`);
  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }
  return res.json();
}

export interface DashboardStats {
  activeAgents: number;
  threatsBlocked: number;
  avgTrustScore: number;
  pendingApprovals: number;
}

export interface Alert {
  id: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  message: string;
  agentId: string;
  timestamp?: string;
}

export interface Agent {
  id: string;
  name: string;
  trustScore: number;
  status: 'active' | 'inactive';
  lastActivity?: string;
}

export interface Approval {
  id: string;
  agentId: string;
  action: string;
  tool: string;
  reason: string;
  status: 'pending' | 'approved' | 'denied';
}

export const api = {
  dashboard: {
    getStats: () => fetchJSON<DashboardStats>('/api/v1/dashboard/stats'),
  },
  alerts: {
    list: () => fetchJSON<{ alerts: Alert[] }>('/api/v1/alerts'),
  },
  agents: {
    list: () => fetchJSON<{ agents: Agent[] }>('/api/v1/agents'),
    get: (id: string) => fetchJSON<Agent>(`/api/v1/agents/${id}`),
  },
  approvals: {
    list: () => fetchJSON<{ approvals: Approval[] }>('/api/v1/approvals'),
  },
};
