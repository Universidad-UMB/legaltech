from typing import ClassVar


class ApplicationError(Exception):
    status_code: ClassVar[int] = 500
    title: ClassVar[str] = "Internal Server Error"
    detail: ClassVar[str] = "An unexpected error occurred."


class ForbiddenOperation(ApplicationError):
    status_code = 403
    title = "Forbidden"
    detail = "The operation is not permitted."


class ResourceNotFound(ApplicationError):
    status_code = 404
    title = "Not Found"
    detail = "The requested resource was not found."


class ResourceConflict(ApplicationError):
    status_code = 409
    title = "Conflict"
    detail = "The operation conflicts with the current resource state."


class InvalidInput(ApplicationError):
    status_code = 422
    title = "Unprocessable Content"
    detail = "The request does not satisfy the API contract."
