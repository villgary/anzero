# Phase 4: Web UI & Enterprise Features Specification

## Overview

Phase 4 implements the Web UI and enterprise features for the AZT Framework. This enables security ops teams and DevOps/platform engineers to manage policies, monitor agents, and respond to threats through a professional dashboard interface.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Next.js Frontend (TypeScript)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │Dashboard │  │ Policies │  │ Agents   │  │  Alerts   │  │
│  │ Widgets  │  │  Editor  │  │ Monitor  │  │ & HITL    │  │
│  └──────────┘  └──────────┘  └──────────┘  └───────────┘  │
│  └── i18n (next-intl) + RTL via dir="rtl"                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │ REST API
┌───────────────────────────▼─────────────────────────────────────┐
│                     Go API Server                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐  │
│  │ Policy   │  │  Agent   │  │  Alert & Approval         │  │
│  │  CRUD    │  │  Status  │  │  Workflow                │  │
│  └──────────┘  └──────────┘  └──────────────────────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐  │
│  │  Trust   │  │  Audit   │  │  Compliance              │  │
│  │  Score   │  │  Logs    │  │  Reports                 │  │
│  └──────────┘  └──────────┘  └──────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Next.js 14 (App Router) |
| Language | TypeScript |
| Styling | CSS Modules + CSS Logical Properties |
| i18n | next-intl with RTL support |
| State | React Server Components + minimal client state |
| API | Go REST API |
| Database | PostgreSQL (shared with gateway) |
| Deployment | Kubernetes (via Helm chart) |

## Visual Design

### Color Palette
- **Primary**: `#007bff` (blue)
- **Secondary**: `#6c757d` (gray)
- **Success**: `#28a745` (green)
- **Warning**: `#ffc107` (amber)
- **Danger**: `#dc3545` (red)
- **Background**: `#f5f7fa` (light gray)
- **Sidebar**: `#1a1a2e` (dark navy)
- **Card Background**: `#ffffff` (white)

### Typography
- **Headings**: System UI stack (Inter, -apple-system, sans-serif)
- **Body**: 14px base, 1.5 line height
- **Monospace**: JetBrains Mono (for code/YAML editor)

### Severity Colors
- **Critical (80+)**: `#dc3545` (red) - BLOCK
- **High (60-79)**: `#fd7e14` (orange) - LOG_ALERT
- **Medium (40-59)**: `#ffc107` (yellow) - monitoring
- **Low (<40)**: `#28a745` (green) - ALLOW

## Features

### 1. Dashboard

**Purpose**: Security overview at a glance

**Components**:
- Stat cards: Active Agents, Threats Blocked, Avg Trust Score, Pending Approvals
- Recent Alerts widget (last 10 alerts with severity badges)
- Quick Actions panel (View Alerts, Pending Approvals, Manage Policies)
- Trend charts (optional: threats over time, trust score distribution)

**Layout**: Compact - 4 stat cards in a row, alerts + actions below

### 2. Policy Management

**Policy List View**:
- Table of policies with columns: Name, Version, Status (Active/Draft), Last Modified, Actions
- Search/filter by name, status
- Create new policy button

**Policy Editor**:
- **Visual Mode**: Form-based rule builder
  - Agent selector (dropdown)
  - Rule name and description
  - Tool allowlist/denylist
  - Trust score conditions
  - Action selector (Allow/Deny/Require Approval)
- **YAML Mode**: Monaco editor with:
  - Syntax highlighting
  - Schema validation
  - Auto-complete for policy fields
- Toggle between Visual and YAML modes
- GitOps sync status indicator

**Policy Validation**:
- JSON Schema validation on save
- OPA Rego syntax check
- Preview of policy evaluation result

### 3. Agent Monitoring

**Agent List**:
- Table: Agent ID, Trust Score, Status (Active/Inactive), Last Activity, Actions
- Trust score badge (color-coded by threshold)
- Filter by status, trust score range

**Agent Detail**:
- Trust score breakdown (5 factors)
- Recent actions timeline
- Score history chart
- Threat detection history

