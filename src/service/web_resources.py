import os

from src import app
from src.repositories.processing_requests import ProcessingRequestRepository
from src.repositories.web_resources import WebResourceRepository
from src.schemes.processing_requests import ProcessingRequestSchema
from src.schemes.web_resources import ResourceBaseSchema, ZipFileRequestSchema
from src.service import exceptions
from src.service.exceptions import ResourceNotFoundError
from src.tasks import process_zip_archive
from src.utils import ziploader
from src.utils.urlparser import parse_url


class WebResourceService:

    def __init__(
        self,
        resource_repo: WebResourceRepository,
        processing_request_repo: ProcessingRequestRepository
    ):
        self.resource_repo = resource_repo
        self.processing_requests_repo = processing_request_repo

    def create_resource_from_url(self, valid_url: str) -> ResourceBaseSchema:
        """
        Create single web resource in DB.
        Raise exception if already exists.
        """
        parsed_url = parse_url(valid_url)
        existing_resource = self.resource_repo.get_by_full_url(parsed_url.full_url)
        if not existing_resource:
            web_resource = self.resource_repo.add_one(parsed_url)
            # TODO: добавить создание объекта новости
            return web_resource
        else:
            raise exceptions.AlreadyExistsError

    def create_resources_from_file(self, valid_file: ZipFileRequestSchema) -> ProcessingRequestSchema:
        """Create a task for processing multiple web resources from the file."""
        if not ziploader.allowed_file(valid_file.file.filename):
            raise exceptions.InvalidFileFormatError("File format is not in allowed extensions.")
        filename = ziploader.make_uuid_filename(valid_file.file.filename)
        valid_file.file.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename,
            )
        )
        processing_request = self.processing_requests_repo.add_one()
        process_zip_archive.delay(
            zip_file=filename,
            request_id=processing_request.id
        )
        return processing_request

    def delete_resource(self, resource_id: str):
        """Delete resource and create event."""
        try:
            self.resource_repo.delete_by_id(resource_id)
        except ResourceNotFoundError as e:
            raise e
