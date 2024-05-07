from typing import List, Optional

import pytest

from src.repositories.base import AbstractRepository
from src.schemes.web_resources import ResourceNoUUIDSchema
from src.service import exceptions
from src.service.web_resources import WebResourceService


class FakeResourceRepository(AbstractRepository):

    def __init__(self, resources: List[ResourceNoUUIDSchema]):
        self._resources = resources

    def add_one(self, resource):
        self._resources.append(resource)
        return resource

    def delete_by_id(self, resource_id):
        try:
            del self._resources[resource_id - 1]
            return True
        except IndexError:
            raise exceptions.ResourceNotFoundError

    def get_by_full_url(self, url) -> Optional[str]:
        for resource in self._resources:
            if resource.full_url == url:
                return resource


class FakeProcessingRequestRepository(AbstractRepository):

    def add_one(self):
        pass

    def delete_by_id(self):
        pass


empty_resource_repo = FakeResourceRepository([])
processing_request_repo = FakeProcessingRequestRepository()


def test_create_single_resource():
    test_resource = "http://example.com"
    service = WebResourceService(empty_resource_repo, processing_request_repo)
    result = service.create_resource_from_url(test_resource)
    assert result == ResourceNoUUIDSchema(
        full_url="http://example.com",
        protocol="http",
        domain="example.com",
        domain_zone="com",
        url_path="",
        query_params={},
    )


def test_error_while_creating_existing_resource():
    resource_repo = FakeResourceRepository(
        [
            ResourceNoUUIDSchema(
                full_url="http://example.com",
                protocol="http",
                domain="example.com",
                domain_zone="com",
                url_path="",
                query_params={},
            )
        ]
    )
    service = WebResourceService(resource_repo, processing_request_repo)

    with pytest.raises(exceptions.AlreadyExistsError):
        service.create_resource_from_url("http://example.com")


def test_delete_resource():
    resource_repo = FakeResourceRepository(
        [
            ResourceNoUUIDSchema(
                full_url="http://example.com",
                protocol="http",
                domain="example.com",
                domain_zone="com",
                url_path="",
                query_params={},
            )
        ]
    )
    service = WebResourceService(resource_repo, processing_request_repo)
    service.delete_resource(1)
    assert resource_repo._resources == []


def test_delete_missing_resource():
    resource_repo = FakeResourceRepository(
        [
            ResourceNoUUIDSchema(
                full_url="http://example.com",
                protocol="http",
                domain="example.com",
                domain_zone="com",
                url_path="",
                query_params={},
            )
        ]
    )
    service = WebResourceService(resource_repo, processing_request_repo)
    with pytest.raises(exceptions.ResourceNotFoundError):
        service.delete_resource(2)
