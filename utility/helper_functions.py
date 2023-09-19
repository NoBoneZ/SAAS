from typing import Any

from django.http import HttpRequest
from ninja.parser import Parser
import orjson


class ORJSONParser(Parser):

    def parse_body(self, request: HttpRequest) -> dict | str | Any:
        return orjson.loads(request.body)


def parse_pydantic_errors(errors: list) -> dict:
    error_dict = dict()
    if isinstance(errors, list):
        for obj in errors:
            loc = obj.get("loc")[-1]
            msg = obj.get("msg")
            error_dict.update({loc: msg})

        return error_dict

    return dict()