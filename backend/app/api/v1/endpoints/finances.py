from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.deps import get_db
from backend.app.models.logs import DailyLog
from backend.app.models.finance import IncomeEntry
from backend.app.models.user import User
from backend.app.schemas.finance import IncomeCreate, IncomeRead

router = APIRouter()


def get_user(db: Session, tg_id: str) -> User:
    user = db.query(User).filter(User.tg_id == tg_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return user


@router.post("/", response_model=IncomeRead)
def create_income(tg_id: str, payload: IncomeCreate, db: Session = Depends(get_db)):
    user = get_user(db, tg_id)
    log = None
    if payload.daily_log_id:
        log = (
            db.query(DailyLog)
            .filter(DailyLog.id == payload.daily_log_id, DailyLog.user_id == user.id)
            .first()
        )
        if not log:
            raise HTTPException(404, "Daily log not found")

    received_at = payload.received_at or (log.log_date if log else date.today())
    income = IncomeEntry(
        user_id=user.id,
        daily_log_id=log.id if log else None,
        amount=payload.amount,
        source=payload.source,
        description=payload.description,
        received_at=received_at,
    )
    db.add(income)
    db.commit()
    db.refresh(income)
    return income


@router.get("/", response_model=list[IncomeRead])
def list_incomes(tg_id: str, limit: int = 100, db: Session = Depends(get_db)):
    user = get_user(db, tg_id)
    incomes = (
        db.query(IncomeEntry)
        .filter(IncomeEntry.user_id == user.id)
        .order_by(IncomeEntry.received_at.desc(), IncomeEntry.id.desc())
        .limit(limit)
        .all()
    )
    return incomes

