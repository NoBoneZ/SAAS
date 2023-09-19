from ninja import Schema


class SignupSchema(Schema):
    email: str
    password: str
    username: str
    full_name: str
