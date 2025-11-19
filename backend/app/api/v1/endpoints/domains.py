from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.deps import get_db
from backend.app.models.user import User
from backend.app.models.domain import Domain
from backend.app.schemas.level import DomainCreate, DomainRead
from backend.app.services.xp_service import add_xp_to_domain

router = APIRouter()

def get_user(db: Session, tg_id: str) -> User:
    user = db.query(User).filter(User.tg_id == tg_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return user

@router.post("/", response_model=DomainRead)
def create_domain(tg_id: str, payload: DomainCreate, db: Session = Depends(get_db)):
    user = get_user(db, tg_id)
    domain = Domain(user_id=user.id, name=payload.name)
    db.add(domain)
    db.commit()
    db.refresh(domain)
    return domain

@router.get("/", response_model=list[DomainRead])
def list_domains(tg_id: str, db: Session = Depends(get_db)):
    user = get_user(db, tg_id)
    return db.query(Domain).filter(Domain.user_id == user.id).all()

@router.post("/add-xp", response_model=DomainRead)
def add_xp(tg_id: str, domain_id: int, xp: int, db: Session = Depends(get_db)):
    user = get_user(db, tg_id)

    domain = db.query(Domain).filter(
        Domain.id == domain_id,
        Domain.user_id == user.id
    ).first()

    if not domain:
        raise HTTPException(404, "Domain not found")

    updated = add_xp_to_domain(db, user, domain, xp)
    db.commit()
    db.refresh(updated)
    return updated
