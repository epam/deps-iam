from dataclasses import dataclass
from typing import Optional, Union

__all__ = [
    "BodyResource",
    "CorleoneBodyResource",
    "DocumentBodyResource",
    "PreprocessBodyResource",
    "OCRBodyResource",
    "ValidationBodyResource",
    "TablesBodyResourse",
    "ParsedDataBodyResourse",
    "UnifierBodyResourse",
    "DocumentTypeBodyResourse",
]

Document = Optional[list[Union[str, int]]]


@dataclass
class DocumentBodyResource:
    document: Document
    label: Optional[list[str]]


@dataclass
class CorleoneBodyResource:
    document: Document


@dataclass
class PreprocessBodyResource:
    document: Document


@dataclass
class OCRBodyResource:
    blob_file: Optional[list[str]]


@dataclass
class ValidationBodyResource:
    document: Document


@dataclass
class TablesBodyResourse:
    blob_file: Optional[list[str]]


@dataclass
class ParsedDataBodyResourse:
    document: Document


@dataclass
class UnifierBodyResourse:
    document: Document


@dataclass
class DocumentTypeBodyResourse:
    document_type: Optional[list[str]]


BodyResource = Union[
    DocumentBodyResource,
    CorleoneBodyResource,
    PreprocessBodyResource,
    OCRBodyResource,
    ValidationBodyResource,
    TablesBodyResourse,
    ParsedDataBodyResourse,
    UnifierBodyResourse,
    DocumentTypeBodyResourse,
]
