from typing import Optional

from src.db import models
from src.db.converters import (convert_web_resource_db_model_to_dto,
                               convert_web_resource_dto_to_db_model)
from src.repositories.base import SqlAlchemyRepository
from src.schemes.web_resources import ResourceBaseSchema
from src.service.exceptions import ResourceNotFoundError


class WebResourceRepository(SqlAlchemyRepository):
    def get_by_uuid(self, uuid: str) -> ResourceBaseSchema:
        """Get WebResource by given uuid. Raise exception otherwise."""
        web_resource = models.WebResource.query.filter_by(uuid=uuid).first()
        if web_resource:
            return convert_web_resource_db_model_to_dto(web_resource)
        else:
            raise ResourceNotFoundError

    def delete_by_uuid(self, uuid: str):
        """Delete WebResource with the given id. Raise exception otherwise."""
        resource = models.WebResource.query.filter_by(uiid=uuid).first()

        if not resource:
            raise ResourceNotFoundError

        self.session.delete(resource)
        self.session.commit()

    def delete_by_id(self, id: int):
        """Delete WebResource with given id."""
        resource = models.WebResource.query.filter_by(id=id).first()

        if not resource:
            raise ResourceNotFoundError

        self.session.delete(resource)
        self.session.commit()

    def get_by_full_url(self, full_url: str) -> Optional[ResourceBaseSchema]:
        """Get WebResource by given full url. Return None otherwise."""
        web_resource = models.WebResource.query.filter_by(full_url=full_url).first()
        if web_resource:
            return convert_web_resource_db_model_to_dto(web_resource)
        else:
            return None

    def add_one(self, web_resource: ResourceBaseSchema):
        """Create new web resource in DB."""
        db_resource = convert_web_resource_dto_to_db_model(web_resource)
        self.session.add(db_resource)
        self.session.commit()
        return convert_web_resource_db_model_to_dto(db_resource)

    def update_resource_availability_counter(
        self,
        resource: models.WebResource,
        is_available: bool
    ):
        """Update or reset counter for availability of web resource."""
        if is_available:
            resource.unavailable_count = 0
        else:
            resource.unavailable_count += 1
        self.session.add(resource)
        self.session.commit()


class NewsFeedRepository(SqlAlchemyRepository):
    def add_news_item(self, resource_id: int, event: models.EventType):
        """Create new NewsFeedItem for resource with the given id."""
        news_item = models.NewsFeedItem(
            event_type=event,
            resource_id=resource_id
        )
        self.session.add(news_item)
        self.session.commit()
