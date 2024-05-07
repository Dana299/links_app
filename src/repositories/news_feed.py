from src.db import models
from src.repositories.base import SqlAlchemyRepository


class NewsFeedRepository(SqlAlchemyRepository):
    def add_one(self, resource_id: int, event: models.EventType):
        """Create new NewsFeedItem for resource with the given id."""
        news_item = models.NewsFeedItem(
            event_type=event,
            resource_id=resource_id
        )
        self.session.add(news_item)
        self.session.commit()
