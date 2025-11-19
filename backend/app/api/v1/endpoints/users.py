from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.deps import get_db
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserRead

router = APIRouter()

@router.post("/register", response_model=UserRead)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.tg_id == payload.tg_id).first()
    if user:
        return user
    user = User(
        tg_id=payload.tg_id,
        username=payload.username,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/by-tg/{tg_id}", response_model=UserRead)
def get_user_by_tg(tg_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.tg_id == tg_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return user
