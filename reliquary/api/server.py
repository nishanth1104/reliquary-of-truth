from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os

from reliquary.memory.store import query_runs, get_stats
from reliquary.human.interaction_handler import process_info_provision, process_approval

app = FastAPI(title="Reliquary of Truth API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Reliquary of Truth API", "version": "1.0.0"}


@app.get("/runs")
def list_runs(
    repo: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """List runs with optional filtering."""
    runs = query_runs(repo_name=repo, status=status, limit=limit + offset)
    # Apply offset
    runs = runs[offset:]

    return {
        "runs": [r.model_dump() for r in runs],
        "count": len(runs)
    }


@app.get("/runs/{work_item_id}")
def get_run(work_item_id: str):
    """Get details for a specific run."""
    runs = query_runs(limit=1000)
    run = next((r for r in runs if r.work_item_id == work_item_id), None)

    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    return run.model_dump()


@app.get("/runs/{work_item_id}/evidence")
def get_evidence(work_item_id: str):
    """Get evidence for a specific run."""
    runs = query_runs(limit=1000)
    run = next((r for r in runs if r.work_item_id == work_item_id), None)

    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    evidence_file = os.path.join(run.run_dir, "evidence.json")
    if not os.path.exists(evidence_file):
        raise HTTPException(status_code=404, detail="Evidence not found")

    import json
    with open(evidence_file, 'r') as f:
        return json.load(f)


@app.get("/runs/{work_item_id}/decision_log")
def get_decision_log(work_item_id: str):
    """Get decision log for a specific run."""
    runs = query_runs(limit=1000)
    run = next((r for r in runs if r.work_item_id == work_item_id), None)

    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    log_file = os.path.join(run.run_dir, "decision_log.json")
    if not os.path.exists(log_file):
        raise HTTPException(status_code=404, detail="Decision log not found")

    import json
    with open(log_file, 'r') as f:
        return json.load(f)


@app.post("/runs/{work_item_id}/provide_info")
def provide_info(work_item_id: str, answer: str):
    """Provide information for a run awaiting human input."""
    runs = query_runs(limit=1000)
    run = next((r for r in runs if r.work_item_id == work_item_id), None)

    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    state = process_info_provision(work_item_id, answer, run.run_dir)
    return {"status": "success", "new_status": state.status}


@app.post("/runs/{work_item_id}/approve")
def approve_run(work_item_id: str, approved: bool, reason: str = ""):
    """Approve or reject a run."""
    runs = query_runs(limit=1000)
    run = next((r for r in runs if r.work_item_id == work_item_id), None)

    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    state = process_approval(work_item_id, approved, reason, run.run_dir)
    return {"status": "success", "new_status": state.status}


@app.get("/stats")
def api_stats():
    """Get aggregate statistics."""
    return get_stats()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
