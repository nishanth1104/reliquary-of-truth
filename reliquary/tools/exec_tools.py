import subprocess
from pathlib import Path
from typing import Tuple
from reliquary.schemas.evidence import CommandRun

def run_command(repo_path: str, command: str, out_dir: str, label: str) -> CommandRun:
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    stdout_path = str(Path(out_dir) / f"{label}.stdout.txt")
    stderr_path = str(Path(out_dir) / f"{label}.stderr.txt")

    # Use PowerShell to run commands consistently on Windows
    proc = subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )

    Path(stdout_path).write_text(proc.stdout or "", encoding="utf-8")
    Path(stderr_path).write_text(proc.stderr or "", encoding="utf-8")

    return CommandRun(
        command=command,
        exit_code=proc.returncode,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
    )
