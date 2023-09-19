from datetime import timedelta
from random import sample
from re import search
from string import digits
from typing import Any

from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.timezone import now
from ninja.parser import Parser
from ninja.renderers import BaseRenderer
import orjson

from accounts.models import AccountRecoveryOTP


class ORJSONParser(Parser):

    def parse_body(self, request: HttpRequest) -> dict | str | Any:
        return orjson.loads(request.body)


class ORJSONRenderer(BaseRenderer):

    def render(self, request: HttpRequest, data: Any, *, response_status: int) -> Any:
        return orjson.dumps(data)


def parse_pydantic_errors(errors: list) -> dict:
    error_dict = dict()
    if isinstance(errors, list):
        for obj in errors:
            loc = obj.get("loc")[-1]
            msg = obj.get("msg")
            error_dict.update({loc: msg})

        return error_dict

    return dict()


def password_validator(password: str) -> bool:
    pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$'
    return search(pattern, password) is not None


def generate_digits(length: int = 6) -> str:
    return "".join(sample(digits, length))


@sync_to_async()
def generate_unique_otp() -> str:
    otp = generate_digits(6)

    if AccountRecoveryOTP.objects.filter(otp=otp).exists():
        return generate_unique_otp()
    return otp


async def send_recovery_mail_with_otp(user_id: int, email: str, full_name: str):
    otp = await generate_unique_otp()
    await AccountRecoveryOTP.objects.filter(user_id=user_id).adelete()
    await AccountRecoveryOTP.objects.acreate(user_id=user_id, otp=otp, expires=now() + timedelta(5))
    context = dict(name=full_name, otp=otp)
    template_name = "otp_email_template.html"
    receiver = (email,)
    msg_html = render_to_string(template_name, context)
    msg = EmailMessage(subject=f"Account Recovery mail for {full_name}", body=msg_html,
                       from_email=settings.EMAIL_HOST_USER, to=receiver)
    msg.content_subtype = "html"
    msg.send()
