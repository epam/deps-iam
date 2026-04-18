from dataclasses import dataclass

from deps_message_flow.events.common import DomainEvent


@dataclass
class OrganisationCreated(DomainEvent):
    id: str
    organisation_name: str
    personal: bool


@dataclass
class TestEvent(DomainEvent):
    data: str


@dataclass
class TenantCreated(DomainEvent):
    tenant_id: str


@dataclass
class SendInvitationEmailEvent(DomainEvent):
    user_email: str
    inviter_name: str
    organisation: str
