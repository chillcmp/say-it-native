from pydantic import BaseModel, EmailStr, constr


class LoginRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=8)
