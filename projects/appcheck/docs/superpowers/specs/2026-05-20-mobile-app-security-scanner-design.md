# Mobile App Security Static Scanner - Design Specification

## 1. Project Overview

**Project Name:** AppScan Pro
**Project Type:** Enterprise Internal Platform (Web Application)
**Core Functionality:** Static security analysis platform for Android, iOS, and HarmonyOS mobile applications
**Target Users:** Enterprise security teams, mobile development teams, QA departments

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  Dashboard │ Scan Jobs │ Reports │ Statistics │ Settings   │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API + WebSocket
┌────────────────────────▼────────────────────────────────────┐
│                    Backend (Python FastAPI)                   │
│  Auth/ IAM │ Scan API │ Report Engine │ Stats API           │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    Task Queue (Celery + Redis)               │
│  Android Scan │ iOS Scan │ HarmonyOS Scan (Async Workers)   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              Static Analysis Engine (Python)                   │
│  APK Parser │ IPA Parser │ HAP Parser │ Security Analyzers  │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   PostgreSQL Database                        │
│  Users │ Roles │ Scan Jobs │ Results │ Reports              │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Architecture Pattern

**Frontend-Backend Separation + Task Queue**

- REST API for synchronous operations (auth, data retrieval)
- WebSocket for real-time scan progress updates
- Celery + Redis for long-running async scan tasks
- Separate worker processes for CPU-intensive static analysis

### 2.3 Technology Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Backend Framework | FastAPI | 0.104+ |
| Task Queue | Celery + Redis | Celery 5.3+ |
| Database ORM | SQLAlchemy + Alembic | 2.0+ |
| Database | PostgreSQL | 15+ |
| Static Analysis | Androguard + Custom + MobSF Integration | - |
| PDF Generation | ReportLab / WeasyPrint | - |
| DOC Generation | python-docx | - |
| Authentication | JWT + OAuth2 Password Flow | - |
| Frontend Framework | React + TypeScript | 18+ |
| UI Component Library | Ant Design | 5+ |
| State Management | Zustand / Redux Toolkit | - |
| Internationalization | i18next + react-i18next | - |
| HTTP Client | Axios | - |
| Charts | ECharts | 5+ |

## 3. Database Schema

### 3.1 Core Tables

#### users
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| username | VARCHAR(100) | UNIQUE, NOT NULL |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| role_id | UUID | FK → roles.id |
| department | VARCHAR(100) | - |
| is_active | BOOLEAN | DEFAULT TRUE |
| created_at | TIMESTAMP | DEFAULT NOW() |
| updated_at | TIMESTAMP | - |

#### roles
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| name | VARCHAR(50) | UNIQUE, NOT NULL |
| permissions | JSONB | NOT NULL |
| created_at | TIMESTAMP | DEFAULT NOW() |

#### departments
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| name | VARCHAR(100) | NOT NULL |
| parent_id | UUID | FK → departments.id (nullable) |

#### scan_jobs
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| user_id | UUID | FK → users.id |
| app_name | VARCHAR(255) | NOT NULL |
| app_version | VARCHAR(100) | - |
| platform | ENUM('android', 'ios', 'harmony') | NOT NULL |
| file_path | VARCHAR(500) | NOT NULL |
| file_size | BIGINT | - |
| file_md5 | VARCHAR(32) | - |
| status | ENUM('pending', 'uploading', 'queued', 'scanning', 'completed', 'failed') | NOT NULL |
| risk_score | DECIMAL(4,2) | - (CVSS 0.0-10.0) |
| sdk_count | INTEGER | - |
| error_message | TEXT | - |
| created_at | TIMESTAMP | DEFAULT NOW() |
| started_at | TIMESTAMP | - |
| completed_at | TIMESTAMP | - |

#### scan_results
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| job_id | UUID | FK → scan_jobs.id |
| category | VARCHAR(50) | NOT NULL |
| severity | ENUM('critical', 'high', 'medium', 'low', 'info') | NOT NULL |
| cvss_score | DECIMAL(3,1) | - (0.0-10.0) |
| cwe_id | VARCHAR(20) | - |
| title | VARCHAR(255) | NOT NULL |
| description | TEXT | - |
| details | JSONB | - |
| file_path | VARCHAR(500) | - |
| line_number | INTEGER | - |
| remediation | TEXT | - |
| is_verified | BOOLEAN | DEFAULT FALSE |
| created_at | TIMESTAMP | DEFAULT NOW() |

