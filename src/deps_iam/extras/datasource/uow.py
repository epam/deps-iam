import threading
from typing import List

from sqlalchemy.engine import Connection, NestedTransaction

from deps_iam.extras.interfaces import IUoW

from .connection_provider import ConnectionProvider


class DatabaseUoW(IUoW):
    def __init__(self, connection_provider: ConnectionProvider):
        self._connection_provider = connection_provider

        self._registry = threading.local()

    def commit(self) -> None:
        self._transaction.commit()

    def rollback(self) -> None:
        self._transaction.rollback()

    @property
    def _connection(self) -> Connection:
        return self._connection_provider()

    @property
    def _transaction_stack(self) -> List[NestedTransaction]:
        if not getattr(self._registry, "transaction_stack", False):
            self._registry.transaction_stack = []

        return self._registry.transaction_stack

    @property
    def _transaction(self) -> NestedTransaction:
        if not self._transaction_stack:
            raise RuntimeError("No opened transactions yet")

        return self._transaction_stack[-1]

    def open_transaction(self) -> None:
        t = self._connection.begin_nested()
        self._transaction_stack.append(t)

    def close_transaction(self) -> None:
        self._transaction.rollback()
        self._transaction_stack.pop()
