from sqlalchemy.orm import Session
from backend.app.models.domain import Domain
from backend.app.models.user import User

BASE_XP = 50

def calc_xp_to_next(level: int) -> int:
    return int(BASE_XP * (level ** 1.5))

def recalc_global_level(db: Session, user: User):
    if not user.domains:
        return
    avg = sum(d.current_level for d in user.domains) / len(user.domains)
    user.current_global_level = min(100, int(avg))
    user.global_xp = int(avg * 100)
    db.add(user)
    db.flush()

def add_xp_to_domain(db: Session, user: User, domain: Domain, xp: int):
    domain.current_xp += xp

    # апгрейд уровня
    while domain.current_xp >= domain.xp_to_next_level and domain.current_level < 100:
        domain.current_xp -= domain.xp_to_next_level
        domain.current_level += 1
        domain.xp_to_next_level = calc_xp_to_next(domain.current_level)

    domain.progress_in_level = domain.current_xp / max(domain.xp_to_next_level, 1)

    db.add(domain)
    db.flush()

    recalc_global_level(db, user)

    return domain
