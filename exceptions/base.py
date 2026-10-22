from http import HTTPStatus


class BaseError(Exception):
    """Domain error that the API turns into a JSON `{"detail": ...}` response."""

    default_message = "Something went wrong"
    default_status = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(
        self, message: str | None = None, status_code: HTTPStatus | None = None
    ):
        self.message = message or self.default_message
        self.status_code = status_code or self.default_status
        super().__init__(self.message)
