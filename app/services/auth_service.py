import bcrypt
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.logger import logger
from app.models.user import User
from app.schemas.auth import LoginRequest


def register_user(request: LoginRequest, db: Session):
    user = db.query(User).filter(User.email == request.email).first()
    if user:
        return JSONResponse(status_code=409, content={"message": f"User {user.email} already exists."})

    hashed_password = bcrypt.hashpw(password=request.password.encode(encoding="utf-8"),
                                    salt=bcrypt.gensalt()).decode("utf-8")
    new_user = User(email=request.email, hashed_password=hashed_password)

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return JSONResponse(status_code=201,
                            content={"message": f"User {new_user.email} registered with ID={new_user.id}."})
    except Exception as e:
        db.rollback()
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
