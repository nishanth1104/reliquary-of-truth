# Reliquary of Truth: Phases 3-6 Implementation Guide

## Overview

This document describes the implementation of Phases 3-6 of the Reliquary of Truth project, adding delivery, memory, policy, and dashboard capabilities.

## Installation

```bash
cd reliquary-engine
pip install -r requirements.txt
```

## Phase 3: Delivery & Auditability

### Features Implemented

- **Multiple delivery modes**: Local patch, GitHub PR, Direct push
- **Proof bundling**: All evidence artifacts packaged with deliveries
- **Audit trail**: Immutable append-only event log with hash chaining

### Usage

#### Local Patch Delivery (default)

```bash
python -m reliquary run --repo ../reliquary-demo-repo --task "Add /status endpoint"
```

The patch and proof bundle will be saved in `runs/{work_item_id}/`.

#### GitHub PR Creation

```bash
# Set GitHub token
export GITHUB_TOKEN=ghp_your_token_here

python -m reliquary run \
  --repo ../reliquary-demo-repo \
  --task "Add /status endpoint" \
  --delivery-mode github_pr \
  --target-branch main
```

#### Verify Audit Integrity

```python
from reliquary.storage.audit_store import verify_audit_integrity

# Verify audit log hasn't been tampered with
is_valid = verify_audit_integrity("runs/abc123_20260121")
print(f"Audit log valid: {is_valid}")
```

### Storage Structure

```
runs/{work_item_id}_{timestamp}/
  state_before_verify.json
  evidence.json
  decision_log.json
  delivery_result.json          # NEW in Phase 3
  proof_bundle.zip              # NEW in Phase 3
  audit_events.jsonl            # NEW in Phase 3 (append-only)
  artifacts/
    change.patch
    git.diff.txt
    pytest_*.stdout.txt
```

## Phase 4: Organizational Memory & Learning

### Features Implemented

- **SQLite memory store**: Indexes all runs for fast querying
- **Pattern matching**: Finds similar successful/failed tasks
- **Advisory system**: Provides recommendations based on history

### Usage

#### Query Past Runs

```bash
# Query all runs
python -m reliquary query

# Filter by repository
python -m reliquary query --repo ../reliquary-demo-repo

# Filter by status
python -m reliquary query --status BLOCKED

# Limit results
python -m reliquary query --limit 20
```

#### View Statistics

```bash
python -m reliquary stats
```

Output:
```
Reliquary Memory Statistics

Total Runs: 15
Successful Runs: 12
Success Rate: 80.0%
Average Attempts: 2.3

Failure Modes:
  tests_failed: 2
  max_attempts_exceeded: 1
```

#### Memory Advice in Workflow

Memory advice is automatically consulted during the planning phase:

```python
# In workflow, memory advice is added to state
memory_advice = get_memory_advice(state.ticket, state.repo_path)

# Decision log will show:
# - Similar successful tasks
# - Similar failed tasks
# - Regression risks
# - Recommendations
```

## Phase 5: Safety, Policy & Governance

### Features Implemented

- **Policy engine**: Declarative rules with gate/warning/audit types
- **Risk classification**: Detects auth changes, migrations, critical paths
- **Security scanning**: Bandit (SAST) + pattern-based secret detection

### Usage

#### Default Policies

Policies are defined in `policies/v1.0.json`:

- **no_auth_without_tests**: Blocks auth changes without tests
- **large_changes_warning**: Warns on large diffs (>500 lines)
- **migration_safety**: Warns on migration changes
- **critical_path_audit**: Logs critical path modifications

#### Custom Policies

Create a new policy file:

```json
{
  "version": "2.0",
  "rules": [
    {
      "rule_id": "require_db_tests",
      "name": "Database changes require integration tests",
      "rule_type": "gate",
      "condition": "risk_factors['modifies_migrations'] and len(evidence.test_runs) == 0",
      "action": "block"
    }
  ]
}
```

Set the policy version:

```bash
export RELIQUARY_POLICY_VERSION=v2.0
```

