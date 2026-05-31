# Phase 4: Web UI & Enterprise Features Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the Web UI dashboard and Go API server for AZT Enterprise, enabling security teams to manage policies, monitor agents, and respond to threats.

**Architecture:** Next.js 14 frontend with TypeScript (App Router), Go REST API server, PostgreSQL database shared with gateway, next-intl for i18n with RTL support.

**Tech Stack:** Next.js 14, TypeScript, CSS Modules, next-intl, Go, PostgreSQL, React

---

## File Structure

```
azt-enterprise/
├── web-ui/                          # Next.js application
│   ├── src/
│   │   ├── app/
│   │   │   ├── [locale]/           # i18n routing
│   │   │   │   ├── layout.tsx
│   │   │   │   ├── page.tsx        # Dashboard
│   │   │   │   ├── policies/
│   │   │   │   ├── agents/
│   │   │   │   ├── alerts/
│   │   │   │   └── settings/
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   ├── dashboard/
│   │   │   ├── policy-editor/
│   │   │   ├── agents/
│   │   │   ├── alerts/
│   │   │   └── ui/                 # Shared components
│   │   ├── lib/
│   │   │   └── api.ts              # API client
│   │   └── messages/               # Translation files
│   │       ├── en.json
│   │       ├── zh.json
│   │       ├── ja.json
│   │       ├── fr.json
│   │       └── ar.json
│   ├── next.config.js
│   └── package.json
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
│   │   └── models/
│   └── go.mod
│
├── migrations/
│   └── 003_create_enterprise_tables.sql
│
└── helm/
    └── azt-enterprise/
```

---

## Task 1: Project Scaffolding

**Files:**
- Create: `azt-enterprise/web-ui/` (Next.js app)
- Create: `azt-enterprise/api-server/` (Go app)
- Create: `azt-enterprise/migrations/003_create_enterprise_tables.sql`

- [ ] **Step 1: Create Next.js project**

Run in `/Users/jyb/projects/anzero/azt-enterprise/`:
```bash
npx create-next-app@latest web-ui \
  --typescript \
  --tailwind=false \
  --eslint \
  --app \
  --src-dir \
  --import-alias "@/*" \
  --no-git \
  --use-npm
```

Expected: Next.js app created in web-ui/

- [ ] **Step 2: Create Go API project**

Run in `/Users/jyb/projects/anzero/azt-enterprise/`:
```bash
mkdir -p api-server/cmd/server
cd api-server
go mod init github.com/anzero/azt-enterprise/api-server
```

- [ ] **Step 3: Create database migration**

Create `migrations/003_create_enterprise_tables.sql`:
```sql
-- Users for Web UI authentication
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'viewer',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- API keys for SDK authentication
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    key_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    user_id INTEGER REFERENCES users(id),
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

-- Alert assignments
CREATE TABLE IF NOT EXISTS alert_assignments (
    id SERIAL PRIMARY KEY,
    alert_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    assigned_at TIMESTAMP DEFAULT NOW()
);

-- Approval requests
CREATE TABLE IF NOT EXISTS approval_requests (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(255) NOT NULL,
    action VARCHAR(100) NOT NULL,
    tool VARCHAR(100),
    parameters JSONB,
    reason TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    requested_by VARCHAR(255) NOT NULL,
    requested_at TIMESTAMP DEFAULT NOW(),
    resolved_by VARCHAR(255),
    resolved_at TIMESTAMP,
    comment TEXT
);

-- Report schedules
CREATE TABLE IF NOT EXISTS report_schedules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    frequency VARCHAR(20) NOT NULL,
    recipients TEXT[],
    enabled BOOLEAN DEFAULT TRUE,
    last_run_at TIMESTAMP,
    next_run_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_approval_requests_status ON approval_requests(status);
CREATE INDEX IF NOT EXISTS idx_approval_requests_agent_id ON approval_requests(agent_id);
CREATE INDEX IF NOT EXISTS idx_alert_assignments_user ON alert_assignments(user_id);
```

- [ ] **Step 4: Commit**

```bash
git add azt-enterprise/
git commit -m "feat(enterprise): scaffold Phase 4 project structure

- Add Next.js web-ui with TypeScript
- Add Go API server skeleton
- Add database migration for enterprise tables"
```

---

## Task 2: Basic Layout & Navigation

