from dataclasses import dataclass
from typing import List

from deps_message_flow.commands.common import Command


class GetTenants(Command):
    pass  # noqa: WPS604


@dataclass
class GetTenantsReply(Command):
    tenant_ids: List[str]
