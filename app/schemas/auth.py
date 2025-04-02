from pydantic import BaseModel, EmailStr, constr


class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
