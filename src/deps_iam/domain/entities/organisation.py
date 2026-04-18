from dataclasses import dataclass
from typing import NewType, Optional

OrganisationPk = NewType("OrganisationPk", str)


@dataclass
class Organisation:
    name: str
    pk: Optional[OrganisationPk] = None
    customization_url: Optional[str] = None
    is_personal: bool = False
