from enum import Enum

from pydantic import BaseModel


class CheckmarkTypeEnum(Enum):
    SQUARE_CHECKED = "square_checked"
    SQUARE_BLANK = "square_blank"
    SQUARE_CROSSED = "square_crossed"
    CIRCLED_ITEM = "circled_item"
    CIRCLE_BLANK = "circle_blank"
    CIRCLE_CHECKED = "circle_checked"
    CORRECTED_ITEM = "corrected_item"
    SINGLE_CHECKMARK = "single_checkmark"
    CIRCLE_FILLED = "circle_filled"
    CIRCLE_CROSSED = "circle_crossed"
    SINGLE_CROSS = "single_cross"


class OMRBoxModel(BaseModel):
    x: float
    y: float
    w: float
    h: float
    page: int = 1


class OMRDataModel(BaseModel):
    label: CheckmarkTypeEnum
    value: bool
    coordinates: OMRBoxModel
    confidence: float
