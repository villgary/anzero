# AZT Framework — Zero Trust Security for AI Agents

## Overview

**AZT** (Agent Zero Trust) is a production security framework for protecting AI agents across enterprise deployments. The framework implements Google's Zero Trust for AI Agents model with four integrated pillars: Policy Engine, Trust Scoring, Threat Shield, and Audit Logging.

### Goals

- Protect AI agents (LangGraph, CrewAI, custom LLM apps, autonomous SaaS agents)
- Deploy as hybrid: embedded library + centralized gateway
- Target enterprise customers deploying to Kubernetes
- Open source core framework, proprietary enterprise control plane on top

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Enterprise App                           │
│  (Proprietary: Web UI, Reports, Multi-tenancy, Compliance)       │
├─────────────────────────────────────────────────────────────────┤
│                     AZT Framework (Open Source)                  │
│                                                                 │
│  ┌─────────────────┐         ┌─────────────────────────────┐   │
│  │   Python SDK    │◄──────►│       Go Gateway            │   │
│  │  (Embedded in   │  gRPC   │  - Policy Engine (OPA)      │   │
│  │   Agent)        │         │  - Trust Scoring Service   │   │
│  └─────────────────┘         │  - Threat Shield             │   │
│                              │  - Audit Logger              │   │
│                              │  - GitOps Sync              │   │
│                              └─────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ deploys to ▼
┌─────────────────────────────────────────────────────────────────┐
│               Customer's Kubernetes Cluster                      │
└─────────────────────────────────────────────────────────────────┘
```

### Components

#### Python SDK (`azt-sdk-python`)
- Embedded in the AI agent's runtime
- Intercepts agent actions (tool calls, prompts, outputs)
- Communicates with Go Gateway via gRPC
- Supports sync (high-risk) and async (low-risk) enforcement

#### Go Gateway (`azt-gateway`)
- Centralized control plane
- Hosts all four pillars
- Exposes REST/gRPC API for policy management
- Deploys as Kubernetes Deployment + Service

---

## Four Pillars

### 1. Policy Engine

**Technology**: OPA (Open Policy Agent) + custom YAML rules

**Policy Structure**:
```yaml
# Example: azt-policy.yaml
agent: email-agent-prod
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
  - name: require-human-approval
    effect: deny
    actions: [delete_data, export_user_info]
    conditions:
      - risk_level: high
```

**Flow**:
1. SDK sends action context (agent_id, tool, parameters, trust_score) to gateway
2. Gateway evaluates against OPA policies + YAML rules
3. Decision (allow/deny/require_approval) returned to SDK

### 2. Trust Scoring

**Scoring Factors**:
- Agent identity verification (SPIFFE workload identity)
- Historical behavior pattern
- Time-of-day and access patterns
- Contextual anomalies
- Tool usage frequency

**Score Range**: 0–100 (default starts at 70)

**Flow**:
1. Each action updates the agent's trust score
2. Trust score feeds into Policy Engine decisions
3. Scores below threshold trigger enhanced verification or async-only mode

### 3. Threat Shield

**Capabilities**:
- Prompt injection detection
- Output filtering for sensitive data
- Model-agnostic (works regardless of LLM provider)
- Real-time interception of harmful outputs

**Integration**:
- Intercepts outputs after model response, before returning to agent
- Sync mode: blocks harmful outputs immediately
- Async mode: logs and alerts, allows action to complete

### 4. Audit Logging

**Logged Events**:
- All policy decisions (request, context, decision, reason)
- Trust score changes
- Threat Shield detections
- Human-in-the-loop approvals/denials

**Format**: Structured JSON logs → Kubernetes events + persistent storage

**Retention**: Configurable, enterprise customers choose retention policy

---

## Communication Patterns

| Action Risk | Pattern | Latency | Use Case |
|-------------|---------|---------|----------|
| High (delete, write, external) | Synchronous | ~50-100ms | Sync enforcement |
| Low (read, query) | Asynchronous | ~5-10ms | Async audit + score |

**Trust Score Thresholds**:
- 80–100: Full sync enforcement
- 60–79: Sync for high-risk, async for low-risk
- Below 60: All actions require human approval or are denied

---

## Policy Management

### GitOps Workflow

```
Developer writes YAML policy
         │
         ▼
    PR submitted to Git repo
         │
         ▼
   Policy reviewed (code review)
         │
         ▼
    Policy merged to main
         │
         ▼
   Gateway syncs via GitOps operator
         │
         ▼
   Active policy in cluster
