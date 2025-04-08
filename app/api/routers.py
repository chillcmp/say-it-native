from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.db.session import get_db
from app.models import User
from app.schemas.auth import UserCreate, LoginRequest
from app.schemas.text_edit import TextInput
from app.services.auth_service import register_user, login_user, get_current_user
from app.services.text_edit_service import run_text_edit
from app.services.text_editors import HFTextEditor

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


@router.post("/edit")
def edit_text(data: TextInput, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    editor = HFTextEditor()
    result = run_text_edit(
        user_id=current_user.id,
        text=data.text,
        editor=editor,
        db=db
    )
    return result
