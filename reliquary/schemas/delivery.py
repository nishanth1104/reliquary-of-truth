from pydantic import BaseModel
from typing import Literal, Optional


DeliveryMode = Literal["local_patch", "github_pr", "direct_push"]


class DeliveryConfig(BaseModel):
    mode: DeliveryMode = "local_patch"
    target_branch: Optional[str] = "main"
    require_ci_pass: bool = False
    github_token: Optional[str] = None


class DeliveryResult(BaseModel):
    delivery_id: str
    mode: DeliveryMode
    status: Literal["pending", "delivered", "failed"]
    pr_url: Optional[str] = None
    pr_number: Optional[int] = None
    patch_bundle_path: Optional[str] = None
    proof_manifest_path: str
    delivered_at: str
    ci_run_url: Optional[str] = None
    error_message: Optional[str] = None