#### report_templates
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| name | VARCHAR(100) | NOT NULL |
| template_type | ENUM('security', 'executive', 'detailed') | NOT NULL |
| content | TEXT | HTML template content |
| is_default | BOOLEAN | DEFAULT FALSE |
| created_by | UUID | FK → users.id |
| created_at | TIMESTAMP | DEFAULT NOW() |
| updated_at | TIMESTAMP | - |

#### reports
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| job_id | UUID | FK → scan_jobs.id |
| template_id | UUID | FK → report_templates.id |
| format | ENUM('html', 'docx', 'pdf') | NOT NULL |
| file_path | VARCHAR(500) | - |
| status | ENUM('pending', 'generating', 'completed', 'failed') | NOT NULL |
| created_by | UUID | FK → users.id |
| created_at | TIMESTAMP | DEFAULT NOW() |
| completed_at | TIMESTAMP | - |

#### known_sdks
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| name | VARCHAR(100) | NOT NULL |
| category | VARCHAR(50) | - |
| version | VARCHAR(50) | - |
| risk_level | ENUM('low', 'medium', 'high', 'critical') | - |
| description | TEXT | - |
| cve_ids | JSONB | - |

### 3.2 Indexes

- `scan_jobs`: INDEX on (user_id, status), INDEX on (platform, created_at)
- `scan_results`: INDEX on (job_id, severity), INDEX on (cwe_id)
- `reports`: INDEX on (job_id, format)

## 4. Security Detection Capabilities

### 4.1 Platform Support Matrix

| Detection Category | Android | HarmonyOS | iOS |
|-------------------|---------|-----------|-----|
| **Basic Info Extraction** | | | |
| App name/version | ✅ | ✅ | ✅ |
| File size/MD5 | ✅ | ✅ | ✅ |
| SDK identification | ✅ | ✅ | ✅ |
| **Certificate & Security** | | | |
| Signing certificate info | ✅ | ✅ | ✅ |
| Certificate chain validation | ✅ | ✅ | ✅ |
| Self-signed certificate detection | ✅ | ✅ | ✅ |
| **Permissions Analysis** | | | |
| Permission manifest | ✅ | ✅ | ✅ |
| Over-privileged detection | ✅ | ✅ | ✅ |
| Sensitive permission usage | ✅ | ✅ | ✅ |
| **Sensitive Function Detection** | | | |
| JNI/Native calls | ✅ | ✅ | ✅ |
| Reflection/dynamic loading | ✅ | ✅ | ✅ |
| Crypto API usage | ✅ | ✅ | ⚠️ |
| **Data Storage** | | | |
| SharedPreferences | ✅ | ✅ | ✅ |
| SQLite databases | ✅ | ✅ | ✅ |
| File storage inspection | ✅ | ✅ | ✅ |
| Log leakage detection | ✅ | ✅ | ⚠️ |
| **Network Communication** | | | |
| HTTP/HTTPS detection | ✅ | ✅ | ✅ |
| Certificate validation bypass | ✅ | ✅ | ⚠️ |
| WebView usage | ✅ | ✅ | ⚠️ |
| **Application Behavior** | | | |
| Auto-start capability | ✅ | ✅ | ⚠️ |
| Background execution | ✅ | ✅ | ⚠️ |
| **Third-party Components** | | | |
| SDK version detection | ✅ | ✅ | ✅ |
| Known vulnerability matching | ✅ | ✅ | ✅ |

✅ Full Support | ⚠️ Partial Support / Requires Special Environment

### 4.2 Detection Categories

1. **Certificate Issues** - Invalid/expired certificates, self-signed certs, certificate chain issues
2. **Permissions** - Over-privileged permissions, dangerous permission combinations
3. **Sensitive Functions** - Crypto misuse, hardcoded secrets, native function calls
4. **Data Storage** - Insecure data storage, logging sensitive data, unencrypted databases
5. **Network Security** - Cleartext traffic, SSL bypass, insecure endpoints
6. **Code Quality** - Debug flags enabled, test code included, code obfuscation
7. **Third-party SDKs** - Known vulnerable SDK versions, privacy-invasive SDKs

