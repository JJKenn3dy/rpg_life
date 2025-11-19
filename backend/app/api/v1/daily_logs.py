from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from backend.app.core.deps import get_db
from backend.app.models.daily_log import DailyLog
from backend.app.models.user import User
from backend.app.schemas.daily_log import DailyLogCreate, DailyLogRead
from backend.app.services.daily_logs import create_daily_log as create_daily_log_service

router = APIRouter()


def _get_user(db: Session, tg_id: str) -> User:
    user = db.query(User).filter(User.tg_id == tg_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return user


@router.post("/", response_model=DailyLogRead)
def create_daily_log(
    tg_id: str,
    payload: DailyLogCreate,
    db: Session = Depends(get_db),
):
    user = _get_user(db, tg_id)
    return create_daily_log_service(db=db, user=user, payload=payload)


@router.get("/", response_model=list[DailyLogRead])
def list_daily_logs(tg_id: str, db: Session = Depends(get_db)):
    user = _get_user(db, tg_id)
    return (
        db.query(DailyLog)
        .filter(DailyLog.user_id == user.id)
        .order_by(desc(DailyLog.log_date))
        .all()
    )


@router.get("/latest", response_model=DailyLogRead)
def get_latest_daily_log(tg_id: str, db: Session = Depends(get_db)):
    user = _get_user(db, tg_id)
    log = (
        db.query(DailyLog)
        .filter(DailyLog.user_id == user.id)
        .order_by(desc(DailyLog.log_date))
        .first()
    )
    if not log:
        raise HTTPException(404, "Daily log not found")
    return log