### 4. Alerts & Threat Shield

**Alert List**:
- Real-time alert feed
- Severity filter (Critical/High/Medium/Low)
- Agent filter
- Time range selector
- Mark as resolved action

**Alert Detail**:
- Full context: agent, action, tool, prompt/output
- Matched threat patterns
- Recommended action
- Take action buttons (Block Agent, Adjust Score, Dismiss)

### 5. Human-in-the-Loop (HITL) Approvals

**Approval Queue**:
- List of pending approval requests
- Request details: agent, action, trust score, reason
- Approve/Deny buttons
- Timeout indicator (if auto-deny after X minutes)

**Request Detail**:
- Full action context
- Agent trust score and history
- Approve/Deny with optional comment
- Email notification sent to approvers

**Notifications**:
- In-app notification badge
- Email notifications to assigned approvers
- Slack/Teams webhook support (optional)

### 6. Audit Logs

**Log Viewer**:
- Searchable, filterable log table
- Columns: Timestamp, Agent, Action, Decision, Reason, Trust Score
- Export to CSV/JSON
- Time range filter
- Advanced filter by agent, action type, decision

**Log Detail**:
- Full request/response context
- Policy evaluation details
- Trust score at time of decision

### 7. Compliance Reports

**Report Types**:
- **Audit Summary**: All decisions over period
- **Threat Report**: All blocked threats
- **Trust Score Report**: Agent score trends
- **HITL Report**: Approval/denial statistics

**Report Features**:
- SOC2/GDPR template formats
- Scheduled reports (weekly/monthly)
- PDF export
- Email distribution lists

### 8. Settings

- **General**: Cluster name, timezone, notification preferences
- **Users**: User management, roles, permissions
- **API Keys**: Generate/revoke API keys for SDK
- **Integrations**: Email, Slack, MISP/STIX feed configuration
- **About**: Version info, license

## i18n Support

**Languages**:
| Code | Language | Direction |
|------|----------|-----------|
| en | English | LTR |
| zh | Chinese (Simplified) | LTR |
| ja | Japanese | LTR |
| fr | French | LTR |
| ar | Arabic | RTL |

**Implementation**:
- next-intl for translation management
- Translations stored in `/messages/{locale}.json`
- RTL via `dir="rtl"` attribute on `<html>`
- CSS Logical Properties for bidirectional layout (`margin-inline-start`, `padding-inline-end`, etc.)
- Language switcher in header
- Browser preference detection

## Deployment

### Open Source Core
```
helm install azt azt-framework/azt \
  --namespace azt-system \
  --create-namespace
```

### Enterprise
```
helm install azt-enterprise azt-enterprise/azt-enterprise \
  --namespace azt-enterprise \
  --set webUI.enabled=true \
  --set webUI.ingress.host=azt.example.com
```

## Data Model

### User
```typescript
interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'operator' | 'viewer';
  preferences: UserPreferences;
}
```

### Policy
```typescript
interface Policy {
  id: string;
  name: string;
  version: number;
  status: 'draft' | 'active';
  yaml: string;
  createdAt: Date;
  updatedAt: Date;
  createdBy: string;
}
```

### Agent
```typescript
interface Agent {
  id: string;
  name: string;
  trustScore: number;
  status: 'active' | 'inactive';
  lastActivity: Date;
  metadata: Record<string, string>;
}
```

### Alert
```typescript
interface Alert {
  id: string;
  agentId: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  analyzer: string;
  indicators: string[];
  context: Record<string, any>;
  status: 'open' | 'resolved' | 'ignored';
  createdAt: Date;
}
```

### ApprovalRequest
```typescript
interface ApprovalRequest {
  id: string;
  agentId: string;
  action: string;
  tool: string;
  parameters: Record<string, any>;
  reason: string;
  status: 'pending' | 'approved' | 'denied';
  requestedAt: Date;
  requestedBy: string;
  resolvedAt?: Date;
  resolvedBy?: string;
  comment?: string;
}
```

