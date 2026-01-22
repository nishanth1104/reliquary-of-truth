import subprocess
import json
import re
from typing import List
from reliquary.schemas.security import SecurityScanResult, SecurityFinding


def run_bandit(repo_path: str, files: List[str]) -> SecurityScanResult:
    """
    Runs bandit security scanner on specified files.

    Args:
        repo_path: Repository path
        files: List of files to scan

    Returns:
        SecurityScanResult
    """
    findings = []

    try:
        # Run bandit with JSON output
        result = subprocess.run(
            ["bandit", "-r", repo_path, "-f", "json"],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.stdout:
            data = json.loads(result.stdout)

            for issue in data.get("results", []):
                severity_map = {
                    "HIGH": "high",
                    "MEDIUM": "medium",
                    "LOW": "low"
                }

                findings.append(SecurityFinding(
                    severity=severity_map.get(issue.get("issue_severity", "LOW"), "low"),
                    category=issue.get("test_id", "unknown"),
                    file_path=issue.get("filename", ""),
                    line_number=issue.get("line_number"),
                    description=issue.get("issue_text", "")
                ))

    except FileNotFoundError:
        # Bandit not installed
        findings.append(SecurityFinding(
            severity="low",
            category="tool_missing",
            file_path="",
            line_number=None,
            description="Bandit security scanner not installed. Install with: pip install bandit"
        ))
    except Exception as e:
        findings.append(SecurityFinding(
            severity="low",
            category="scan_error",
            file_path="",
            line_number=None,
            description=f"Error running bandit: {str(e)}"
        ))

    # Check if passed (no critical or high findings)
    critical_or_high = [f for f in findings if f.severity in ["critical", "high"]]
    passed = len(critical_or_high) == 0

    return SecurityScanResult(
        scan_type="bandit",
        findings=findings,
        passed=passed
    )


def detect_secrets(patch_content: str) -> SecurityScanResult:
    """
    Detects potential secrets in patch content using pattern matching.

    Args:
        patch_content: Patch diff content

    Returns:
        SecurityScanResult
    """
    findings = []

    # Secret patterns
    patterns = {
        "api_key": r'(api[_-]?key|apikey)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?',
        "password": r'(password|passwd|pwd)\s*[:=]\s*["\']([^"\']{8,})["\']',
        "token": r'(token|auth[_-]?token)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?',
        "private_key": r'-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----',
        "aws_key": r'(AKIA|A3T|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}',
    }

    lines = patch_content.split('\n')
    for i, line in enumerate(lines):
        # Only check added lines
        if not line.startswith('+'):
            continue

        for secret_type, pattern in patterns.items():
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                findings.append(SecurityFinding(
                    severity="high",
                    category=f"potential_{secret_type}",
                    file_path="patch",
                    line_number=i + 1,
                    description=f"Potential {secret_type.replace('_', ' ')} detected: {match.group(0)[:50]}..."
                ))

    # Check if passed
    passed = len(findings) == 0

    return SecurityScanResult(
        scan_type="detect-secrets",
        findings=findings,
        passed=passed
    )


def aggregate_scan_results(scans: List[SecurityScanResult]) -> bool:
    """
    Aggregates multiple scan results.

    Args:
        scans: List of SecurityScanResult

    Returns:
        True if all scans passed, False otherwise
    """
    return all(scan.passed for scan in scans)
