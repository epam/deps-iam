from enum import StrEnum

__all__ = ["ServiceName"]


class ServiceName(StrEnum):
    DOCUMENT = "document"
    CORLEONE = "corleone"
    PREPROCESS = "preprocess"
    OCR = "ocr"
    VALIDATION = "validation"
    FILE_STORAGE = "storage"
    TABLES = "tables"
    PARSED_DATA = "parsed-data"
    IMAGE_PREPROCESS = "image-preprocess"
    IAM = "iam"
    UNIFIER = "unifier"
    EXTRACTION = "extraction"
    DOCUMENT_TYPE = "document-type"
