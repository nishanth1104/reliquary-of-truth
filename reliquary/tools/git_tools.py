import subprocess
from pathlib import Path

def _run(repo_path: str, args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args,
        cwd=repo_path,
        capture_output=True,
        text=True,
        shell=False,
    )

def ensure_clean_or_commit(repo_path: str) -> None:
    r = _run(repo_path, ["status", "--porcelain"])
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    # Clean is fine; dirty is also fine (we just need diffs to show)
    return

def get_diff(repo_path: str) -> str:
    r = _run(repo_path, ["diff"])
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    return r.stdout

def apply_patch(repo_path: str, patch_path: str) -> None:
    p = Path(patch_path)
    if not p.exists():
        raise FileNotFoundError(patch_path)
    r = _run(repo_path, ["apply", "--whitespace=fix", str(p)])
    if r.returncode != 0:
        raise RuntimeError(f"git apply failed:\n{r.stderr}")

def create_patch_file(out_path: str, unified_diff: str) -> None:
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(unified_diff, encoding="utf-8")
