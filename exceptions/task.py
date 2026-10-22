from http import HTTPStatus

from exceptions.base import BaseError


class TaskError(BaseError):
    default_message = "Task request failed"
    default_status = HTTPStatus.BAD_REQUEST


class TaskNotFoundError(TaskError):
    default_message = "Task not found"
    default_status = HTTPStatus.NOT_FOUND


class TaskNotAvailableTransitionError(TaskError):
    default_message = "Task not available transition"
