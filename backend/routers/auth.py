from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

try:
    from database import get_db
    from models.user import Token, User, UserCreate, UserLogin, UserOut
    from services.auth_service import (
        authenticate_user,
        get_current_user,
        list_users,
        register_user,
    )
except ImportError:
    from backend.database import get_db
    from backend.models.user import Token, User, UserCreate, UserLogin, UserOut
    from backend.services.auth_service import (
        authenticate_user,
        get_current_user,
        list_users,
        register_user,
    )

router = APIRouter(tags=["Authentication & Users"])


@router.post("/auth/register", response_model=Token, status_code=status.HTTP_200_OK)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, user_in)


@router.post("/auth/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    return authenticate_user(db, credentials)


@router.get("/auth/me", response_model=UserOut)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)


@router.get("/users", response_model=list[UserOut])
def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_users(db, current_user)
