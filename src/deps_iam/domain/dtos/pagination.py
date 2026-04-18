from dataclasses import dataclass


@dataclass
class PaginationObject:
    page: int = 1
    per_page: int = 10
