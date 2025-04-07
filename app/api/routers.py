from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.db.session import get_db
from app.schemas.auth import UserCreate, LoginRequest
from app.services.auth_service import register_user, login_user, get_current_user

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.get("/")
def hello():
    return {"message": "Hello from SayItNative!"}


@router.post("/register")
def register(request: UserCreate, db: Session = Depends(get_db)):
    response, status_code = register_user(request, db)
    return JSONResponse(status_code=status_code, content=response)


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    response, status_code = login_user(request, db)
    return JSONResponse(status_code=status_code, content=response)


@router.get("/secure-endpoint", dependencies=[Depends(get_current_user)])
def secure_endpoint():
    return {"message": "You've accessed a secure endpoint!"}
