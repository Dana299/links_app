class AlreadyExistsError(Exception):
    pass


class ResourceNotFoundError(Exception):
    pass


class ProcessingRequestNotFound(Exception):
    pass


class InvalidFileFormatError(Exception):
    pass


class NoCSVFileError(Exception):
    pass
