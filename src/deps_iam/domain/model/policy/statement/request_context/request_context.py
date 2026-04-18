import re
from collections import defaultdict
from dataclasses import asdict
from typing import Any, Callable, Iterable, Union

from ....shared.guards import Guard, ImmutableCheck
from ..action import Action
from ..principal import Principal
from ..request_statement import RequestStatement
from ..resource import Resource
from .mappers.request_mapper import RawRequestContext, RequestInfo
from .parsed_request import ParsedRequest
from .resource_source import ResourceSource

__all__ = ["RequestContext"]


class RequestContext:
    action = Guard[Action](Action, ImmutableCheck())
    resources = Guard[list[Resource]](list, ImmutableCheck())
    principal = Guard[Principal](Principal, ImmutableCheck())
    resource_data = Guard[dict[str, list[Union[str, int]]]](dict, ImmutableCheck())  # noqa: WPS221

    def __init__(
        self,
        action: Action,
        resources: list[Resource],
        principal: Principal,
        resource_data: dict[str, Any],
    ) -> None:
        self.action = action
        self.resources = resources
        self.principal = principal
        self.resource_data = resource_data

    def __str__(self) -> str:
        return (
            f"<RequestContext> action: {self.action},"
            f"resources count: {len(self.resources)}, "
            f"principal: {self.principal}, "
            f"resource data: {self.resource_data}"
        )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)  # noqa: WPS222
            and self.action == other.action
            and self.resources == other.resources
            and self.principal == other.principal
            and self.resource_data == other.resource_data
        )

    @property
    def request_statements(self) -> Iterable[RequestStatement]:
        return self._make_concrete_statements() if self.resource_data else self._make_common_statements()

    def _make_common_statements(self) -> Iterable[RequestStatement]:
        return [
            RequestStatement(
                self.action,
                resource,
                self.principal,
            )
            for resource in self.resources
        ]

    def _make_concrete_statements(self) -> Iterable[RequestStatement]:
        return [
            RequestStatement(
                self.action,
                Resource(resource().format(resource_id=resource_data)),
                self.principal,
            )
            for resource in self.resources
            for resource_data in self.resource_data[resource()]
        ]

    @classmethod
    def get_resources_parser(cls, resource_source: str) -> Callable:
        resource_parsers = {
            ResourceSource.PATH: cls._get_resource_data_from_path,
            ResourceSource.BODY: cls._get_resource_data_from_body,
            ResourceSource.QUERY: cls._get_resource_data_from_query,
        }
        return resource_parsers[resource_source]  # type: ignore

    @classmethod
    def from_parsed_request(
        cls, match: tuple[RequestInfo, RawRequestContext], user_subject: str, parsed_request: ParsedRequest
    ) -> "RequestContext":
        request_info, raw_request_context = match
        resource_source = raw_request_context.resource_source

        resource_data = (
            cls.get_resources_parser(resource_source)(request_info, raw_request_context, parsed_request)
            if resource_source
            else defaultdict(list)
        )

        return cls(
            action=Action(raw_request_context.action),
            resources=[Resource(resource) for resource in raw_request_context.resources],
            principal=Principal(user_subject),
            resource_data=resource_data,
        )

    @classmethod
    def _get_resource_data_from_path(
        cls, request_info: RequestInfo, raw_request_context: RawRequestContext, parsed_request: ParsedRequest
    ) -> dict[str, list]:
        resource_data = defaultdict(list)
        match = re.search(request_info.path_regex, parsed_request.base_path)
        for index, _resource in enumerate(raw_request_context.resources):
            resource_data[raw_request_context.resources[index]].append(
                match.group(raw_request_context.resource_data[index])
            )
        return resource_data

    @classmethod
    def _get_resource_data_from_body(
        cls, request_info: RequestInfo, raw_request_context: RawRequestContext, parsed_request
    ) -> dict[str, list]:
        resource_data = defaultdict(list)
        for index, _resource in enumerate(raw_request_context.resources):
            resource_data[raw_request_context.resources[index]].extend(
                asdict(parsed_request.body_resource)[raw_request_context.resource_data[index]]  # type: ignore
            )  # noqa: WPS221
        return resource_data

    @classmethod
    def _get_resource_data_from_query(
        cls, request_info: RequestInfo, raw_request_context: RawRequestContext, parsed_request
    ) -> dict[str, list]:
        resource_data = defaultdict(list)
        query_splitted = parsed_request.query.split("&")

        for index, _resource in enumerate(raw_request_context.resources):  # noqa: WPS426
            query_regex = f"^{raw_request_context.resource_data[index]}=(.*)$"
            match = list(filter(lambda q: re.search(query_regex, q), query_splitted))

            if match:
                query = re.search(query_regex, match[0]).group(1)
                resource_data[raw_request_context.resources[index]].append(query)

        return resource_data
