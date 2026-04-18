from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class DateTimeRange:
    start: Optional[datetime] = None
    end: Optional[datetime] = None