## API Endpoints

### Policies
- `GET /api/policies` - List policies
- `POST /api/policies` - Create policy
- `GET /api/policies/:id` - Get policy
- `PUT /api/policies/:id` - Update policy
- `DELETE /api/policies/:id` - Delete policy
- `POST /api/policies/:id/validate` - Validate policy

### Agents
- `GET /api/agents` - List agents
- `GET /api/agents/:id` - Get agent details
- `GET /api/agents/:id/history` - Get agent history
- `PUT /api/agents/:id/trust-score` - Adjust trust score

### Alerts
- `GET /api/alerts` - List alerts
- `GET /api/alerts/:id` - Get alert details
- `PUT /api/alerts/:id/status` - Update alert status

### Approvals
- `GET /api/approvals` - List pending approvals
- `POST /api/approvals` - Create approval request
- `PUT /api/approvals/:id/approve` - Approve
- `PUT /api/approvals/:id/deny` - Deny

### Audit Logs
- `GET /api/audit-logs` - List logs
- `GET /api/audit-logs/export` - Export logs (CSV/JSON)

### Compliance
- `GET /api/reports/audit-summary` - Audit summary report
- `GET /api/reports/threat-summary` - Threat summary report
- `POST /api/reports/schedule` - Schedule report

## Files to Create

```
azt-enterprise/
├── web-ui/                          # Next.js application
│   ├── src/
│   │   ├── app/
│   │   │   ├── [locale]/           # i18n routing
│   │   │   │   ├── page.tsx       # Dashboard
│   │   │   │   ├── policies/
│   │   │   │   ├── agents/
│   │   │   │   ├── alerts/
│   │   │   │   ├── approvals/
│   │   │   │   ├── audit/
│   │   │   │   └── settings/
│   │   │   ├── api/                # API routes (optional)
│   │   │   └── layout.tsx
│   │   ├── components/
│   │   │   ├── dashboard/
│   │   │   ├── policy-editor/
│   │   │   ├── agents/
│   │   │   ├── alerts/
│   │   │   └── ui/                 # Shared UI components
│   │   ├── lib/
│   │   │   ├── api.ts             # API client
│   │   │   └── i18n.ts
│   │   ├── messages/               # Translation files
│   │   │   ├── en.json
│   │   │   ├── zh.json
│   │   │   ├── ja.json
│   │   │   ├── fr.json
│   │   │   └── ar.json
│   │   └── styles/
│   │       └── globals.css
│   ├── next.config.js
│   ├── package.json
│   └── tsconfig.json
│
├── api-server/                      # Go REST API
│   ├── cmd/
│   │   └── server/
│   │       └── main.go
│   ├── internal/
│   │   ├── api/
│   │   │   ├── handlers/
│   │   │   ├── middleware/
│   │   │   └── router.go
│   │   ├── models/
│   │   └── services/
│   ├── go.mod
│   └── go.sum
│
├── migrations/
│   └── 003_create_enterprise_tables.sql
│
├── helm/
│   ├── azt-enterprise/             # Enterprise Helm chart
│   └── values.yaml
│
└── README.md
```

## Implementation Phases

### Phase 4.1: Foundation
- Next.js project setup with TypeScript
- Basic layout (sidebar + header)
- i18n setup with next-intl
- Go API server skeleton
- Database migration

### Phase 4.2: Dashboard & Agents
- Dashboard with stat cards
- Agent list and detail views
- Trust score display
- Basic API integration

### Phase 4.3: Policy Management
- Policy list view
- YAML editor with Monaco
- Policy validation
- Create/edit policy flow

### Phase 4.4: Alerts & HITL
- Alert list and detail
- Approval queue
- Approve/deny workflow
- Notifications

### Phase 4.5: Audit & Compliance
- Audit log viewer
- Export functionality
- Report templates
- Scheduled reports

### Phase 4.6: i18n & Polish
- All translations
- RTL support
- Responsive design
- Performance optimization
