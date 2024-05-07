from src.db import models
from src.db.converters import convert_processing_request_db_model_to_dto
from src.repositories.base import SqlAlchemyRepository
from src.schemes.processing_requests import ProcessingRequestSchema
from src.service.exceptions import ProcessingRequestNotFound


class ProcessingRequestRepository(SqlAlchemyRepository):
    def get_by_id(self, uuid: str) -> ProcessingRequestSchema:
        """Get file processing request by given id. Raise exception otherwise."""
        processing_request = models.FileProcessingRequest.query.filter_by(id=id).first()
        if processing_request:
            return convert_processing_request_db_model_to_dto(processing_request)
        else:
            raise ProcessingRequestNotFound

    def add_one(self) -> ProcessingRequestSchema:
        """Create new file processing request in DB."""
        db_processing_request = models.FileProcessingRequest()
        self.session.add(db_processing_request)
        self.session.commit()
        return convert_processing_request_db_model_to_dto(db_processing_request)

    def delete_by_id(self):
        pass
