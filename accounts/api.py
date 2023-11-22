from asgiref.sync import sync_to_async

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.utils.timezone import now
from ninja import Router
from rest_framework_simplejwt.tokens import RefreshToken

from .schema import (SignupSchema, SignInSchema, RecoveryMailSchema, ValidateRecoveryOTPSchema,
                     RecoveryChangePasswordSchema)
from accounts.models import User, AccountRecoveryOTP
from utility.helper_functions import password_validator, send_recovery_mail_with_otp
from utility.response import Response, ResponseWithData, ResponseWithError

router = Router()
response = Response


@router.post("sign-up/", auth=None, response={200: ResponseWithData, 400: ResponseWithError})
async def sign_up(request, data: SignupSchema):
    data = data.dict()

    username = data.get("username").lower()
    email = data.get("email").lower()
    full_name = data.get("full_name").title()
    password = data.get("password")

    if await User.objects.filter(username=username).aexists():
        return response.response_with_error(errors="Username is already taken !")

    if await User.objects.filter(email=email).aexists():
        return response.response_with_error(errors="Email is already taken !")

    try:
        validate_password(password)
    except Exception as e:
        return response.response_with_error(errors="".join(e))

    if not password_validator(password):
        return response.response_with_error(errors="Password needs to be more than 7 characters long and contain a "
                                                   "digit, a symbol, an uppercase letter and a lowercase letter !")

    await User.objects.acreate(username=username, email=email, full_name=full_name, password=make_password(password))

    return response.response_with_data(status_code=201)


@router.get("check-username/", auth=None, response={200: ResponseWithData})
async def check_username(request, username: str):
    check = await User.objects.filter(username=username.lower()).aexists()
    message = "Username is available" if not check else "Username is not available"
    return response.response_with_data(message=message)


@router.get("check-email/", auth=None, response={200: ResponseWithData})
async def check_email(request, email: str):
    check = await User.objects.filter(email=email.lower()).aexists()
    message = "Email is available" if not check else "Email is not available"
    return response.response_with_data(message=message)


@router.post("sign-in/", auth=None, response={201: ResponseWithData, 400: ResponseWithError})
async def sign_in(request, data: SignInSchema):
    data = data.dict()

    email = data.get("email").lower()
    password = data.get("password")

    user = await User.objects.filter(email=email).afirst()
    if not user:
        return response.response_with_error(errors="User does not exist")

    if not await sync_to_async(authenticate)(request, username=user.username, password=password):
        return response.response_with_error(errors="Invalid username or password")

    refresh_token = RefreshToken.for_user(user)
    data = dict(refresh_token=str(refresh_token), access_token=str(refresh_token.access_token))
    return response.response_with_data(data=data, status_code=201)


@router.post("recover-account/", auth=None, response={201: ResponseWithData, 400: ResponseWithError})
async def send_recovery_mail(request, data: RecoveryMailSchema):
    data = data.dict()
    email = data.get("email").lower()
    user = await User.objects.filter(email=email).afirst()
    if not user:
        return response.response_with_error(errors="User does not exist")

    await send_recovery_mail_with_otp(user_id=user.id, email=email, full_name=user.full_name)

    return response.response_with_data()


@router.post("validate-recovery-otp/", auth=None, response={204: ResponseWithData, 400: ResponseWithError})
async def validate_recovery_otp(request, data: ValidateRecoveryOTPSchema):
    data = data.dict()
    email = data.get("email").lower()
    otp = data.get("otp")
    user = await User.objects.only("id", "email", "full_name").filter(email=email).afirst()
    if not user:
        return response.response_with_error(errors="User does not exist")

    otp_obj = await AccountRecoveryOTP.objects.only("expires").filter(user__email=email, otp=otp).afirst()

    if not otp_obj:
        return response.response_with_error(errors="Invalid OTP")

    if otp_obj.expires > now():
        await send_recovery_mail_with_otp(user_id=user.id, email=user.email, full_name=user.full_name)
        return response.response_with_error(errors="This otp has expired, a new OTP has been sent to your email")

    otp_obj.delete()
    return response.response_with_data(status_code=204)


@router.post("change-password-recovery/", auth=None, response={204: ResponseWithData, 400: ResponseWithError})
async def recovery_change_password(request, data: RecoveryChangePasswordSchema):
    data = data.dict()

    email = data.get("email").lower()
    password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    if password != confirm_password:
        return response.response_with_error(errors="Passwords do not match")

    user = await User.objects.filter(email=email).afirst()
    if not user:
        return response.response_with_error(errors="Invalid email")

    user.password = make_password(password)
    await user.asave(update_fields=["password"])

    return response.response_with_data()
