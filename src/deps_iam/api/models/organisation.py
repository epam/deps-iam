from pydantic import BaseModel, ConfigDict, Field

from deps_iam.domain.dtos import OrganisationUpdate
from deps_iam.domain.entities.organisation import Organisation, OrganisationPk


class OrganisationModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    pk: OrganisationPk | None = None
    name: str
    customization_url: str | None = Field(None, alias="customizationUrl")

    def to_domain(self) -> Organisation:
        return Organisation(**self.model_dump())


class OrganisationUpdateModel(BaseModel):
    name: str | None = None
    customization_url: str | None = Field(default=None, alias="customizationUrl")

    def to_domain(self) -> OrganisationUpdate:
        return OrganisationUpdate(**self.model_dump(exclude_unset=True))
