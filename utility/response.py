from typing import Optional, Any, Union

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
        return dict(status_code=status_code, data=data, message=message)


    @staticmethod
    def response_with_error(status_code: int = 400, message: str = "Operation Failed", errors: str = ""):
        return dict(status_code=status_code, message=message, errors=errors)