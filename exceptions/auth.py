from http import HTTPStatus

from exceptions.base import BaseError


class AuthError(BaseError):
    default_message = "Authentication failed"
    default_status = HTTPStatus.BAD_REQUEST


class AuthCredentialsError(AuthError):
    default_message = "Could not validate credentials or user is inactive"
    default_status = HTTPStatus.UNAUTHORIZED


class EmailTakenError(AuthError):
    default_message = "Email already registered"


class UserNotFoundError(AuthError):
    default_message = "User not found"
    default_status = HTTPStatus.NOT_FOUND


class UserAlreadyActiveError(AuthError):
    default_message = "User is active"


class InvalidCodeError(AuthError):
    default_message = "Invalid code"