## 5. CVSS Scoring System

### 5.1 Scoring Model

采用 CVSS 3.1 标准进行风险评分。

### 5.2 Severity Levels

| Level | CVSS Score | Color | Description |
|-------|------------|-------|-------------|
| Critical | 9.0 - 10.0 | Red | Immediate action required |
| High | 7.0 - 8.9 | Orange | High priority remediation |
| Medium | 4.0 - 6.9 | Yellow | Schedule remediation |
| Low | 0.1 - 3.9 | Green | Monitor/optional fix |
| None | 0.0 | Gray | No vulnerability |

### 5.3 CVSS Metric Groups

- **Attack Vector (AV):** Network, Adjacent, Local, Physical
- **Attack Complexity (AC):** Low, High
- **Privileges Required (PR):** None, Low, High
- **User Interaction (UI):** None, Required
- **Scope (S):** Unchanged, Changed
- **Impact Metrics:** Confidentiality (C), Integrity (I), Availability (A)

### 5.4 Aggregate Risk Score

Overall app risk score = Weighted average of all findings, adjusted by:
- Presence of critical findings (exponential boost)
- Number of high-severity issues
- Coverage/completeness of analysis

## 6. API Specification

### 6.1 Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | User login, returns JWT |
| POST | `/api/v1/auth/logout` | Invalidate token |
| GET | `/api/v1/auth/me` | Get current user info |
| PUT | `/api/v1/auth/password` | Change password |

### 6.2 Scan Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/scans/upload` | Upload app file (multipart/form-data) |
| GET | `/api/v1/scans` | List scan jobs (paginated, filterable) |
| GET | `/api/v1/scans/{id}` | Get scan job details |
| POST | `/api/v1/scans/{id}/start` | Trigger scan for queued job |
| DELETE | `/api/v1/scans/{id}` | Delete scan job |
| GET | `/api/v1/scans/{id}/status` | Get real-time status (supports WebSocket upgrade) |

### 6.3 Results Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/scans/{id}/results` | List all results for a scan |
| GET | `/api/v1/scans/{id}/results/{rid}` | Get detailed result |
| GET | `/api/v1/scans/{id}/summary` | Get result summary statistics |
| GET | `/api/v1/scans/{id}/risk-score` | Get detailed CVSS breakdown |

### 6.4 Reports Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/reports/templates` | List report templates |
| POST | `/api/v1/reports/templates` | Create custom template |
| PUT | `/api/v1/reports/templates/{id}` | Update template |
| POST | `/api/v1/reports/generate` | Generate report (async) |
| GET | `/api/v1/reports/{id}/download` | Download generated report |
| GET | `/api/v1/reports` | List generated reports |

### 6.5 Statistics Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/stats/overview` | Dashboard overview stats |
| GET | `/api/v1/stats/trend` | Risk score trend over time |
| GET | `/api/v1/stats/by-category` | Findings by category |
| GET | `/api/v1/stats/by-platform` | Findings by platform |

### 6.6 Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/users` | List all users |
| POST | `/api/v1/admin/users` | Create user |
| PUT | `/api/v1/admin/users/{id}` | Update user |
| DELETE | `/api/v1/admin/users/{id}` | Deactivate user |
| GET | `/api/v1/admin/roles` | List roles |
| GET | `/api/v1/admin/sdks` | List known SDKs |
| POST | `/api/v1/admin/sdks` | Add known SDK |

## 7. Frontend Design

### 7.1 Page Structure

```
AppScan Pro
├── /login                    # Login page
├── /dashboard                # Main dashboard
├── /scans                    # Scan management
│   ├── /                     # Scan list
│   ├── /new                  # New scan (upload)
│   └── /:id                  # Scan detail
│       ├── /overview         # Basic info & score
│       ├── /findings         # Security findings
│       ├── /permissions      # Permission analysis
│       ├── /components       # Third-party SDKs
│       └── /network          # Network communication
├── /reports                  # Report center
│   ├── /                     # Report list
│   ├── /templates            # Template management
│   └── /:id/preview          # Report preview
├── /statistics               # Statistics & trends
│   ├── /overview             # Overview charts
│   └── /trend                # Trend analysis
└── /settings                 # System settings
    ├── /profile              # User profile
    ├── /users                # User management (admin)
    ├── /roles                # Role management (admin)
    └── /preferences          # Language, theme
```

