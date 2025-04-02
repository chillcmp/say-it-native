import bcrypt
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import LoginRequest


def register_user(request: LoginRequest, db: Session) -> tuple[dict, int]:
    user = db.query(User).filter(User.email == request.email).first()
    if user:
        return {"message": f"User {user.email} already exists."}, 409

    hashed_password = bcrypt.hashpw(password=request.password.encode(encoding="utf-8"),
                                    salt=bcrypt.gensalt()).decode("utf-8")
    new_user = User(email=request.email, hashed_password=hashed_password)

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": f"User {new_user.email} registered with ID={new_user.id}."}, 201
    except Exception as e:
        db.rollback()
        raise e
