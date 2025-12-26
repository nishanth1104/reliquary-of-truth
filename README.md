# Reliquary of Truth

**Reliquary of Truth** is a proof-gated, AI-driven software engineering organization.

Instead of treating software development as a single prompt or agent, Reliquary models it as a small engineering org with structure, ownership, verification, and auditability. A task is only considered complete when it can be backed by **evidence** (tests, logs, diffs). If something is ambiguous or unverifiable, the system explicitly stops.

---

## Why Reliquary exists

Modern AI coding tools are good at generating code quickly, but they struggle with ownership, verification, and knowing when requirements are incomplete. Reliquary enforces real engineering discipline through structured intake, single-owner execution, verification, and proof-backed delivery.

---

## Core principle

**No proof → no delivery.**

---

## Workflow

**Stage 1 — Intake & Triage**
- Converts natural-language tasks into structured tickets
- Detects ambiguity and asks clarifying questions

**Stage 2 — Owning Engineer**
- One agent owns planning and implementation
- Generates minimal, scoped patches

**Stage 3 — Review & Verification**
- Applies patches
- Runs tests
- Collects logs, diffs, and evidence

---

## Terminal states

- **DELIVERED** — patch applied, tests passed, proof saved  
- **NEEDS_INFO** — missing requirements  
- **BLOCKED** — task cannot be completed safely  

---

## Proof artifacts

Each run creates a folder under `runs/` containing:
- unified diffs
- git snapshots
- test logs
- evidence JSON
- final state JSON

---

## Repository structure

```
reliquary-of-truth/
├─ reliquary/
│  ├─ agents/
│  ├─ graph/
│  ├─ schemas/
│  ├─ storage/
│  └─ cli.py
├─ runs/
├─ README.md
└─ LICENSE
```

---

## Setup (Windows)

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env`:
```
OPENAI_API_KEY=YOUR_KEY
```

---

## Running

```powershell
python -m reliquary --repo ..\reliquary-demo-repo --task "Add a /health endpoint"
```

---

## Status

Week 1 complete. Proof-gated delivery implemented.

---

## Non-goals

- Replacing human engineers
- One-shot code generation
- Maximizing speed over correctness
- Solving ambiguous requirements silently

---

## License

MIT

