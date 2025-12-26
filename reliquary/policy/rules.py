from typing import List

def evidence_gate_can_finalize(test_exit_code: int) -> bool:
    return test_exit_code == 0

def must_block_when_no_tests_available() -> bool:
    # Week 1 policy: we require tests to pass if tests exist.
    # If tests can't be run (missing deps), we block.
    return True
