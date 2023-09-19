from ninja import Schema, Field


class SignupSchema(Schema):
    email: str
    password: str
    username: str = Field(min_length=8)
    full_name: str


class SignInSchema(Schema):
    email: str
    password: str


class RecoveryMailSchema(Schema):
    email: str


class ValidateRecoveryOTPSchema(Schema):
    otp: str = Field(min_length=6, max_length=6)
    email: str


class RecoveryChangePasswordSchema(Schema):
    email: str
    new_password: str
    confirm_password: str
