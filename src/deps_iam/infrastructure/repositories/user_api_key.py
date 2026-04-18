from sqlalchemy import delete, insert, update
from sqlalchemy.engine import Connection, RowProxy
from sqlalchemy.exc import StatementError
from sqlalchemy.sql import select

from deps_iam.domain.exceptions import UserApiKeyNotFoundError, UserNotFoundError
from deps_iam.domain.interfaces.repositories import IUserApiKeyRepository
from deps_iam.extras.datasource import Database
from deps_iam.infrastructure.repositories.constants import DatabaseErrorTypeEnum
from deps_iam.infrastructure.repositories.error_extractor import (
    extract_database_error_type,
)
from deps_iam.infrastructure.tables import user_api_key_table


class UserApiKeyRepository(IUserApiKeyRepository):
    def __init__(self, database: Database):
        self._database = database

    def create(self, user_pk: str, api_key: str) -> str:
        try:
            self.get(user_pk)
            res = self._update(user_pk, api_key)
        except UserApiKeyNotFoundError:
            res = self._insert(user_pk, api_key)

        return res[0]

    def get(self, user_pk: str) -> str:
        select_query = select([user_api_key_table.c.api_key]).where(user_api_key_table.c.user_pk == user_pk)

        res = self._connection.execute(select_query).fetchone()

        if not res:
            raise UserApiKeyNotFoundError(f"User with id {user_pk} doesn't have api key.")

        return res["api_key"]

    def get_user_by_api_key(self, api_key: str) -> str:
        select_query = select([user_api_key_table.c.user_pk]).where(user_api_key_table.c.api_key == api_key)
        res = self._connection.execute(select_query).fetchone()

        if not res:
            raise UserNotFoundError(f"User for api key {api_key} not found.")

        return res["user_pk"]

    def delete(self, user_pk: str) -> None:
        delete_query = delete(user_api_key_table).where(user_api_key_table.c.user_pk == user_pk)

        res = self._connection.execute(delete_query)

        if not res.rowcount:
            raise UserApiKeyNotFoundError(f"User with id {user_pk} doesn't have api key.")

    def _update(self, user_pk: str, api_key: str) -> RowProxy:
        update_query = (
            update(user_api_key_table)
            .where(user_api_key_table.c.user_pk == user_pk)
            .values(api_key=api_key)
            .returning(user_api_key_table.c.api_key)
        )

        return self._connection.execute(update_query).fetchone()

    def _insert(self, user_pk: str, api_key: str) -> RowProxy:
        insert_query = (
            insert(user_api_key_table).values(user_pk=user_pk, api_key=api_key).returning(user_api_key_table.c.api_key)
        )

        try:
            res = self._connection.execute(insert_query).fetchone()
        except StatementError as err:
            if extract_database_error_type(err, self._database) == DatabaseErrorTypeEnum.FOREIGN_KEY_VIOLATION:
                raise UserNotFoundError(f"User with id {user_pk} doesn't exist")
            raise

        return res

    @property
    def _connection(self) -> Connection:
        return self._database.get_connection()
