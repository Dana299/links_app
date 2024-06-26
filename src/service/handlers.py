import json
import os
from typing import Optional

from pydantic import ValidationError
from werkzeug.datastructures.structures import ImmutableMultiDict

from src import app
from src.db import models
from src.repositories.processing_requests import ProcessingRequestRepository
from src.repositories.web_resources import WebResourceRepository
from src.schemes.web_resources import (FileRequestSchema,
                                       PaginatedListResourceSchema,
                                       ResourceAddRequestSchema,
                                       ResourceAddResponseSchema,
                                       ResourceBaseSchema,
                                       ResourcePageResponseSchema,
                                       ResourcePageSchema,
                                       ZipFileRequestSchema)
from src.service import exceptions
from src.service.web_resources import WebResourceService
from src.tasks import FileProcessingTaskResponse, process_zip_archive
from src.utils import ziploader
from src.web.app import db


def handle_post_url_json(body) -> ResourceAddResponseSchema:
    resource_service = WebResourceService(
        WebResourceRepository(db.session),
        ProcessingRequestRepository(db.session),
    )
    try:
        resource_add_schema = ResourceAddRequestSchema(**body)

    except ValidationError as e:
        raise e

    try:
        resource = resource_service.create_resource_from_url(resource_add_schema.full_url)
        return resource

    except exceptions.AlreadyExistsError as e:
        raise e


def handle_post_url_file(files) -> int:
    resource_service = WebResourceService(
        WebResourceRepository(db.session),
        ProcessingRequestRepository(db.session),
    )
    try:
        validated_data = ZipFileRequestSchema(**files)
        return resource_service.create_resources_from_file(validated_data)

    except ValidationError as e:
        raise e


def handle_add_image_for_web_resource(files: ImmutableMultiDict, resource_uuid: str) -> None:
    try:
        web_resource = db.get_resource_by_uuid(resource_uuid)
        validated_data = FileRequestSchema(**files)
        db.add_image_to_resource(web_resource, validated_data.file)

    except exceptions.ResourceNotFoundError:
        raise

    except ValidationError as e:
        raise e


def handle_get_request_status(request_id, storage_client) -> FileProcessingTaskResponse:
    processing_request = db.get_file_processing_request_by_id(request_id)

    if not processing_request:
        raise exceptions.ResourceNotFoundError

    if processing_request.status == models.StatusOption.INPROCESS:
        task_id = processing_request.task_id
        status_info_from_storage = storage_client.get(name=task_id)

        if status_info_from_storage:
            status_info = json.loads(status_info_from_storage)
            return FileProcessingTaskResponse(**status_info)
        else:
            # TODO: unexpected case but should be handled
            ...

    else:
        status_info: FileProcessingTaskResponse = {
            "status": processing_request.status.value,
            "processed": processing_request.processed_count,
            "total": processing_request.total_count,
            "errors": {
                "count": processing_request.errors_count,
                "error_urls": processing_request.error_urls,
            }
        }

        return status_info


def handle_get_resources_with_filters(
    domain_zone: Optional[str],
    availability: Optional[str],
    resource_id: Optional[int],
    uuid: Optional[str],
    page: Optional[int],
    per_page: Optional[int],
) -> PaginatedListResourceSchema:

    query = db.get_web_resources_query(
        left_join=True,
        domain_zone=domain_zone,
        resource_id=resource_id,
        resource_uuid=uuid,
        is_available=availability,
    )

    paginated_resource_list = db.paginate_query(
        query,
        page,
        per_page,
        'main.get_resources',
    )

    paginated_resources_with_meta_data = PaginatedListResourceSchema(
        items=[
            ResourceBaseSchema(**item).dict() for item in paginated_resource_list["items"]
        ],
        meta=paginated_resource_list.get('_meta'),
        links=paginated_resource_list.get('_links')
    )

    return paginated_resources_with_meta_data


def handle_get_resource_data(resource_uuid: str) -> ResourcePageSchema:

    # TODO: refactor!!!

    try:
        page = db.get_resource_page(resource_uuid=resource_uuid)
        resource: models.WebResource = page[0][0]   # WebResource is on the 1 position in tuple
        events = []

        for item in page:
            news_item: models.NewsFeedItem = item[1]  # NewsFeedItem is on the 2 position in tuple
            if news_item:
                news_dict = {
                    "event_type": news_item.event_type.value,
                    "timestamp": news_item.timestamp.isoformat()
                }
                events.append(news_dict)

        resource_page = ResourcePageSchema(
            **resource.__dict__, events=events,
        )

        return resource_page

    except exceptions.ResourceNotFoundError:
        raise


# def handle_get_news_feed() -> NewsFeedItemSchema:
#     """Handle request for getting all news feed items."""
#     news_items_from_db = db.get_news_items()
#     feed_items = [
#         NewsFeedItemWithWebResourceSchema(
#             event_type=item.event_type.value,
#             timestamp=item.timestamp,
#             web_resource=ResourceBaseSchema(
#                 **item.resource.__dict__
#             )
#         )
#         for item in news_items_from_db
#     ]

#     return NewsFeedItemSchema(feed_items=feed_items)
