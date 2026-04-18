from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ListMetaDataModel(BaseModel):
    total: int
    size: int


class ListDataModel(BaseModel, Generic[T]):
    meta: ListMetaDataModel
    result: list[T]
