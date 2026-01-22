# 🏛️ Reliquary of Truth

**A proof-gated, auditable AI software engineering system with organizational memory and human oversight.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2+-blue.svg)](https://reactjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Core Principle**: No proof → no delivery.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#️-architecture)
- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Workflow](#-workflow)
- [API Documentation](#-api-documentation)
- [Dashboard](#-dashboard)
- [Configuration](#️-configuration)
- [Examples](#-examples)
- [Storage Structure](#-storage-structure)
- [Security](#-security)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

The **Reliquary of Truth** is an AI-powered software engineering system that enforces real engineering discipline. Every code change must be backed by **proof** (passing tests, audit logs, evidence artifacts).

### Why Reliquary?

Modern AI coding tools generate code quickly but struggle with:
- ❌ Knowing when requirements are incomplete
- ❌ Verification and ownership
- ❌ Audit trails and accountability

Reliquary solves this through:
- ✅ **Structured intake**: Parse tasks into tickets with acceptance criteria
- ✅ **Single-owner execution**: One AI agent owns the entire implementation
- ✅ **Test-based verification**: Code must pass tests before delivery
- ✅ **Proof-backed delivery**: Every delivery includes evidence artifacts
- ✅ **Organizational memory**: Learn from past successes and failures
- ✅ **Human oversight**: Dashboard with approval workflows

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    RELIQUARY OF TRUTH                       │
│                  Proof-Gated AI System                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │         WORKFLOW ENGINE               │
        │         (LangGraph State)             │
        └───────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌───────────────┐                     ┌───────────────┐
│   AI AGENTS   │                     │   STORAGE     │
├───────────────┤                     ├───────────────┤
│ • Owner       │                     │ • File-based  │
│ • Helpers     │                     │ • SQLite DB   │
│ • Reviewer    │                     │ • Audit Log   │
└───────────────┘                     └───────────────┘
        │                                       │
        └───────────────────┬───────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌───────────────┐                     ┌───────────────┐
│  DELIVERY     │                     │  GOVERNANCE   │
├───────────────┤                     ├───────────────┤
│ • Local Patch │                     │ • Policies    │
│ • GitHub PR   │                     │ • Security    │
│ • Direct Push │                     │ • Risk Class  │
└───────────────┘                     └───────────────┘
        │                                       │
        └───────────────────┬───────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │         HUMAN INTERFACE               │
        │     (API + React Dashboard)           │
        └───────────────────────────────────────┘
```

---

## ✨ Features

### 🎯 Phase 1-2: Core Proof-Gated Workflow
- **Intake**: Parse tasks into structured tickets with acceptance criteria
- **Planning**: Multi-step implementation plans
- **Implementation**: AI-generated patches with specialist help system
- **Verification**: Test-based proof of correctness
- **Decision Logging**: Complete audit trail with actor attribution

### 📦 Phase 3: Delivery & Auditability
- **Proof Bundling**: ZIP archives with evidence.json, decision_log.json, test outputs
- **Multiple Delivery Modes**:
  - Local patch (default)
  - GitHub PR with proof in description
  - Direct push to branch
- **Immutable Audit Log**: Hash-chained event trail with integrity verification
- **GitHub Integration**: Automated PR creation with proof artifacts

### 🧠 Phase 4: Organizational Memory & Learning
- **SQLite Memory Store**: Fast indexed run history
- **Pattern Matching**: Find similar successful/failed tasks
- **Advisory System**: Recommendations based on past runs
- **Statistics**: Success rates, failure modes, average attempts
- **Query Interface**: CLI commands for memory exploration

### 🛡️ Phase 5: Safety, Policy & Governance
- **Policy Engine**: Declarative JSON-based rules
  - Gate rules (block delivery)
  - Warning rules (flag for review)
  - Audit rules (log for compliance)
- **Risk Classification**: Detects auth, migration, critical path changes
- **Security Scanning**:
  - Pattern-based secret detection
  - Bandit SAST integration
  - Blocks delivery on critical findings
- **Workflow Gates**: Automatic blocking of unsafe changes

### 👥 Phase 6: Human Interface & Operations
- **FastAPI REST API**: 8+ endpoints for run management
- **React Dashboard**: Web UI with run list, evidence viewer, decision log
- **Human-in-the-Loop**: Approve/reject high-risk changes
- **Multi-Repo Support**: Filter and aggregate by repository

---

## 📦 Installation

### Prerequisites
- Python 3.10+
- Node.js 16+ (for dashboard)
- Git
- OpenAI API key

### Backend Setup

```bash
# Clone repository
cd reliquary-engine

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate
# OR Unix/Mac
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Create .env file with:
OPENAI_API_KEY=sk-...
GITHUB_TOKEN=ghp_...  # Optional, for PR creation
```

### Frontend Setup (Optional)

```bash
cd reliquary/dashboard/web
npm install
```

---

## 🚀 Quick Start

### 1. Run a Basic Task

```bash
python -m reliquary run \
  --repo ../your-repo \
  --task "Add a /health endpoint that returns {status: ok}"
```

**Output:**
```
Reliquary of Truth — Run Complete
Work Item: abc123
Status: DELIVERED

Delivered with proof
- Tests run count: 1
- Last test exit code: 0
- Proof Bundle: runs/abc123_20260121/proof_bundle.zip
```

### 2. Deliver via GitHub PR

```bash
# Set GitHub token
export GITHUB_TOKEN=ghp_your_token_here

python -m reliquary run \
  --repo ../your-repo \
  --task "Add user authentication with JWT" \
  --delivery-mode github_pr \
  --target-branch main
```

### 3. Query Organizational Memory

```bash
# View all past runs
python -m reliquary query

# Filter by status
python -m reliquary query --status DELIVERED

# View statistics
python -m reliquary stats
```

Output:
```
Reliquary Memory Statistics

Total Runs: 25
Successful Runs: 20
Success Rate: 80.0%
Average Attempts: 2.1

Failure Modes:
  tests_failed: 3
  max_attempts_exceeded: 2
```

### 4. Start API Server & Dashboard

```bash
# Terminal 1: Start API
python -m uvicorn reliquary.api.server:app --reload

# Terminal 2: Start Dashboard (optional)
cd reliquary/dashboard/web
npm run dev
```

**Access:**
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:3000

---

## 🔄 Workflow

### Complete Workflow Diagram

```
┌──────────┐
│  START   │
│  (Task)  │
└────┬─────┘
     │
     ▼
┌─────────────────┐
│   1. INTAKE     │  Parse task → TicketSpec
│   Agent: owner  │  • Validate requirements
└────┬────────────┘  • Identify domain tags
     │
     │ needs_info?
     ├─────YES──────► NEEDS_INFO (END)
     │
     NO
     ▼
┌─────────────────┐
│  2. PLANNING    │  Create implementation plan
│  Agent: owner   │  • Consult memory (Phase 4)
└────┬────────────┘  • Get advice from past runs
     │
     ▼
┌─────────────────┐
│ 3. POLICY_CHECK │  Evaluate policies (Phase 5)
│ System          │  • Check risk factors
└────┬────────────┘  • Enforce rules (gate/warn/audit)
     │
     │ violation?
     ├─────YES──────► BLOCKED (END)
     │
     NO
     ▼
┌─────────────────┐
│ 4. IMPLEMENT    │  Generate code patch
│ Agent: owner    │  • Create unified diff
└────┬────────────┘  • Request specialist help if needed
     │
     │ need_help?
     ├─────YES──────┐
     │               │
     NO              ▼
     │         ┌─────────────┐
     │         │  5. HELP    │  Domain specialists
     │         │  Helpers    │  • Backend/Frontend/DB experts
     │         └──────┬──────┘
     │                │
     │◄───────────────┘
     │
     │ max_attempts?
     ├─────YES──────► BLOCKED (END)
     │
     NO
     ▼
┌─────────────────┐
│ 6. SECURITY_SCAN│  Scan for secrets (Phase 5)
│ System          │  • Pattern matching for API keys, passwords
└────┬────────────┘  • Bandit SAST (if installed)
     │
     │ critical findings?
     ├─────YES──────► BLOCKED (END)
     │
     NO
     ▼
┌─────────────────┐
│  7. VERIFY      │  🔐 PROOF GATE
│  System         │  • Apply patch to repo
└────┬────────────┘  • Run test suite
     │               • Collect evidence artifacts
     │
     │ tests_passed?
     ├─────NO───────► Loop back to IMPLEMENT
     │
     YES
     ▼
┌─────────────────┐
│  8. DELIVER     │  Deliver with proof (Phase 3)
│  System         │  • Bundle proof artifacts (ZIP)
└────┬────────────┘  • Create PR / Save patch
     │               • Log to immutable audit trail
     │               • Index to memory DB (Phase 4)
     ▼
┌──────────┐
│   END    │
│ DELIVERED│
└──────────┘
```

### Workflow States

| State | Description | Terminal? |
|-------|-------------|-----------|
| `INTAKE` | Parsing task into ticket | No |
| `NEEDS_INFO` | Awaiting human clarification | **Yes** |
| `PLANNING` | Creating implementation plan | No |
| `POLICY_CHECK` | Evaluating policies | No |
| `IMPLEMENTING` | Generating code patch | No |
| `NEED_HELP` | Requesting specialist help | No |
| `SECURITY_SCAN` | Scanning for security issues | No |
| `VERIFYING` | Running tests (proof gate) | No |
| `DELIVERING` | Creating delivery | No |
| `DELIVERED` | Successfully delivered with proof | **Yes** |
| `BLOCKED` | Cannot proceed safely | **Yes** |

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### Health Check
```bash
GET /
```
**Response:**
```json
{"message": "Reliquary of Truth API", "version": "1.0.0"}
```

#### List Runs
```bash
GET /runs?repo={repo}&status={status}&limit={limit}
```
**Parameters:**
- `repo`: Filter by repository name (optional)
- `status`: Filter by status (optional)
- `limit`: Max results (default: 50)

**Response:**
```json
{
  "runs": [
    {
      "work_item_id": "abc123",
      "repo_name": "demo-repo",
      "task_raw": "Add feature X",
      "ticket_title": "Add feature X",
      "final_status": "DELIVERED",
      "implement_attempts": 2,
      "test_exit_code": 0,
      "completed_at": "2026-01-21T10:30:00",
      "failure_mode": null
    }
  ],
  "count": 1
}
```

#### Get Run Details
```bash
GET /runs/{work_item_id}
```

#### Get Evidence
```bash
GET /runs/{work_item_id}/evidence
```
**Response:**
```json
{
  "test_runs": [
    {
      "command": "pytest",
      "exit_code": 0,
      "stdout_path": "runs/abc123/artifacts/pytest_attempt_1.stdout.txt",
      "stderr_path": "runs/abc123/artifacts/pytest_attempt_1.stderr.txt"
    }
  ]
}
```

#### Get Decision Log
```bash
GET /runs/{work_item_id}/decision_log
```

#### Provide Information (HITL)
```bash
POST /runs/{work_item_id}/provide_info
Content-Type: application/json

{"answer": "Use FastAPI for the REST API"}
```

#### Approve/Reject Run (HITL)
```bash
POST /runs/{work_item_id}/approve
Content-Type: application/json

{"approved": true, "reason": "Looks good to me"}
```

#### Get Statistics
```bash
GET /stats
```
**Response:**
```json
{
  "total_runs": 25,
  "successful_runs": 20,
  "success_rate": 80.0,
  "avg_attempts": 2.1,
  "failure_modes": {
    "tests_failed": 3,
    "max_attempts_exceeded": 2
  }
}
```

### API Testing

```bash
# Test API is running
curl http://localhost:8000/

# Get statistics
curl http://localhost:8000/stats

# List all runs
curl http://localhost:8000/runs | jq
```

---

## 🎨 Dashboard

### Features

**Run List** - Color-coded by status:
- 🟢 **Green**: DELIVERED (tests passed, proof bundled)
- 🔴 **Red**: BLOCKED (failed policy/security/max attempts)
- 🟡 **Yellow**: NEEDS_INFO (awaiting human input)
- 🔵 **Blue**: In progress

**Statistics Panel**:
- Total runs
- Success rate percentage
- Average implementation attempts
- Failure mode breakdown

**Run Detail View**:
- Evidence viewer with syntax highlighting
- Decision log timeline with actor attribution
- Delivery information (PR URL, patch location)
- Proof bundle download link

### Dashboard Layout

```
┌─────────────────────────────────────────────────────────────┐
│  🏛️ Reliquary of Truth Dashboard                           │
├─────────────────────────────────────────────────────────────┤
│  📊 Statistics                                              │
│  ┌────────┬────────┬────────┬────────┐                     │
│  │   15   │   12   │  80.0% │  2.3   │                     │
│  │ Total  │Success │Success │  Avg   │                     │
│  │ Runs   │ Runs   │ Rate   │Attempts│                     │
│  └────────┴────────┴────────┴────────┘                     │
│                                                             │
│  📋 Recent Runs                                             │
│  ┌──────────┬──────────┬──────────────┬────┬───────────┐  │
│  │ Status   │ Work Item│ Title        │Att │ Completed │  │
│  ├──────────┼──────────┼──────────────┼────┼───────────┤  │
│  │🟢DELIVERED│ abc123   │Add /users API│ 2  │ 10:30 AM  │  │
│  │🔴BLOCKED  │ def456   │Add auth      │ 4  │ 11:15 AM  │  │
│  │🟢DELIVERED│ ghi789   │Fix bug #42   │ 1  │ 02:45 PM  │  │
│  └──────────┴──────────┴──────────────┴────┴───────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file:

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional - GitHub Integration
GITHUB_TOKEN=ghp_...

# Optional - Database
RELIQUARY_DB_PATH=memory.db

# Optional - Policy Version
RELIQUARY_POLICY_VERSION=v1.0
```

### Policy Configuration

Edit `policies/v1.0.json`:

```json
{
  "version": "1.0",
  "description": "Default Reliquary policies",
  "rules": [
    {
      "rule_id": "no_auth_without_tests",
      "name": "Auth changes require tests",
      "rule_type": "gate",
      "condition": "risk_factors['modifies_auth'] and len(evidence.test_runs) == 0",
      "action": "block"
    },
    {
      "rule_id": "large_changes_warning",
      "name": "Large changes should be reviewed",
      "rule_type": "warning",
      "condition": "risk_factors['large_change']",
      "action": "warn"
    },
    {
      "rule_id": "migration_safety",
      "name": "Migration changes require careful review",
      "rule_type": "warning",
      "condition": "risk_factors['modifies_migrations']",
      "action": "warn"
    }
  ]
}
```

**Rule Types:**
- `gate`: Must pass or delivery is blocked
- `warning`: Flags for human review
- `audit`: Logged for compliance only

**Actions:**
- `block`: Prevent delivery
- `warn`: Show warning to user
- `log`: Audit trail only

---

## 📚 Examples

### Example 1: Simple Feature Addition

```bash
python -m reliquary run \
  --repo ../my-api \
  --task "Add a GET /users endpoint that returns all users from the database"
```

**Output:**
```
Reliquary of Truth — Run Complete
Work Item: abc123
Status: DELIVERED

Delivered with proof
- Tests run count: 1
- Last test exit code: 0
- stdout: runs/abc123_20260121/artifacts/pytest_attempt_1.stdout.txt

Delivery Details:
- Mode: local_patch
- Status: delivered
- Patch: runs/abc123_20260121/artifacts/change.patch
- Proof Bundle: runs/abc123_20260121/proof_bundle.zip
```

### Example 2: GitHub PR Creation

```bash
export GITHUB_TOKEN=ghp_your_token_here

python -m reliquary run \
  --repo ../my-api \
  --task "Add JWT authentication middleware" \
  --delivery-mode github_pr \
  --target-branch main
```

**Output:**
```
Reliquary of Truth — Run Complete
Work Item: def456
Status: DELIVERED

Delivery Details:
- Mode: github_pr
- Status: delivered
- PR URL: https://github.com/user/my-api/pull/42
- PR Number: 42
- Proof Bundle: runs/def456_20260121/proof_bundle.zip
```

### Example 3: Query Memory

```bash
# View all delivered runs
python -m reliquary query --status DELIVERED --limit 5

# Output:
Found 5 runs:

DELIVERED abc123: Add GET /users endpoint
  Repo: my-api | Attempts: 1 | Completed: 2026-01-21T10:30:00

DELIVERED def456: Add JWT authentication
  Repo: my-api | Attempts: 2 | Completed: 2026-01-21T11:15:00

DELIVERED ghi789: Fix CORS headers
  Repo: my-api | Attempts: 1 | Completed: 2026-01-21T14:20:00
```

### Example 4: Statistics

```bash
python -m reliquary stats
```

**Output:**
```
Reliquary Memory Statistics

Total Runs: 25
Successful Runs: 20
Success Rate: 80.0%
Average Attempts: 2.1

Failure Modes:
  tests_failed: 3
  max_attempts_exceeded: 2
```

---

## 📊 Storage Structure

```
reliquary-engine/
├── runs/                              # All run data
│   └── {work_item_id}_{timestamp}/
│       ├── state_before_verify.json   # State snapshot
│       ├── evidence.json              # Test results
│       ├── decision_log.json          # All decisions
│       ├── help_requests.json         # Help requests
│       ├── help_responses.json        # Help responses
│       ├── delivery_result.json       # Delivery info (Phase 3)
│       ├── proof_bundle.zip           # All artifacts (Phase 3)
│       ├── audit_events.jsonl         # Immutable audit log (Phase 3)
│       └── artifacts/
│           ├── change.patch           # Unified diff
│           ├── git.diff.txt          # Git diff
│           └── pytest_*.stdout.txt   # Test outputs
│
├── memory.db                          # SQLite index (Phase 4)
│
├── policies/                          # Policy rules (Phase 5)
│   └── v1.0.json
│
└── reliquary/
    ├── agents/                        # AI agents (owner, helpers, reviewer)
    ├── delivery/                      # Delivery engine (Phase 3)
    ├── memory/                        # Memory & learning (Phase 4)
    ├── policy/                        # Policy engine (Phase 5)
    ├── security/                      # Security scanners (Phase 5)
    ├── api/                           # REST API (Phase 6)
    ├── human/                         # HITL handlers (Phase 6)
    └── dashboard/                     # React UI (Phase 6)
```

---

## 🔐 Security

### Built-in Security Features

1. **Secret Detection**: Pattern-based scanning for:
   - API keys (`api_key`, `apikey`)
   - Passwords (`password`, `passwd`, `pwd`)
   - Tokens (`token`, `auth_token`)
   - Private keys (PEM format)
   - AWS credentials (`AKIA...`)

2. **Bandit Integration**: Python SAST tool (optional)
   ```bash
   pip install bandit
   ```

3. **Policy Enforcement**: Blocks unsafe changes
   - Auth changes without tests
   - Large changes (>500 lines)
   - Migration changes

4. **Audit Trail**: Cryptographically signed event log
   - Hash chaining prevents tampering
   - Integrity verification available

### Security Best Practices

✅ **DO:**
- Use environment variables for secrets
- Review PR descriptions before merging
- Verify audit log integrity regularly
- Enable policy gates for critical paths

❌ **DON'T:**
- Commit `.env` files
- Skip security scans
- Modify audit_events.jsonl manually
- Store secrets in code

---

## 🚫 Non-Goals

- Replacing human engineers
- One-shot code generation
- Maximizing speed over correctness
- Solving ambiguous requirements silently

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install dev dependencies
pip install pytest black flake8 mypy

# Run tests
pytest tests/

# Format code
black reliquary/

# Lint
flake8 reliquary/

# Type check
mypy reliquary/
```

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🗺️ Roadmap

### Completed ✅
- [x] Phase 1-2: Core proof-gated workflow
- [x] Phase 3: Delivery & auditability
- [x] Phase 4: Organizational memory
- [x] Phase 5: Policy & governance
- [x] Phase 6: Human interface

### Planned 🚧
- [ ] Docker deployment configuration
- [ ] Slack/email notifications for human input
- [ ] Webhook integration (PR comments, issue creation)
- [ ] Advanced pattern matching with embeddings
- [ ] Cost tracking (LLM token usage)
- [ ] Rollback mechanism
- [ ] Multi-repo orchestration
- [ ] Policy editor UI
- [ ] Audit report generator (PDF)

---

## 📞 Support

- **Documentation**: See [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
- **Technical Details**: See [PHASES_3-6_SUMMARY.md](PHASES_3-6_SUMMARY.md)
- **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Roadmap**: See [ROADMAP.md](ROADMAP.md)

---

## 🙏 Acknowledgments

- **LangGraph**: Workflow orchestration framework
- **LangChain**: Agent framework and tooling
- **FastAPI**: High-performance API framework
- **React**: UI framework
- **OpenAI**: LLM provider

---

## 📸 Quick Reference

### CLI Commands

```bash
# Run a task
python -m reliquary run --repo ../repo --task "Add feature"

# With GitHub PR
python -m reliquary run --repo ../repo --task "Add feature" \
  --delivery-mode github_pr --github-token $GITHUB_TOKEN

# Query memory
python -m reliquary query
python -m reliquary query --status DELIVERED
python -m reliquary query --repo my-repo --limit 10

# View statistics
python -m reliquary stats
```

### API Quick Reference

```bash
# Health check
curl http://localhost:8000/

# List runs
curl http://localhost:8000/runs

# Get run details
curl http://localhost:8000/runs/abc123

# Get evidence
curl http://localhost:8000/runs/abc123/evidence

# Get statistics
curl http://localhost:8000/stats

# Provide info (HITL)
curl -X POST http://localhost:8000/runs/abc123/provide_info \
  -H "Content-Type: application/json" \
  -d '{"answer": "Use FastAPI for the API"}'

# Approve run (HITL)
curl -X POST http://localhost:8000/runs/abc123/approve \
  -H "Content-Type: application/json" \
  -d '{"approved": true, "reason": "LGTM"}'
```

---

<div align="center">

**🏛️ Built with proof, delivered with truth.**

[Documentation](IMPLEMENTATION_GUIDE.md) • [Architecture](ARCHITECTURE.md) • [Roadmap](ROADMAP.md)

**Reliquary of Truth** © 2026

</div>
