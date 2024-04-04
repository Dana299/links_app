from abc import ABC, abstractmethod


class AbstractRepository(ABC):
    @abstractmethod
    def add_one():
        """Create a new record."""

    @abstractmethod
    def delete_by_id():
        """Delete a record."""


class SqlAlchemyRepository(AbstractRepository):

    def __init__(self, session):
        self.session = session
