import os
from datetime import timedelta, datetime, timezone

from dotenv import load_dotenv
from fastapi import HTTPException, Depends
import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.db.session import get_db
from app.logger import logger
from app.models.user import User
from app.schemas.auth import UserCreate, LoginRequest


load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def register_user(request: UserCreate, db: Session) -> tuple[dict, int]:
    user = db.query(User).filter(User.email == request.email).first()
    if user:
        return {"message": f"User {user.email} already exists."}, 409

    hashed_password = pwd_context.hash(request.password)
    new_user = User(email=request.email, hashed_password=hashed_password)

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": f"User {new_user.email} registered with ID={new_user.id}."}, 201
    except Exception as e:
        db.rollback()
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


def _create_jwt_token(data: dict, expires_hours: int = 24) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=expires_hours)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def login_user(request: LoginRequest, db: Session) -> tuple[dict, int]:
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not pwd_context.verify(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = _create_jwt_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}, 200


def get_current_user(db: Session = Depends(get_db),
                     authorization: HTTPAuthorizationCredentials = Depends(security)) -> User:
    token = authorization.credentials
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"verify_exp": True},
        )
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
