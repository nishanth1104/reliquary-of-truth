from pathlib import Path
from typing import List

def list_tree(root: str, max_files: int = 200) -> List[str]:
    root_path = Path(root)
    files = []
    for p in root_path.rglob("*"):
        if p.is_file():
            rel = p.relative_to(root_path).as_posix()
            # Skip venv and git internals
            if rel.startswith(".git/") or rel.startswith(".venv/") or "/.venv/" in rel:
                continue
            files.append(rel)
            if len(files) >= max_files:
                break
    return sorted(files)

def read_text(root: str, rel_path: str, max_chars: int = 12000) -> str:
    p = Path(root) / rel_path
    txt = p.read_text(encoding="utf-8", errors="ignore")
    return txt[:max_chars]

def write_text(root: str, rel_path: str, content: str) -> None:
    p = Path(root) / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
