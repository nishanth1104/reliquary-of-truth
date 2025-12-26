import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict

def new_run_dir(base_dir: str, work_item_id: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = Path(base_dir) / f"{work_item_id}_{ts}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "artifacts").mkdir(exist_ok=True)
    return str(run_dir)

def write_json(path: str, data: Any) -> None:
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")

def write_text(path: str, text: str) -> None:
    Path(path).write_text(text, encoding="utf-8")