#### Security Scanning

Security scans run automatically during implementation:

1. **Secret detection**: Patterns for API keys, passwords, tokens, private keys, AWS keys
2. **Bandit SAST**: Static analysis for Python security issues (if installed)

If secrets are detected, the workflow blocks:

```
Status: BLOCKED
Reason: Security scans failed - potential secrets detected
Needs: Review and remove secrets from patch
```

#### Workflow Integration

```
intake → plan → policy_check → implement → security_scan → verify → deliver
```

- **policy_check**: Evaluates policies before implementation
- **security_scan**: Scans patch for secrets and vulnerabilities

## Phase 6: Human Interface & Operations

### Features Implemented

- **FastAPI server**: REST API for run queries and approvals
- **React dashboard**: Web UI for viewing runs and evidence
- **Human-in-the-loop**: Approve/reject high-risk changes
- **Multi-repo views**: Filter by repository and team

### Usage

#### Start API Server

```bash
cd reliquary-engine
python -m uvicorn reliquary.api.server:app --reload
```

API will be available at `http://localhost:8000`

#### API Endpoints

```bash
# List runs
curl http://localhost:8000/runs

# Get run details
curl http://localhost:8000/runs/{work_item_id}

# Get evidence
curl http://localhost:8000/runs/{work_item_id}/evidence

# Get decision log
curl http://localhost:8000/runs/{work_item_id}/decision_log

# Provide info for NEEDS_INFO run
curl -X POST http://localhost:8000/runs/{work_item_id}/provide_info \
  -H "Content-Type: application/json" \
  -d '{"answer": "Use FastAPI for the REST API"}'

# Approve/reject run
curl -X POST http://localhost:8000/runs/{work_item_id}/approve \
  -H "Content-Type: application/json" \
  -d '{"approved": true, "reason": "Looks good"}'

# Get statistics
curl http://localhost:8000/stats
```

#### Start Dashboard

```bash
cd reliquary-engine/reliquary/dashboard/web

# Install dependencies
npm install

# Start dev server
npm run dev
```

Dashboard will be available at `http://localhost:3000`

#### Dashboard Features

- **Run list**: Color-coded by status (green=DELIVERED, red=BLOCKED, yellow=NEEDS_INFO)
- **Statistics**: Total runs, success rate, average attempts, failure modes
- **Run details**: Evidence, decision log, delivery info
- **Actor attribution**: Shows whether actions were taken by AI (owner/helper) or human
- **Approval panel**: Approve/reject high-risk changes

## Environment Variables

Create a `.env` file in `reliquary-engine/`:

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional
GITHUB_TOKEN=ghp_...                    # For PR creation
RELIQUARY_DB_PATH=memory.db             # Memory database path
RELIQUARY_POLICY_VERSION=v1.0           # Policy version to use
```

## Complete Workflow Example

```bash
# 1. Run a task with GitHub PR delivery
python -m reliquary run \
  --repo ../reliquary-demo-repo \
  --task "Add user authentication endpoint with JWT" \
  --delivery-mode github_pr

# Workflow:
# - Intake: Parse task into ticket
# - Plan: Consult memory, get advice
# - Policy Check: Evaluate auth-related policies
# - Implement: Generate patch
# - Security Scan: Check for secrets/vulnerabilities
# - Verify: Run tests, create proof bundle
# - Deliver: Create GitHub PR with proof

# 2. Query memory to see similar tasks
python -m reliquary query --status DELIVERED

# 3. View statistics
python -m reliquary stats

# 4. Start API and dashboard (in separate terminals)
python -m uvicorn reliquary.api.server:app --reload
cd reliquary/dashboard/web && npm run dev

# 5. Open dashboard in browser
# http://localhost:3000
```

## Testing the Implementation

### Test Phase 3 (Delivery)

```bash
# Test local patch delivery
python -m reliquary run --repo ../reliquary-demo-repo --task "Add /health endpoint"

