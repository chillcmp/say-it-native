from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import LoginRequest
from app.services.auth_service import register_user

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.get("/")
def hello():
    return {"message": "Hello from SayItNative!"}


@router.post("/register")
def register(request: LoginRequest, db: Session = Depends(get_db)):
    return register_user(request, db)
