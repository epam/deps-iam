import json
import logging
import re
from http import HTTPStatus
from itertools import chain
from typing import Callable, Optional

from cachetools import TTLCache
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import StreamingResponse

from deps_iam.constants import API_KEY, API_PREFIX
from deps_iam.domain.exceptions import AuthError
from deps_iam.domain.services.access_token_auth_service import AUTH_HEADER, TOKEN_PREFIX


class CacheMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: dict[str, int]):
        super().__init__(app)
        self._response_cache: TTLCache[str, Response] = TTLCache(
            maxsize=settings["maxsize"],
            ttl=settings["ttl"],
        )
        self._credentials_cache: TTLCache[str, list[str]] = TTLCache(
            maxsize=settings["maxsize"],
            ttl=settings["ttl"],
        )
        self._logger = logging.getLogger(self.__class__.__name__)

    @property
    def request_mapper(self):
        return {
            ("GET", f"^{API_PREFIX}/authorize$"): self._get_response,
            ("DELETE", f"^{API_PREFIX}/users/me/api-key$"): self._clean_current_user_cache,
            ("POST", f"^{API_PREFIX}/users/me/api-key/generate$"): self._clean_current_user_cache,
            ("DELETE", rf"^{API_PREFIX}/organisations/[\w\-]+$"): self._clean_all_cache,
            ("POST", rf"^{API_PREFIX}/organisations/[\w\-]+/activate$"): self._clean_current_user_cache,
            ("DELETE", rf"^{API_PREFIX}/organisations/[\w\-]+/users$"): self._clean_deleted_user_cache,
            ("POST", rf"^{API_PREFIX}/organisations/[\w\-]+/join$"): self._clean_current_user_cache,
            ("DELETE", rf"^{API_PREFIX}/users/[\w\-]+$"): self._clean_all_cache,
        }

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if response_handler := self._get_response_handler(request):
            self._logger.debug(
                "Custom response_handler for method %s  to %s is selected." % (request.method, request.url.path)
            )
            return await response_handler(request, call_next)
        return await call_next(request)

    async def _get_response(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if cached_response := self._get_cached_response(request):
            self._logger.debug("Return cached response.")
            return cached_response

        return await self._add_new_response_to_cache(request, call_next)

    def _get_cached_response(self, request: Request) -> Optional[Response]:
        cache_key = self._get_cache_key(request)
        return self._response_cache.get(cache_key)

    async def _add_new_response_to_cache(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response, succesfull = await self._make_request(request, call_next)
        if succesfull:
            response = await self._make_cached_response(response)
            self._add_response_to_cache(response, self._get_cache_key(request))
            self._logger.debug("Warming up authorize caching... ")
            return response
        self._logger.warning("Status code %s doesn't allow add response to cache" % response.status_code)
        return response

    async def _make_request(self, request: Request, call_next: RequestResponseEndpoint) -> tuple[Response, bool]:
        response = await call_next(request)
        return (response, self._is_response_successful(response))

    def _get_response_handler(self, request: Request) -> Optional[Callable]:
        path = request.url.path
        for (method, url), response_handler in self.request_mapper.items():
            if request.method == method and re.match(url, path):
                self._logger.info("Custom response_handler for method %s  to %s is selected." % (method, path))
                return response_handler

    def _add_response_to_cache(self, response: Response, cache_key: str) -> None:
        self._response_cache[cache_key] = response
        credentials_cache_key = self._get_credentials_from_json(response.headers["deps-token"])
        self._credentials_cache.setdefault(credentials_cache_key, []).append(cache_key)
        self._logger.debug("Response added to cache. Keys: %s /n %s" % (cache_key, credentials_cache_key))

    async def _make_cached_response(self, response: StreamingResponse) -> Response:
        body_content = b""
        async for chunk in response.body_iterator:  # noqa: WPS519
            body_content += chunk  # type: ignore

        return Response(
            content=body_content,
            status_code=response.status_code,
            headers=response.headers,
            media_type=response.media_type,
            background=response.background,
        )

    def _clean_response_cache_by_keys(self, cache_keys: list[str]) -> None:
        for key in cache_keys:
            self._response_cache.pop(key, None)
            self._logger.debug("%s key removed from cache" % key)

    def _get_cache_key(self, request: Request) -> str:
        try:
            cache_key = request.headers.get(API_KEY) or request.headers[AUTH_HEADER]
            return cache_key.replace(TOKEN_PREFIX, "").strip()
        except KeyError:
            self._logger.error("Headers don't content token nor api-key. Headers %s" % request.headers)
            raise AuthError("No auth header.")

    async def _clean_all_cache(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response, successful = await self._make_request(request, call_next)
        if successful:
            self._response_cache.clear()
            self._credentials_cache.clear()
            self._logger.debug("Cache is cleared.")
        return response

    async def _clean_current_user_cache(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response, successful = await self._make_request(request, call_next)
        if successful:
            credentials_cache_key = self._get_credentials_from_json(request.headers["deps-token"])
            response_cache_keys = self._credentials_cache.pop(credentials_cache_key, [])
            self._clean_response_cache_by_keys(response_cache_keys)
            self._logger.debug("%s and %s keys removed from cache" % (credentials_cache_key, response_cache_keys))
        return response

    async def _clean_deleted_user_cache(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response, successful = await self._make_request(request, call_next)
        if successful:
            response = await self._make_cached_response(response)
            response_cache_keys = list(
                chain.from_iterable(
                    self._credentials_cache.pop(deleted_user_pk, [])
                    for deleted_user_pk in json.loads(response.body)["deletedUsers"]
                )
            )
            self._clean_response_cache_by_keys(response_cache_keys)
            self._logger.debug("Keys for deleting from cache: %s" % response_cache_keys)
        return response

    @staticmethod
    def _get_credentials_from_json(deps_token: str) -> str:
        return json.loads(deps_token)["subject"]

    @staticmethod
    def _is_response_successful(response: Response) -> bool:
        return HTTPStatus.OK <= response.status_code < HTTPStatus.MULTIPLE_CHOICES
