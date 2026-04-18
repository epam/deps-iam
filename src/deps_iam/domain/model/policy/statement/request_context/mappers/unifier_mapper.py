from ...action import UnifierAction
from ..resource_source import ResourceSource
from .request_mapper import RawRequestContext, RequestInfo

unifier_mapper: dict[RequestInfo, RawRequestContext] = {
    RequestInfo("GET", "^unified_data/([0-9]*)$"): RawRequestContext(
        UnifierAction.GET_UNIFIED_DATA, ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("PUT", "^unified_data/upsert-data$"): RawRequestContext(
        UnifierAction.UPDATE_UNIFIED_DATA, ["document"], ResourceSource.BODY, ["document"]
    ),
    RequestInfo("PATCH", "^unified_data/(.*)/transformations$"): RawRequestContext(
        UnifierAction.RUN_TRANSFORMATIONS, ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("GET", "^unified_data/(.*)/tables/(.*)/cells$"): RawRequestContext(
        UnifierAction.LIST_CELLS, ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("POST", "^cells$"): RawRequestContext(UnifierAction.ADD_CELLS, ["document"], None, []),
}
