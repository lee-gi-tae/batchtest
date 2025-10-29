from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

from .db import SessionLocal
from .models import Repo


# url 들어오면 int로 반환
def create_repo_id(repo_url: str) -> int:
    db = SessionLocal()
    # 이미 있으면 id만 반환
    try:
        exists_id = db.execute(select(Repo.id).where(Repo.repo_url == repo_url)).scalar_one_or_none()
        # 이미 있으면 그 id를 반환
        if exists_id is not None:
            return int(exists_id)

        # 만약에 없다면 insert해서 id 발급
        try:
            new_id = db.execute(insert(Repo).values(repo_url=repo_url).returning(Repo.id)).scalar_one()
            db.commit()
            return int(new_id)

        # 만약에 동시 요청 들어오면 하나는 성공 하나는 unique위반으로 롤백후 다시 조회
        except IntegrityError:
            db.rollback()
            fixed_id = db.execute(select(Repo.id).where(Repo.repo_url == repo_url)).scalar_one()
            return int(fixed_id)

    finally:
        db.close()

def callme():
    return "addy"
