from typing import Optional, Any

from ninja.security import HttpBearer
from rest_framework_simplejwt.tokens import AccessToken

from .exception import InvalidTokenError
from accounts.models import User


class ActiveUserAuth(HttpBearer):

    def authenticate(self, request, token) -> Optional[Any]:
        if token:
            try:
                access_token_obj = AccessToken(token)
                user_id = access_token_obj["user_id"]
                user = User.objects.filter(id=user_id).first()
                if not user:
                    return InvalidTokenError()
                return user
            except:
                return InvalidTokenError()
        return InvalidTokenError()
