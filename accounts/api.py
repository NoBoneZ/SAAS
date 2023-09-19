from ninja import Router

from .schema import SignupSchema
from accounts.models import User
from utility.response import Response, ResponseWithData

router = Router()
response = Response


@router.post("sign-up/", auth=None, response={201: ResponseWithData})
def sign_up(request, data: SignupSchema):
    data = data.dict()

    ...


@router.get("check-username/", auth=None, response={200: ResponseWithData})
def check_username(request, username: str):
    check = User.objects.filter(username=username).exists()
    message = "Username is available" if not check else "Username is not available"
    return response.response_with_data(message=message)
