from django.http import JsonResponse
from ninja import NinjaAPI
from ninja.errors import ValidationError

from accounts.api import router as accounts_router
from utility.authorization import ActiveUserAuth
from utility.exception import InvalidTokenError
from utility.helper_functions import ORJSONParser, parse_pydantic_errors, ORJSONRenderer

api = NinjaAPI(auth=ActiveUserAuth(), parser=ORJSONParser(), renderer=ORJSONRenderer())

api.add_router("auth/", accounts_router)


@api.exception_handler(InvalidTokenError)
def invalid_token_error(request, exc):
    return api.create_response(request, data=dict(message="unauthorized"), status=401)


@api.exception_handler(ValidationError)
def validation_errors(request, exc):
    errors = vars(exc).get('errors')
    parsed_errors = parse_pydantic_errors(errors)
    return JsonResponse({'message': "Validation Error", 'errors': parsed_errors}, status=400)