```

### Web UI

- Reads/writes YAML policies directly
- Validates YAML against schema before save
- Shows visual representation of policy rules
- Non-technical users can view/understand, Git is source of truth
- No separate policy database — operates on Git files

### Internationalization (i18n)

**Supported Languages**:
| Language | Code | Direction |
|----------|------|-----------|
| English | `en` | LTR |
| Chinese (Simplified) | `zh` | LTR |
| Japanese | `ja` | LTR |
| French | `fr` | LTR |
| Arabic | `ar` | RTL |

**i18n Architecture**:
- All user-facing strings externalized to translation files (JSON format)
- RTL support for Arabic via CSS logical properties and `dir` attribute
- Language detection: browser preference → user setting → fallback to English
- Number/date formatting via locale-aware libraries (Intl API)
- Language switcher in UI header, persisted to user preferences

**Translation Files**: `web-ui/src/locales/{en,zh,ja,fr,ar}.json`

---

## Data Flow: Action Enforcement

```
1. Agent calls tool
         │
         ▼
2. SDK captures action context
         │
         ▼
3. SDK sends to Gateway (sync or async based on action type)
         │
         ▼
4. Gateway:
   a) Evaluates Trust Score
   b) Runs Policy Engine check
   c) Threat Shield scans output/context
   d) Logs decision to Audit
         │
         ▼
5. Gateway returns: ALLOW | DENY | REQUIRE_APPROVAL
         │
         ▼
6. SDK enforces decision:
   - ALLOW: proceed with tool call
   - DENY: block and return error
   - REQUIRE_APPROVAL: pause, send to human-in-the-loop queue
```

---

## Project Structure

```
anzero/
├── azt-framework/              # Open source framework
│   ├── azt-sdk-python/         # Python SDK (embeddable)
│   │   ├── azt/
│   │   │   ├── __init__.py
│   │   │   ├── client.py       # gRPC client
│   │   │   ├── enforce.py      # Enforcement logic
│   │   │   ├── config.py        # SDK configuration
│   │   │   └── models.py        # Data models
│   │   └── pyproject.toml
│   │
│   ├── azt-gateway/            # Go gateway
│   │   ├── cmd/
│   │   │   └── gateway/
│   │   │       └── main.go
│   │   ├── internal/
│   │   │   ├── policy/         # OPA integration
│   │   │   ├── trust/          # Trust scoring
│   │   │   ├── shield/         # Threat shield
│   │   │   ├── audit/          # Audit logging
│   │   │   ├── gitops/         # GitOps sync
│   │   │   └── grpc/           # gRPC server
│   │   └── go.mod
│   │
│   └── policies/               # Example policies
│       └── azt-policy.yaml
│
├── azt-enterprise/             # Proprietary enterprise app
│   ├── web-ui/                 # React dashboard
│   │   └── src/
│   │       └── locales/        # i18n translation files
│   │           ├── en.json
│   │           ├── zh.json
│   │           ├── ja.json
│   │           ├── fr.json
│   │           └── ar.json
│   ├── api-server/             # Go REST API
│   ├── multi-tenancy/          # Tenant isolation
│   └── compliance/             # Compliance reports
│
└── docs/
    └── superpowers/
        └── specs/
            └── 2026-05-31-azt-framework-design.md
```

---

## Implementation Phases

### Phase 1: Foundation
- Python SDK skeleton + gRPC client
- Go Gateway skeleton + gRPC server
- Basic Policy Engine (OPA + YAML rules)
- Audit logging (structured JSON)
- Sync communication only

### Phase 2: Trust & Context
- Trust Scoring service (basic factors)
- Trust score integration in Policy Engine
- Async communication path
- Example policies and tutorials

### Phase 3: Shield & Protection
- Threat Shield implementation
- Prompt injection detection patterns
- Output filtering
- Real-time alerts

### Phase 4: Enterprise
- Web UI for policy management
- **i18n support** (English, Chinese, Japanese, French, Arabic with RTL)
- Multi-tenancy
- Compliance reporting
- Human-in-the-loop approval workflow

---

## Open Questions / Future Decisions

- [ ] Specific OPA Rego rule templates for common AI agent threat patterns
- [ ] Trust scoring algorithm weights (future tuning with customer feedback)
- [ ] gRPC vs REST for SDK-gateway communication
- [ ] Helm chart vs Operator for Kubernetes deployment
- [ ] Managed SaaS vs on-prem licensing model
