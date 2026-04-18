from typing import List

from pydantic import BaseModel, ConfigDict, Field


class BboxModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    y: float = Field(..., ge=0, le=1)
    x: float = Field(..., ge=0, le=1)
    w: float = Field(..., ge=0, le=1)
    h: float = Field(..., ge=0, le=1)
    page: int = 1

    @property
    def top(self) -> float:
        return self.y

    @property
    def left(self) -> float:
        return self.x

    @property
    def bottom(self) -> float:
        return self.y + self.h

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def centerx(self) -> float:
        return self.x + self.w / 2

    @property
    def centery(self) -> float:
        return self.y + self.h / 2


class WordBoxModel(BaseModel):
    content: str
    bbox: BboxModel
    confidence: float = Field(1.0, ge=0, le=1.0)


class TextLineModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    word_boxes: List[WordBoxModel] = Field(..., alias="wordBoxes")
