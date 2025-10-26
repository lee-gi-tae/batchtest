from sqlalchemy import TIMESTAMP, BigInteger, Column, ForeignKey, Index, Integer, Text, UniqueConstraint
from sqlalchemy.orm import declarative_base  # orm모델의 베이스클래스를 만드는 도구
from sqlalchemy.sql import func

Base = declarative_base()


class Repo(Base):
    __tablename__ = "repos"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    repo_url = Column(Text, nullable=False, unique=True)
    license = Column(String(50))
    allow_indexing = Column(Boolean)
    head_coomit_sha = Column(String(40))


class Run(Base):
    __tablename__ = "runs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    repo_id = Column(BigInteger, ForeignKey("repos.id"), nullable=False)
    # 처리 대상 커밋/브랜치 문자열(예: 짧은 해시, 'main', 'feature/xyz')
    now_commit_sha = Column(string(40), nullable=False)
    # 실행 범위/의미(예: 'pr' 또는 'main')
    scope = Column(string(20), nullable=False)
    # 실행 상태: 'running' | 'success' | 'failed' | 'partial_success'
    status = Column(string(20), nullable=False)
    started_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    finished_at = Column(TIMESTAMP(timezone=True))
    processed_count = Column(Integer, server_default="0")
    failed_count = Column(Integer, server_default="0")
    error_msg = Column(Text)

    # __table_args__ = (
    #     # repo_id + started_at 조합으로 최근 실행 이력 빠르게 보기
    #     Index("idx_runs_repo_started_at", "repo_id", "started_at"),
    #     # repo_id + commit으로 특정 커밋 결과 빠르게 찾기
    #     Index("idx_runs_repo_commit", "repo_id", "commit"),
    # )
