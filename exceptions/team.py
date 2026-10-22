from http import HTTPStatus

from exceptions.base import BaseError


class TeamError(BaseError):
    def __init__(self, message: str, status_code: HTTPStatus):
        super().__init__(message, status_code)


class TeamNotFoundError(TeamError):
    def __init__(
        self,
        message: str = "You're not in a team",
        status_code: HTTPStatus = HTTPStatus.NOT_FOUND,
    ):
        super().__init__(message, status_code)


class TeamPermissionError(TeamError):
    def __init__(
        self,
        message: str = "Only the team owner can do that",
        status_code: HTTPStatus = HTTPStatus.FORBIDDEN,
    ):
        super().__init__(message, status_code)


class TeamConflictError(TeamError):
    def __init__(self, message: str, status_code: HTTPStatus = HTTPStatus.CONFLICT):
        super().__init__(message, status_code)