# Verify proof bundle exists
ls runs/*/proof_bundle.zip

# Verify audit log integrity
python -c "from reliquary.storage.audit_store import verify_audit_integrity; print(verify_audit_integrity('runs/abc123_20260121'))"
```

### Test Phase 4 (Memory)

```bash
# Run several tasks
python -m reliquary run --repo ../reliquary-demo-repo --task "Add /users endpoint"
python -m reliquary run --repo ../reliquary-demo-repo --task "Add /posts endpoint"

# Query memory
python -m reliquary query

# View stats
python -m reliquary stats
```

### Test Phase 5 (Policy & Security)

```bash
# Test secret detection
# Create a patch with a fake API key in the code
# Run workflow and verify it blocks

# Test policy evaluation
# Create a task that modifies auth without tests
# Verify policy engine blocks it
```

### Test Phase 6 (Dashboard)

```bash
# Start API
python -m uvicorn reliquary.api.server:app --reload

# Test API endpoints
curl http://localhost:8000/runs
curl http://localhost:8000/stats

# Start dashboard
cd reliquary/dashboard/web
npm install
npm run dev

# Open http://localhost:3000 in browser
```

## Architecture Changes

### New Modules

```
reliquary/
  delivery/           # Phase 3
    deliverer.py
    pr_builder.py
  memory/             # Phase 4
    store.py
    indexer.py
    pattern_matcher.py
    advisor.py
  policy/             # Phase 5
    engine.py
    risk_classifier.py
  security/           # Phase 5
    scanners.py
  api/                # Phase 6
    server.py
  human/              # Phase 6
    interaction_handler.py
  dashboard/web/      # Phase 6
    src/
      api/client.ts
      App.tsx
```

### Schema Extensions

```python
# state.py
class WorkItemState(BaseModel):
    # ... existing fields ...

    # Phase 3
    delivery_config: Optional[DeliveryConfig] = None
    delivery_result: Optional[DeliveryResult] = None

    # Phase 4
    memory_advice: Optional[MemoryAdvice] = None

    # Phase 5
    policy_evaluation: Optional[PolicyEvaluation] = None
    security_scans: List[SecurityScanResult] = []
```

### Workflow Updates

```
Phase 1-2: intake → plan → implement → help → verify → END
Phase 3-6: intake → plan → policy_check → implement → help → security_scan → verify → deliver → END
```

## Success Criteria

### Phase 3

- ✅ Can create PR on GitHub with proof in description
- ✅ Proof bundle contains all artifacts (evidence, logs, diffs)
- ✅ Audit trail is immutable and verifiable

### Phase 4

- ✅ Past runs indexed in SQLite
- ✅ Memory advice appears in decision log during planning
- ✅ Similar task detection works
- ✅ Query CLI can search by repo, status, failure mode

### Phase 5

- ✅ Policy engine blocks unsafe changes
- ✅ Secret detection finds potential secrets and blocks delivery
- ✅ Policy violations logged with justification

### Phase 6

- ✅ Dashboard displays runs with color-coded statuses
- ✅ Evidence viewer shows test outputs and diffs
- ✅ Decision log shows AI vs Human actions
- ✅ API supports human approval/rejection
- ✅ Multi-repo statistics available

## Next Steps

1. **Deploy**: Set up production deployment with Docker
2. **Notifications**: Add Slack/email alerts for human input needed
3. **Advanced Memory**: Use embeddings for better similarity matching
4. **Webhook Integration**: Trigger runs on PR comments, issue creation
5. **Audit Reports**: Generate PDF compliance reports

## Troubleshooting

### Bandit not found

```bash
pip install bandit
```

### GitHub PR creation fails

Ensure `GITHUB_TOKEN` is set and has `repo` scope.

### Memory database locked

Close any open connections to `memory.db`.

### Frontend build errors

```bash
cd reliquary/dashboard/web
rm -rf node_modules package-lock.json
npm install
```

## Contributing

See `ARCHITECTURE.md` and `ROADMAP.md` for project structure and future plans.
