from dataclasses import dataclass
from typing import Optional, Union

from ..resource_source import ResourceSource

ResourceData = Optional[list[Union[str, int]]]


@dataclass(frozen=True)
class RequestInfo:
    method: str
    path_regex: str


@dataclass
class RawRequestContext:
    action: str
    resources: list[str]
    resource_source: Optional[ResourceSource]
    resource_data: ResourceData

    @property
    def has_resource(self) -> bool:
        return self.resource_source is not None
