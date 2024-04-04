from enum import Enum
from typing import Optional

from pydantic import BaseModel


class StatusOption(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class OkResponseSchema(BaseModel):
    status: StatusOption = StatusOption.SUCCESS
    code: int = 200
    data: Optional[dict]