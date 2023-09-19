from typing import Optional, Any, Union

from django.http import JsonResponse
from ninja import Schema


class ResponseWithData(Schema):
    data: Union[list, dict]
    message: str


class ResponseWithError(Schema):
    errors: str
    message: str


class Response:

    @staticmethod
    def response_with_data(status_code: int = 200, message: str = "Operation Successful", data: dict | list = {}):
        return JsonResponse(dict(data=data, message=message), status=status_code)

    @staticmethod
    def response_with_error(status_code: int = 400, message: str = "Operation Failed", errors: str = ""):
        return JsonResponse(dict(message=message, errors=errors), status=status_code)
