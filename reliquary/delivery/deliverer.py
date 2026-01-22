import os
import zipfile
from pathlib import Path
from datetime import datetime
import uuid

from reliquary.schemas.state import WorkItemState
from reliquary.schemas.delivery import DeliveryConfig, DeliveryResult


def prepare_proof_bundle(run_dir: str) -> str:
    """
    Creates a ZIP file containing all proof artifacts.

    Args:
        run_dir: Path to the run directory

    Returns:
        Path to the created proof bundle ZIP file
    """
    bundle_path = os.path.join(run_dir, "proof_bundle.zip")

    with zipfile.ZipFile(bundle_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add evidence.json
        evidence_path = os.path.join(run_dir, "evidence.json")
        if os.path.exists(evidence_path):
            zipf.write(evidence_path, "evidence.json")

        # Add decision_log.json
        decision_log_path = os.path.join(run_dir, "decision_log.json")
        if os.path.exists(decision_log_path):
            zipf.write(decision_log_path, "decision_log.json")

        # Add help_requests.json
        help_requests_path = os.path.join(run_dir, "help_requests.json")
        if os.path.exists(help_requests_path):
            zipf.write(help_requests_path, "help_requests.json")

        # Add help_responses.json
        help_responses_path = os.path.join(run_dir, "help_responses.json")
        if os.path.exists(help_responses_path):
            zipf.write(help_responses_path, "help_responses.json")

        # Add all test outputs from artifacts directory
        artifacts_dir = os.path.join(run_dir, "artifacts")
        if os.path.exists(artifacts_dir):
            for filename in os.listdir(artifacts_dir):
                file_path = os.path.join(artifacts_dir, filename)
                if os.path.isfile(file_path):
                    zipf.write(file_path, f"artifacts/{filename}")

    return bundle_path


def deliver_local_patch(state: WorkItemState, run_dir: str, config: DeliveryConfig) -> DeliveryResult:
    """
    Delivers changes as a local patch file with proof bundle.

    Args:
        state: Current work item state
        run_dir: Path to the run directory
        config: Delivery configuration

    Returns:
        DeliveryResult with local patch details
    """
    try:
        # Prepare proof bundle
        proof_bundle_path = prepare_proof_bundle(run_dir)

        # Patch file should already exist in artifacts
        patch_path = os.path.join(run_dir, "artifacts", "change.patch")

        if not os.path.exists(patch_path):
            return DeliveryResult(
                delivery_id=str(uuid.uuid4())[:8],
                mode="local_patch",
                status="failed",
                proof_manifest_path=proof_bundle_path,
                delivered_at=datetime.utcnow().isoformat(),
                error_message="Patch file not found"
            )

        return DeliveryResult(
            delivery_id=str(uuid.uuid4())[:8],
            mode="local_patch",
            status="delivered",
            patch_bundle_path=patch_path,
            proof_manifest_path=proof_bundle_path,
            delivered_at=datetime.utcnow().isoformat()
        )

    except Exception as e:
        return DeliveryResult(
            delivery_id=str(uuid.uuid4())[:8],
            mode="local_patch",
            status="failed",
            proof_manifest_path=run_dir,
            delivered_at=datetime.utcnow().isoformat(),
            error_message=str(e)
        )


def deliver_github_pr(state: WorkItemState, run_dir: str, config: DeliveryConfig) -> DeliveryResult:
    """
    Creates a GitHub PR with proof artifacts.

    Args:
        state: Current work item state
        run_dir: Path to the run directory
        config: Delivery configuration

    Returns:
        DeliveryResult with PR details
    """
    try:
        from reliquary.tools.github_tools import create_github_pr, upload_proof_gist
        from reliquary.delivery.pr_builder import create_pr_description

        # Prepare proof bundle
        proof_bundle_path = prepare_proof_bundle(run_dir)

        # Upload proof bundle to Gist
        with open(proof_bundle_path, 'rb') as f:
            proof_content = f.read()

        # For now, we'll include proof summary in PR description
        # In production, upload to Gist or release asset
        pr_description = create_pr_description(state, proof_bundle_path)

        # Extract repo URL from repo_path
        # This is a simplified version; real implementation would parse git remote
        repo_url = "https://github.com/user/repo"  # Placeholder

        # Create branch name from work_item_id
        branch_name = f"reliquary/{state.work_item_id}"

        pr_data = create_github_pr(
            repo_url=repo_url,
            branch=branch_name,
            title=state.ticket.title if state.ticket else state.task_raw[:50],
            body=pr_description,
            token=config.github_token
        )

        return DeliveryResult(
            delivery_id=str(uuid.uuid4())[:8],
            mode="github_pr",
            status="delivered",
            pr_url=pr_data.get("html_url"),
            pr_number=pr_data.get("number"),
            proof_manifest_path=proof_bundle_path,
            delivered_at=datetime.utcnow().isoformat()
        )

    except Exception as e:
        return DeliveryResult(
            delivery_id=str(uuid.uuid4())[:8],
            mode="github_pr",
            status="failed",
            proof_manifest_path=run_dir,
            delivered_at=datetime.utcnow().isoformat(),
            error_message=str(e)
        )


def deliver_direct_push(state: WorkItemState, run_dir: str, config: DeliveryConfig) -> DeliveryResult:
    """
    Pushes changes directly to a branch.

    Args:
        state: Current work item state
        run_dir: Path to the run directory
        config: Delivery configuration

    Returns:
        DeliveryResult with push details
    """
    try:
        from reliquary.tools.github_tools import push_to_branch

        # Prepare proof bundle
        proof_bundle_path = prepare_proof_bundle(run_dir)

        # Create commit message
        commit_message = f"[Reliquary] {state.ticket.title if state.ticket else state.task_raw[:50]}\n\nWork Item: {state.work_item_id}"

        # Push to branch
        push_to_branch(
            repo_path=state.repo_path,
            branch_name=config.target_branch,
            commit_message=commit_message
        )

        return DeliveryResult(
            delivery_id=str(uuid.uuid4())[:8],
            mode="direct_push",
            status="delivered",
            proof_manifest_path=proof_bundle_path,
            delivered_at=datetime.utcnow().isoformat()
        )

    except Exception as e:
        return DeliveryResult(
            delivery_id=str(uuid.uuid4())[:8],
            mode="direct_push",
            status="failed",
            proof_manifest_path=run_dir,
            delivered_at=datetime.utcnow().isoformat(),
            error_message=str(e)
        )
