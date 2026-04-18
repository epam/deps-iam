import contextvars
from typing import Any

user: contextvars.ContextVar[dict[str, Any]] = contextvars.ContextVar("user")