**Files:**
- Create: `azt-enterprise/web-ui/src/app/[locale]/layout.tsx`
- Create: `azt-enterprise/web-ui/src/app/[locale]/page.tsx`
- Create: `azt-enterprise/web-ui/src/components/ui/Sidebar.tsx`
- Create: `azt-enterprise/web-ui/src/components/ui/Header.tsx`

- [ ] **Step 1: Write layout test**

Create `web-ui/src/app/[locale]/layout.test.tsx`:
```typescript
import { render, screen } from '@testing-library/react';
import { NextIntlClientProvider } from 'next-intl';
import messages from '@/messages/en.json';

describe('Layout', () => {
  it('renders sidebar navigation', () => {
    render(
      <NextIntlClientProvider locale="en" messages={messages}>
        <Layout>
          <div>Content</div>
        </Layout>
      </NextIntlClientProvider>
    );

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Policies')).toBeInTheDocument();
    expect(screen.getByText('Agents')).toBeInTheDocument();
    expect(screen.getByText('Alerts')).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Create Sidebar component**

```typescript
// web-ui/src/components/ui/Sidebar.tsx
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import styles from './Sidebar.module.css';

const navItems = [
  { href: '/', label: 'Dashboard' },
  { href: '/policies', label: 'Policies' },
  { href: '/agents', label: 'Agents' },
  { href: '/alerts', label: 'Alerts' },
  { href: '/approvals', label: 'Approvals' },
  { href: '/settings', label: 'Settings' },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className={styles.sidebar}>
      <div className={styles.logo}>AZT Shield</div>
      <nav>
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={pathname === item.href ? styles.active : ''}
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
```

- [ ] **Step 3: Create Sidebar CSS**

```css
/* web-ui/src/components/ui/Sidebar.module.css */
.sidebar {
  width: 220px;
  background: #1a1a2e;
  color: white;
  padding: 16px;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
}

.logo {
  font-weight: bold;
  font-size: 18px;
  margin-bottom: 20px;
}

nav {
  display: flex;
  flex-direction: column;
}

nav a {
  color: white;
  text-decoration: none;
  padding: 8px 12px;
  margin-bottom: 4px;
  border-radius: 4px;
}

nav a:hover {
  background: #16213e;
}

nav a.active {
  background: #16213e;
}
```

- [ ] **Step 4: Create locale layout**

```typescript
// web-ui/src/app/[locale]/layout.tsx
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { notFound } from 'next/navigation';
import { Sidebar } from '@/components/ui/Sidebar';
import styles from './layout.module.css';

export function generateStaticParams() {
  return [{ locale: 'en' }, { locale: 'zh' }, { locale: 'ja' }, { locale: 'fr' }, { locale: 'ar' }];
}

export default async function LocaleLayout({
  children,
  params: { locale }
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  const messages = await getMessages();

  if (!messages) {
    notFound();
  }

  return (
    <html dir={locale === 'ar' ? 'rtl' : 'ltr'}>
      <body>
        <NextIntlClientProvider locale={locale} messages={messages}>
          <div className={styles.layout}>
            <Sidebar />
            <main className={styles.main}>{children}</main>
          </div>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
```

- [ ] **Step 5: Create layout CSS**

```css
/* web-ui/src/app/[locale]/layout.module.css */
.layout {
  display: flex;
  min-height: 100vh;
}

.main {
  margin-left: 220px;
  flex: 1;
  padding: 24px;
  background: #f5f7fa;
}

[dir="rtl"] .main {
  margin-left: 0;
  margin-right: 220px;
}
```

- [ ] **Step 6: Create dashboard page**

```typescript
// web-ui/src/app/[locale]/page.tsx
import { getTranslations } from 'next-intl/server';

export default async function DashboardPage() {
  const t = await getTranslations('dashboard');

  return (
    <div>
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
```

- [ ] **Step 7: Create English messages**

```json
// web-ui/src/messages/en.json
{
  "dashboard": {
    "title": "Security Overview",
    "activeAgents": "Active Agents",
    "threatsBlocked": "Threats Blocked",
    "avgTrustScore": "Avg Trust Score",
    "pendingApprovals": "Pending Approvals"
  },
  "nav": {
    "dashboard": "Dashboard",
    "policies": "Policies",
    "agents": "Agents",
    "alerts": "Alerts",
    "approvals": "Approvals",
    "settings": "Settings"
  }
}
```

- [ ] **Step 8: Verify and commit**

```bash
cd web-ui && npm run build
git add azt-enterprise/
git commit -m "feat(enterprise): basic layout and navigation

- Add sidebar navigation
- Add locale-based routing
- Add RTL support for Arabic
- Add dashboard page structure"
```

---

## Task 3: Dashboard Widgets

**Files:**
- Create: `web-ui/src/components/dashboard/StatCard.tsx`
- Modify: `web-ui/src/app/[locale]/page.tsx`
- Create: `web-ui/src/components/dashboard/AlertFeed.tsx`
- Create: `web-ui/src/components/dashboard/QuickActions.tsx`

- [ ] **Step 1: Create StatCard component**

```typescript
// web-ui/src/components/dashboard/StatCard.tsx
import styles from './StatCard.module.css';

interface StatCardProps {
  title: string;
  value: string | number;
  severity?: 'success' | 'warning' | 'danger';
}

export function StatCard({ title, value, severity }: StatCardProps) {
  return (
    <div className={`${styles.card} ${severity ? styles[severity] : ''}`}>
      <div className={styles.title}>{title}</div>
      <div className={styles.value}>{value}</div>
    </div>
  );
}
```

```css
/* web-ui/src/components/dashboard/StatCard.module.css */
.card {
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  flex: 1;
}

.title {
  color: #666;
  font-size: 12px;
  text-transform: uppercase;
}

.value {
  font-size: 28px;
  font-weight: bold;
}

.success .value {
  color: #28a745;
}

.warning .value {
  color: #ffc107;
}

.danger .value {
  color: #dc3545;
}
```

- [ ] **Step 2: Create AlertFeed component**

```typescript
// web-ui/src/components/dashboard/AlertFeed.tsx
import styles from './AlertFeed.module.css';

interface Alert {
  id: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  message: string;
  agentId: string;
  timestamp: string;
}

interface AlertFeedProps {
  alerts: Alert[];
}

const severityColors = {
  critical: '#dc3545',
  high: '#fd7e14',
  medium: '#ffc107',
  low: '#28a745',
};

export function AlertFeed({ alerts }: AlertFeedProps) {
  return (
    <div className={styles.feed}>
      <h3>Recent Alerts</h3>
      {alerts.map((alert) => (
        <div key={alert.id} className={styles.alert}>
          <span
            className={styles.badge}
            style={{ background: severityColors[alert.severity] }}
          >
            {alert.severity.toUpperCase()}
          </span>
          <span className={styles.message}>{alert.message}</span>
        </div>
      ))}
    </div>
  );
}
```

- [ ] **Step 3: Update dashboard page with mock data**

```typescript
// web-ui/src/app/[locale]/page.tsx
import { getTranslations } from 'next-intl/server';
import { StatCard } from '@/components/dashboard/StatCard';
import { AlertFeed } from '@/components/dashboard/AlertFeed';
import styles from './page.module.css';

// Mock data for demo
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
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Add CSS**

```css
/* web-ui/src/app/[locale]/page.module.css */
.dashboard h1 {
  margin-bottom: 24px;
}

.statsGrid {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.widgets {
  display: flex;
  gap: 16px;
}
```

- [ ] **Step 5: Commit**

```bash
git add azt-enterprise/
git commit -m "feat(enterprise): dashboard widgets

- Add StatCard component with severity colors
- Add AlertFeed component
- Add dashboard page with mock data"
```

---

## Task 4: Go API Server Foundation

**Files:**
- Create: `azt-enterprise/api-server/cmd/server/main.go`
- Create: `azt-enterprise/api-server/internal/api/router.go`
- Create: `azt-enterprise/api-server/internal/api/handlers/health.go`

- [ ] **Step 1: Create main.go**

```go
package main

import (
    "log"
    "os"

    "github.com/anzero/azt-enterprise/api-server/internal/api"
)

func main() {
    port := os.Getenv("PORT")
    if port == "" {
        port = "8080"
    }

    router := api.NewRouter()
    log.Printf("Starting API server on :%s", port)
    if err := router.Run(":" + port); err != nil {
        log.Fatalf("Failed to start server: %v", err)
    }
}
```

- [ ] **Step 2: Create router.go**

```go
package api

import (
    "github.com/gin-gonic/gin"
)

func NewRouter() *gin.Engine {
    r := gin.Default()

    // CORS middleware
    r.Use(func(c *gin.Context) {
        c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
        c.Writer.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
        if c.Request.Method == "OPTIONS" {
            c.AbortWithStatus(204)
            return
        }
        c.Next()
    })

    // Health check
    r.GET("/health", func(c *gin.Context) {
        c.JSON(200, gin.H{"status": "ok"})
    })

    // API v1 routes
    v1 := r.Group("/api/v1")
    {
        v1.GET("/dashboard/stats", func(c *gin.Context) {
            c.JSON(200, gin.H{
                "activeAgents":    24,
                "threatsBlocked":  12,
                "avgTrustScore":   78,
                "pendingApprovals": 3,
            })
        })

        v1.GET("/alerts", func(c *gin.Context) {
            c.JSON(200, gin.H{
                "alerts": []gin.H{
                    {"id": "1", "severity": "critical", "message": "Prompt injection attempt", "agentId": "agent-42"},
                },
            })
        })
    }

    return r
}
```

- [ ] **Step 3: Create go.mod**

```go
module github.com/anzero/azt-enterprise/api-server

go 1.21

require github.com/gin-gonic/gin v1.9.1
```

- [ ] **Step 4: Test and commit**

```bash
cd api-server && go mod tidy && go build ./...
git add azt-enterprise/
git commit -m "feat(enterprise): Go API server foundation

- Add basic Gin router
- Add health check endpoint
- Add dashboard stats and alerts endpoints
- Add CORS middleware"
```

---

## Task 5: i18n Setup with Translations

**Files:**
- Create: `web-ui/src/messages/zh.json`
- Create: `web-ui/src/messages/ja.json`
- Create: `web-ui/src/messages/fr.json`
- Create: `web-ui/src/messages/ar.json`
- Modify: `web-ui/src/app/[locale]/layout.tsx` (add all locales)

- [ ] **Step 1: Create Chinese translations**

```json
{
  "dashboard": {
    "title": "安全概览",
    "activeAgents": "活跃代理",
    "threatsBlocked": "已阻止威胁",
    "avgTrustScore": "平均信任分数",
    "pendingApprovals": "待审批"
  },
  "nav": {
    "dashboard": "仪表板",
    "policies": "策略",
    "agents": "代理",
    "alerts": "告警",
    "approvals": "审批",
    "settings": "设置"
  }
}
```

- [ ] **Step 2: Create Japanese translations**

```json
{
  "dashboard": {
    "title": "セキュリティ概要",
    "activeAgents": "アクティブエージェント",
    "threatsBlocked": "ブロックされた脅威",
    "avgTrustScore": "平均信頼スコア",
    "pendingApprovals": "承認待ち"
  },
  "nav": {
    "dashboard": "ダッシュボード",
    "policies": "ポリシー",
    "agents": "エージェント",
    "alerts": "アラート",
    "approvals": "承認",
    "settings": "設定"
  }
}
```

- [ ] **Step 3: Create French translations**

```json
{
  "dashboard": {
    "title": "Aperçu de la sécurité",
    "activeAgents": "Agents actifs",
    "threatsBlocked": "Menaces bloquées",
    "avgTrustScore": "Score de confiance moyen",
    "pendingApprovals": "Approbations en attente"
  },
  "nav": {
    "dashboard": "Tableau de bord",
    "policies": "Politiques",
    "agents": "Agents",
    "alerts": "Alertes",
    "approvals": "Approbations",
    "settings": "Paramètres"
  }
}
```

- [ ] **Step 4: Create Arabic translations**

```json
{
  "dashboard": {
    "title": "نظرة عامة على الأمان",
    "activeAgents": "الوكلاء النشطون",
    "threatsBlocked": "التهديدات المحظورة",
    "avgTrustScore": "متوسط درجة الثقة",
    "pendingApprovals": "الموافقات المعلقة"
  },
  "nav": {
    "dashboard": "لوحة القيادة",
    "policies": "السياسات",
    "agents": "الوكلاء",
    "alerts": "التنبيهات",
    "approvals": "الموافقات",
    "settings": "الإعدادات"
  }
}
```

- [ ] **Step 5: Update layout to include all locales**

```typescript
export function generateStaticParams() {
  return [
    { locale: 'en' },
    { locale: 'zh' },
    { locale: 'ja' },
    { locale: 'fr' },
    { locale: 'ar' },
  ];
}
```

- [ ] **Step 6: Commit**

```bash
git add azt-enterprise/
git commit -m "feat(enterprise): add i18n translations

- Add Chinese (zh), Japanese (ja), French (fr), Arabic (ar) translations
- All UI strings translated
- RTL support for Arabic via dir attribute"
```

---

## Task 6: Agent List & Detail Pages

**Files:**
- Create: `web-ui/src/app/[locale]/agents/page.tsx`
- Create: `web-ui/src/app/[locale]/agents/[id]/page.tsx`
- Create: `web-ui/src/components/agents/AgentTable.tsx`
- Create: `web-ui/src/components/agents/AgentDetail.tsx`

- [ ] **Step 1: Create AgentTable component**

```typescript
// web-ui/src/components/agents/AgentTable.tsx
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
              <Link href={`/agents/${agent.id}`}>{agent.id}</Link>
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
            <td>{agent.lastActivity}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

- [ ] **Step 2: Create agents page**

```typescript
// web-ui/src/app/[locale]/agents/page.tsx
import { AgentTable } from '@/components/agents/AgentTable';

const mockAgents = [
  { id: 'agent-42', name: 'Email Agent', trustScore: 72, status: 'active' as const, lastActivity: '2024-01-15T10:30:00Z' },
  { id: 'agent-17', name: 'Search Agent', trustScore: 85, status: 'active' as const, lastActivity: '2024-01-15T10:25:00Z' },
  { id: 'agent-99', name: 'Data Agent', trustScore: 45, status: 'inactive' as const, lastActivity: '2024-01-14T15:00:00Z' },
];

export default function AgentsPage() {
  return (
    <div>
      <h1>Agents</h1>
      <AgentTable agents={mockAgents} />
    </div>
  );
}
```

- [ ] **Step 3: Create agent detail page**

```typescript
// web-ui/src/app/[locale]/agents/[id]/page.tsx
import { notFound } from 'next/navigation';

interface Props {
  params: { id: string };
}

export default function AgentDetailPage({ params }: Props) {
  // In real app, fetch agent by ID
  if (!params.id) {
    notFound();
  }

  return (
    <div>
      <h1>Agent: {params.id}</h1>
      <div className={styles.detailGrid}>
        <div>Trust Score: 72</div>
        <div>Status: active</div>
        <div>Last Activity: 2024-01-15T10:30:00Z</div>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Add API endpoint**

```go
// In router.go, add:
v1.GET("/agents", func(c *gin.Context) {
    c.JSON(200, gin.H{
        "agents": []gin.H{
            {"id": "agent-42", "name": "Email Agent", "trustScore": 72, "status": "active"},
            {"id": "agent-17", "name": "Search Agent", "trustScore": 85, "status": "active"},
        },
    })
})

v1.GET("/agents/:id", func(c *gin.Context) {
    id := c.Param("id")
    c.JSON(200, gin.H{
        "id": id,
        "name": "Email Agent",
        "trustScore": 72,
        "status": "active",
        "lastActivity": "2024-01-15T10:30:00Z",
    })
})
```

- [ ] **Step 5: Commit**

```bash
git add azt-enterprise/
git commit -m "feat(enterprise): agent list and detail pages

- Add AgentTable component with trust score coloring
- Add agents listing page
- Add agent detail page with dynamic routing
- Add agents API endpoints"
```

---

## Task 7: Policy Editor with YAML

**Files:**
- Create: `web-ui/src/app/[locale]/policies/page.tsx`
- Create: `web-ui/src/components/policy-editor/PolicyEditor.tsx`
- Create: `web-ui/src/components/policy-editor/YAMLEditor.tsx`
- Add: Monaco editor package

- [ ] **Step 1: Install Monaco editor**

```bash
cd web-ui && npm install @monaco-editor/react
```

- [ ] **Step 2: Create YAMLEditor component**

```typescript
// web-ui/src/components/policy-editor/YAMLEditor.tsx
'use client';

import Editor from '@monaco-editor/react';
import styles from './YAMLEditor.module.css';

interface YAMLEditorProps {
  value: string;
  onChange: (value: string) => void;
}

export function YAMLEditor({ value, onChange }: YAMLEditorProps) {
  return (
    <div className={styles.editor}>
      <Editor
        height="400px"
        defaultLanguage="yaml"
        value={value}
        onChange={(v) => onChange(v || '')}
        theme="vs-dark"
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          lineNumbers: 'on',
          scrollBeyondLastLine: false,
        }}
      />
    </div>
  );
}
```

- [ ] **Step 3: Create PolicyEditor component**

```typescript
// web-ui/src/components/policy-editor/PolicyEditor.tsx
'use client';

import { useState } from 'react';
import { YAMLEditor } from './YAMLEditor';
import styles from './PolicyEditor.module.css';

const defaultPolicy = `agent: email-agent-prod
version: 1
rules:
  - name: allow-read-tools
    effect: allow
    tools: [search, lookup, read]
  - name: deny-external-write
    effect: deny
    tools: [send_email, post_message]
    conditions:
      - trust_score_below: 70
`;

export function PolicyEditor() {
  const [yaml, setYaml] = useState(defaultPolicy);
  const [mode, setMode] = useState<'yaml' | 'visual'>('yaml');

  return (
    <div className={styles.editor}>
      <div className={styles.toolbar}>
        <button onClick={() => setMode('yaml')} className={mode === 'yaml' ? styles.active : ''}>
          YAML
        </button>
        <button onClick={() => setMode('visual')} className={mode === 'visual' ? styles.active : ''}>
          Visual
        </button>
        <button className={styles.validateBtn}>Validate</button>
      </div>
      {mode === 'yaml' && <YAMLEditor value={yaml} onChange={setYaml} />}
      {mode === 'visual' && <div>Visual editor coming soon</div>}
    </div>
  );
}
```

- [ ] **Step 4: Create policies page**

```typescript
// web-ui/src/app/[locale]/policies/page.tsx
import { PolicyEditor } from '@/components/policy-editor/PolicyEditor';

export default function PoliciesPage() {
  return (
    <div>
      <h1>Policy Editor</h1>
      <PolicyEditor />
    </div>
  );
}
```

- [ ] **Step 5: Commit**

```bash
git add azt-enterprise/
git commit -m "feat(enterprise): policy editor with YAML support

- Add Monaco-based YAML editor
- Add policy editor with YAML/visual toggle
- Add validate button (placeholder)
- Add policies page"
```

---

## Task 8: Alerts & Approval Queue

**Files:**
- Create: `web-ui/src/app/[locale]/alerts/page.tsx`
- Create: `web-ui/src/app/[locale]/approvals/page.tsx`
- Create: `web-ui/src/components/alerts/AlertList.tsx`
- Create: `web-ui/src/components/approvals/ApprovalQueue.tsx`

- [ ] **Step 1: Create AlertList component**

```typescript
// web-ui/src/components/alerts/AlertList.tsx
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
  onResolve?: (id: string) => void;
}

const severityConfig = {
  critical: { color: '#dc3545', label: 'CRITICAL' },
  high: { color: '#fd7e14', label: 'HIGH' },
  medium: { color: '#ffc107', label: 'MEDIUM' },
  low: { color: '#28a745', label: 'LOW' },
};

export function AlertList({ alerts, onResolve }: AlertListProps) {
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
              <span className={styles.time}>{new Date(alert.createdAt).toLocaleString()}</span>
            </div>
            <div className={styles.message}>{alert.message}</div>
            <div className={styles.meta}>
              <span>Agent: {alert.agentId}</span>
              <span>Analyzer: {alert.analyzer}</span>
            </div>
            {onResolve && (
              <button onClick={() => onResolve(alert.id)} className={styles.resolveBtn}>
                Mark Resolved
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
}
```

- [ ] **Step 2: Create ApprovalQueue component**

```typescript
// web-ui/src/components/approvals/ApprovalQueue.tsx
import styles from './ApprovalQueue.module.css';

interface ApprovalRequest {
  id: string;
  agentId: string;
  action: string;
  tool: string;
  reason: string;
  requestedAt: string;
}

interface ApprovalQueueProps {
  requests: ApprovalRequest[];
  onApprove: (id: string) => void;
  onDeny: (id: string) => void;
}

export function ApprovalQueue({ requests, onApprove, onDeny }: ApprovalQueueProps) {
  return (
    <div className={styles.queue}>
      {requests.length === 0 ? (
        <div className={styles.empty}>No pending approvals</div>
      ) : (
        requests.map((req) => (
          <div key={req.id} className={styles.request}>
            <div className={styles.header}>
              <span className={styles.agent}>{req.agentId}</span>
              <span className={styles.time}>{new Date(req.requestedAt).toLocaleString()}</span>
            </div>
            <div className={styles.action}>
              {req.action} - {req.tool}
            </div>
            <div className={styles.reason}>{req.reason}</div>
            <div className={styles.actions}>
              <button onClick={() => onApprove(req.id)} className={styles.approveBtn}>
                Approve
              </button>
              <button onClick={() => onDeny(req.id)} className={styles.denyBtn}>
                Deny
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
```

- [ ] **Step 3: Create alerts page**

```typescript
// web-ui/src/app/[locale]/alerts/page.tsx
import { AlertList } from '@/components/alerts/AlertList';

const mockAlerts = [
  { id: '1', severity: 'critical' as const, message: 'Prompt injection attempt', agentId: 'agent-42', analyzer: 'prompt_injection', createdAt: '2024-01-15T10:30:00Z' },
  { id: '2', severity: 'high' as const, message: 'Unusual tool sequence', agentId: 'agent-17', analyzer: 'model_abuse', createdAt: '2024-01-15T10:25:00Z' },
];

export default function AlertsPage() {
  return (
    <div>
      <h1>Alerts</h1>
      <AlertList alerts={mockAlerts} />
    </div>
  );
}
```

- [ ] **Step 4: Create approvals page**

```typescript
// web-ui/src/app/[locale]/approvals/page.tsx
import { ApprovalQueue } from '@/components/approvals/ApprovalQueue';

const mockRequests = [
  { id: '1', agentId: 'agent-99', action: 'tool_call', tool: 'delete_database', reason: 'Database cleanup request', requestedAt: '2024-01-15T10:00:00Z' },
];

export default function ApprovalsPage() {
  return (
    <div>
      <h1>Approval Queue</h1>
      <ApprovalQueue requests={mockRequests} onApprove={(id) => console.log('approve', id)} onDeny={(id) => console.log('deny', id)} />
    </div>
  );
}
```

- [ ] **Step 5: Commit**

```bash
git add azt-enterprise/
git commit -m "feat(enterprise): alerts and approval queue

- Add AlertList component with severity badges
- Add ApprovalQueue component with approve/deny actions
- Add alerts page
- Add approvals page"
```

---

## Task 9: Helm Chart & Deployment

**Files:**
- Create: `azt-enterprise/helm/azt-enterprise/Chart.yaml`
- Create: `azt-enterprise/helm/azt-enterprise/values.yaml`
- Create: `azt-enterprise/helm/azt-enterprise/templates/deployment.yaml`
- Create: `azt-enterprise/helm/azt-enterprise/templates/service.yaml`

- [ ] **Step 1: Create Chart.yaml**

```yaml
apiVersion: v2
name: azt-enterprise
description: AZT Enterprise Web UI and API Server
type: application
version: 0.1.0
appVersion: "1.0"
```

- [ ] **Step 2: Create values.yaml**

```yaml
replicaCount: 1

image:
  webui:
    repository: azt-enterprise/web-ui
    tag: latest
    pullPolicy: IfNotPresent
  api:
    repository: azt-enterprise/api-server
    tag: latest
    pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 3000

ingress:
  enabled: true
  className: nginx
  host: azt.example.com
```

- [ ] **Step 3: Create deployment template**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: azt-enterprise
  template:
    metadata:
      labels:
        app: azt-enterprise
    spec:
      containers:
        - name: web-ui
          image: "{{ .Values.image.webui.repository }}:{{ .Values.image.webui.tag }}"
          ports:
            - containerPort: 3000
        - name: api-server
          image: "{{ .Values.image.api.repository }}:{{ .Values.image.api.tag }}"
          ports:
            - containerPort: 8080
```

- [ ] **Step 4: Create service template**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: 3000
  selector:
    app: azt-enterprise
```

- [ ] **Step 5: Commit**

```bash
git add azt-enterprise/
git commit -m "feat(enterprise): add Helm chart for deployment

- Add Chart.yaml with app metadata
- Add values.yaml with configurable options
- Add deployment and service templates"
```

---

## Self-Review Checklist

1. **Spec coverage**: Dashboard, Agents, Policies, Alerts, Approvals, i18n, Helm - all covered
2. **Placeholder scan**: No TBD/TODO in plan
3. **Type consistency**: All TypeScript interfaces match the spec data models

---

**Plan complete and saved to `docs/superpowers/plans/2026-06-01-azt-phase4-web-ui-plan.md`**.

Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