### 7.2 Internationalization

- **Supported Languages:** English (en), Chinese Simplified (zh-CN)
- **Framework:** i18next + react-i18next
- **Implementation:** All UI strings externalized to JSON locale files
- **Language Switching:** Real-time switch without page reload
- **Default:** Browser language detection with fallback to English

### 7.3 Key UI Components

1. **Dashboard**
   - Scan statistics cards (total, completed, in-progress, failed)
   - Risk distribution pie chart
   - Recent scans table with status badges
   - Quick actions (new scan, view reports)

2. **Scan Detail**
   - App info card (name, version, platform, size, MD5)
   - Risk score gauge (CVSS 0-10)
   - Severity breakdown bar chart
   - Filterable/sortable findings table
   - Category tabs for different analysis views

3. **Report Viewer**
   - Format selector (HTML/DOCX/PDF)
   - Preview pane
   - Download button
   - Share functionality

## 8. Scanner Engine Design

### 8.1 Analysis Pipeline

```
Upload File → Format Detection → Extraction → Analysis → Reporting
     │              │               │           │           │
     ▼              ▼               ▼           ▼           ▼
  Storage    File Type Parse   Binary/XML   Security   Results +
                           Decomposition  Analyzers   Reports
```

### 8.2 Android Analysis (APK)

1. **File Extraction**
   - Unzip APK (standard zip format)
   - Parse AndroidManifest.xml (binary XML format)
   - Extract DEX files for code analysis
   - Extract resources (.arsc, .so files)

2. **Static Analysis**
   - Manifest analysis (permissions, components, intent-filters)
   - DEX disassembly and Smali conversion
   - String extraction and secret scanning
   - Native library analysis (ELF format)
   - Certificate analysis (CERT.RSA/CERT.SF)

3. **Security Checks**
   - Permission misuse detection
   - Component export analysis
   - Deep link validation
   - Crypto usage patterns
   - Hardcoded credentials detection

### 8.3 HarmonyOS Analysis (HAP)

- HAP format is similar to APK (compressed archive)
- Similar extraction process to Android
- HarmonyOS-specific manifest format (config.json)
- Custom permission model analysis

### 8.4 iOS Analysis (IPA)

1. **Environment Requirement**
   - Remote Mac service with Apple tools
   - IPA is actually a zip archive
   - Requires macOS for symbolication and deep analysis

2. **Analysis Process**
   - Extract IPA contents (without Mac)
   - Parse Info.plist (property list)
   - Basic binary analysis of compiled code
   - Remote Mac service for advanced analysis (class-dump, etc.)

### 8.5 Third-party Tool Integration

- **MobSF:** Integrated for additional Android analysis rules
- **AMEFeng (Android):** For malware detection patterns
- **Custom Rules:** Organization-specific security policies

## 9. Report Generation

### 9.1 Supported Formats

| Format | Use Case | Generation |
|--------|----------|------------|
| HTML | Web viewing, inline images | Jinja2 template → HTML |
| DOCX | Word editing, corporate templates | python-docx API | 
| PDF | Official reports, archival | HTML → WeasyPrint → PDF |

### 9.2 Report Templates

1. **Security Executive Summary**
   - High-level risk assessment
   - Critical findings only
   - Remediation priorities

2. **Detailed Technical Report**
   - Complete findings with code snippets
   - CVSS scoring details
   - Step-by-step remediation

3. **Comparison Report**
   - Multiple app versions comparison
   - Trend analysis over time

### 9.3 Report Features

- Custom branding (logo, colors)
- Executive summary vs technical details toggle
- Appendix with raw data
- Automated report scheduling

## 10. Deployment Architecture

### 10.1 Container Layout

