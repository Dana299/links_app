from src.repositories.web_resources import WebResourceRepository
from src.schemes.web_resources import ResourceBaseSchema
from src.service import exceptions
from src.utils.urlparser import parse_url


class WebResourceService:

    def __init__(self, repo: WebResourceRepository):
        self.repo = repo

    def create_resource(self, valid_url: str) -> ResourceBaseSchema:
        parsed_url = parse_url(valid_url)
        existing_resource = self.repo.get_by_full_url(parsed_url.full_url)
        if not existing_resource:
            web_resource = self.repo.add_one(parsed_url)
            # TODO: добавить создание объекта новости
            return web_resource
        else:
            raise exceptions.AlreadyExistsError
