from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.deps import get_db
from backend.app.models.domain import Domain
from backend.app.models.logs import DailyLog
from backend.app.models.user import User
from backend.app.models.finance import IncomeEntry
from backend.app.schemas.daily_log import DailyLogCreate, DailyLogRead
from backend.app.schemas.finance import IncomeInput
from backend.app.services.xp_service import add_xp_to_domain

router = APIRouter()


def get_user(db: Session, tg_id: str) -> User:
    user = db.query(User).filter(User.tg_id == tg_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return user


def _apply_xp_updates(db: Session, user: User, payload: DailyLogCreate):
    total_xp = 0
    breakdown: list[dict] = []
    for xp_entry in payload.xp_updates:
        domain = (
            db.query(Domain)
            .filter(Domain.id == xp_entry.domain_id, Domain.user_id == user.id)
            .first()
        )
        if not domain:
            raise HTTPException(404, f"Domain {xp_entry.domain_id} not found for user")
        updated = add_xp_to_domain(db, user, domain, xp_entry.xp)
        breakdown.append(
            {
                "domain_id": domain.id,
                "domain_name": domain.name,
                "xp": xp_entry.xp,
                "new_level": updated.current_level,
            }
        )
        total_xp += xp_entry.xp
    return total_xp, breakdown


def _attach_finances(db: Session, user: User, log: DailyLog, finances: list[IncomeInput]):
    for record in finances:
        entry = IncomeEntry(
            user_id=user.id,
            daily_log_id=log.id,
            amount=record.amount,
            source=record.source,
            description=record.description,
            received_at=record.received_at or log.log_date,
        )
        db.add(entry)


@router.post("/", response_model=DailyLogRead)
def create_daily_log(tg_id: str, payload: DailyLogCreate, db: Session = Depends(get_db)):
    user = get_user(db, tg_id)
    log_date = payload.log_date or date.today()

    existing = (
        db.query(DailyLog)
        .filter(DailyLog.user_id == user.id, DailyLog.log_date == log_date)
        .first()
    )
    if existing:
        raise HTTPException(400, "Daily log for this date already exists")

    log = DailyLog(
        user_id=user.id,
        log_date=log_date,
        summary=payload.summary,
        accomplishments=payload.accomplishments,
        blockers=payload.blockers,
        rating=payload.rating,
    )
    db.add(log)
    db.flush()

    total_xp, breakdown = _apply_xp_updates(db, user, payload)
    log.total_xp_awarded = total_xp
    log.xp_breakdown = breakdown
    log.xp_pulse = payload.xp_pulse if payload.xp_pulse is not None else total_xp > 0

    _attach_finances(db, user, log, payload.finances)

    db.commit()
    db.refresh(log)
    return log


@router.get("/", response_model=list[DailyLogRead])
def list_daily_logs(tg_id: str, limit: int = 30, db: Session = Depends(get_db)):
    user = get_user(db, tg_id)
    logs = (
        db.query(DailyLog)
        .filter(DailyLog.user_id == user.id)
        .order_by(DailyLog.log_date.desc())
        .limit(limit)
        .all()
    )
    return logs


@router.get("/latest", response_model=DailyLogRead)
def get_latest_log(tg_id: str, db: Session = Depends(get_db)):
    user = get_user(db, tg_id)
    log = (
        db.query(DailyLog)
        .filter(DailyLog.user_id == user.id)
        .order_by(DailyLog.log_date.desc())
        .first()
    )
    if not log:
        raise HTTPException(404, "No logs yet")
    return log

