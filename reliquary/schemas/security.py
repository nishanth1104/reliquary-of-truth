from pydantic import BaseModel
from typing import Literal, List, Optional


class SecurityFinding(BaseModel):
    severity: Literal["critical", "high", "medium", "low"]
    category: str
    file_path: str
    line_number: Optional[int]
    description: str


class SecurityScanResult(BaseModel):
    scan_type: str  # "bandit", "detect-secrets"
    findings: List[SecurityFinding]
    passed: bool  # No critical/high findings