```
┌──────────────────────────────────────────────┐
│                  Docker Compose                │
├──────────────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────────┐   │
│  │  Nginx  │ │ Backend │ │   Worker    │   │
│  │ (Proxy) │ │ (API)   │ │ (Celery)    │   │
│  └─────────┘ └─────────┘ └─────────────┘   │
│  ┌─────────┐ ┌─────────┐ ┌─────────────┐   │
│  │   Redis │ │   DB    │ │  MinIO/S3   │   │
│  │ (Queue) │ │ (PG)    │ │  (Files)    │   │
│  └─────────┘ └─────────┘ └─────────────┘   │
└──────────────────────────────────────────────┘
```

### 10.2 Environment Variables

```
# Database
DATABASE_URL=postgresql://user:pass@db:5432/appcheck

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
JWT_SECRET_KEY=<generated>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# File Storage
STORAGE_TYPE=local  # or s3
STORAGE_PATH=/data/uploads

# iOS Analysis (optional)
IOS_ANALYSIS_ENABLED=true
IOS_MAC_HOST=mac-service.internal
IOS_MAC_API_KEY=<key>

# Optional: MobSF Integration
MOBSF_URL=http://mobsf:8000
MOBSF_API_KEY=<key>
```

## 11. Development Phases

### Phase 1: Foundation (4-6 weeks)
- Project scaffolding (backend + frontend)
- Database schema and migrations
- User authentication system
- Basic file upload functionality
- **Deliverable:** Working backend with user auth, no scanning

### Phase 2: Android Scanner (6-8 weeks)
- Android APK parsing
- Manifest analysis
- Permission analysis
- Basic security checks
- Results storage and display
- **Deliverable:** Android APK scanning with basic security findings

### Phase 3: HarmonyOS + Advanced Android (4-6 weeks)
- HarmonyOS HAP support
- Enhanced Android analysis (native code, crypto)
- CVSS scoring implementation
- **Deliverable:** Multi-platform support with scoring

### Phase 4: iOS Support (4-6 weeks)
- Remote Mac service integration
- IPA analysis (basic + advanced via Mac)
- **Deliverable:** iOS support (requires Mac infrastructure)

### Phase 5: Reporting (3-4 weeks)
- Report template system
- HTML/DOCX/PDF generation
- Report scheduling
- **Deliverable:** Complete reporting system

### Phase 6: Polish & Enterprise Features (3-4 weeks)
- Advanced statistics
- User management improvements
- Performance optimization
- **Deliverable:** Production-ready platform

**Total Estimated:** 24-30 weeks

## 12. Acceptance Criteria

### 12.1 Core Functionality
- [ ] User can register, login, logout
- [ ] User can upload APK/IPA/HAP files
- [ ] System correctly extracts app metadata (name, version, size, MD5)
- [ ] System identifies and counts third-party SDKs
- [ ] Scan results stored and retrievable
- [ ] CVSS scoring calculated correctly

### 12.2 Security Detection
- [ ] Certificate issues detected
- [ ] Over-privileged permissions flagged
- [ ] Sensitive function calls identified
- [ ] Insecure data storage detected
- [ ] Network security issues found
- [ ] Known vulnerable SDKs matched

### 12.3 Reporting
- [ ] HTML report generation works
- [ ] DOCX report generation works
- [ ] PDF report generation works
- [ ] Reports downloadable

### 12.4 UI/UX
- [ ] English interface fully translated
- [ ] Chinese interface fully translated
- [ ] Language switch works without reload
- [ ] Dashboard displays correct statistics
- [ ] Scan results viewable with filtering/sorting

### 12.5 Enterprise Features
- [ ] Role-based access control works
- [ ] Multi-user concurrent access supported
- [ ] Scan history preserved
- [ ] Reports accessible by authorized users only

## 13. Out of Scope (v1)

The following are intentionally deferred to future versions:

- Real-time dynamic analysis (not static)
- Malware behavioral analysis sandbox
- App source code decompilation (beyond necessary)
- Direct integration with app stores for automated download
- Mobile device management (MDM) integration
- Compliance report generation (PCI-DSS, GDPR, etc.)
- Team collaboration features (comments, assignments)
- Integration with CI/CD pipelines
- API access for third-party tools
