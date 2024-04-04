from base64 import b64encode
from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, AnyHttpUrl, BaseModel, root_validator, validator
from werkzeug.datastructures import FileStorage

from src.web.schemes import OkResponseSchema


class LogRecordSchema(BaseModel):
    level: str
    message: str


class ListLogRecordSchema(BaseModel):
    logs: List[LogRecordSchema]


class ListLogRecordResponseSchema(OkResponseSchema):
    data: ListLogRecordSchema


class NewsFeedItemSchema(BaseModel):
    event_type: str
    timestamp: datetime


class ListNewsFeedItemSchema(BaseModel):
    events: List[NewsFeedItemSchema]


class NewsFeedItemListResponseSchema(OkResponseSchema):
    data: ListNewsFeedItemSchema


# class NewsFeedItemWithWebResourceSchema(NewsFeedItemSchema):
#     web_resource: ResourceBaseSchema

class FileRequestSchema(BaseModel):
    file: FileStorage

    @validator('file')
    def validate_file(cls, file):
        if file is None or file.filename == '':
            raise ValueError('File cannot be empty')
        return file

    class Config:
        arbitrary_types_allowed = True


class ZipFileRequestSchema(FileRequestSchema):
    @validator('file')
    def validate_file(cls, file):
        if file is None or file.filename == '':
            raise ValueError('File cannot be empty')

        if not file.filename.lower().endswith('.zip'):
            raise ValueError('Invalid file type. Only ZIP files are allowed.')

        return file


class ResourceAddRequestSchema(BaseModel):
    full_url: AnyHttpUrl


class ResourceBaseSchema(ResourceAddRequestSchema):
    uuid: UUID4
    protocol: str
    domain: str
    domain_zone: str
    url_path: Optional[str]
    query_params: Optional[dict]
    screenshot: Optional[str]

    @root_validator(pre=True)
    def convert_bytes_to_base64(cls, values):
        screenshot = values.get("screenshot")
        if screenshot is not None and isinstance(screenshot, bytes):
            values["screenshot"] = b64encode(screenshot).decode("utf-8")
        return values


class ResourceShortSchema(ResourceAddRequestSchema):
    status_code: Optional[int]
    is_available: Optional[bool]


class ResourceAddResponseSchema(ResourceBaseSchema, ResourceShortSchema):
    pass


class ListResourceSchema(BaseModel):
    resources: List[ResourceAddResponseSchema]


class PaginatedListResourceSchema(ListResourceSchema):
    meta: dict
    links: dict


class PaginatedListResourceResponseSchema(OkResponseSchema):
    data: PaginatedListResourceSchema


class ResourcePageSchema(ResourceBaseSchema):
    events: List[NewsFeedItemSchema]


class ResourcePageResponseSchema(OkResponseSchema):
    data: ResourcePageSchema