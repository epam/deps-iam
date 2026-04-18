from dataclasses import dataclass
from datetime import datetime


@dataclass
class ApprovalRequest:
    user_pk: str
    organisation_pk: str
    created_at: datetime
