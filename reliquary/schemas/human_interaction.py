from pydantic import BaseModel
from typing import Literal


class HumanAction(BaseModel):
    action_id: str
    work_item_id: str
    actor: str  # email or username
    action_type: Literal["provide_info", "approve", "reject"]
    timestamp: str
    details: dict
