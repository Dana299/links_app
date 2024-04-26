from src.db import models
from src.schemes import web_resources, processing_requests


def convert_web_resource_dto_to_db_model(
    web_resource: web_resources.ResourceBaseSchema
) -> models.WebResource:
    """Convert web resource DTO to DB model."""
    return models.WebResource(
        full_url=web_resource.full_url,
        protocol=web_resource.protocol,
        domain=web_resource.domain,
        domain_zone=web_resource.domain_zone,
        url_path=web_resource.url_path,
        query_params=web_resource.query_params,
        screenshot=web_resource.screenshot,
    )


def convert_web_resource_db_model_to_dto(
    web_resource: models.WebResource
) -> web_resources.ResourceBaseSchema:
    """Convert web resource DB model to DTO."""
    return web_resources.ResourceBaseSchema(
        full_url=web_resource.full_url,
        uuid=web_resource.uuid,
        protocol=web_resource.protocol,
        domain=web_resource.domain,
        domain_zone=web_resource.domain_zone,
        url_path=web_resource.url_path,
        query_params=web_resource.query_params,
        screenshot=web_resource.screenshot,
    )


def convert_processing_request_db_model_to_dto(
    processing_request: models.FileProcessingRequest
) -> processing_requests.ProcessingRequestSchema:
    """Convert processing request DB model object to DTO."""
    return processing_requests.ProcessingRequestSchema(
        id=processing_request.id,
        status=processing_request.status,
        total_count=processing_request.total_count,
        processed_count=processing_request.processed_count,
        errors_count=processing_request.errors_count,
        error_urls=processing_request.error_urls,
    )
