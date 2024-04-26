from dataclasses import dataclass
from typing import List, Optional

from src.web.schemes import OkResponseSchema


@dataclass
class ProcessingRequestSchema:
    id: int
    status: str
    total_count: Optional[int]
    processed_count: Optional[int]
    errors_count: Optional[int]
    error_urls: List[str]