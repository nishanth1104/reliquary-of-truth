from pydantic import BaseModel, Field
from typing import List, Optional

class CommandRun(BaseModel):
    command: str
    exit_code: int
    stdout_path: str
    stderr_path: str

class Evidence(BaseModel):
    test_runs: List[CommandRun] = Field(default_factory=list)
    lint_runs: List[CommandRun] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)
