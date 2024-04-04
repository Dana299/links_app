from src.db import models
from src.schemes import web_resources


def convert_web_resource_dto_to_db_model(
    web_resource: web_resources.ResourceBaseSchema
) -> models.WebResource:
    """Convert web resource DTO to DB model."""
    return models.WebResource(
        uuid=web_resource.uuid,
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
        uuid=web_resource.uuid,
        protocol=web_resource.protocol,
        domain=web_resource.domain,
        domain_zone=web_resource.domain_zone,
        url_path=web_resource.url_path,
        query_params=web_resource.query_params,
        screenshot=web_resource.screenshot,
    )
