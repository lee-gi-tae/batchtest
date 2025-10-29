# app/main.py
# ------------------------------------------------------------
# 이 파일이 하는 일(요약)
# - FastAPI 서버 엔트리포인트.
# - POST /batch/run : repo_url(+ref) 받아서 → 덤프 → 임베딩 → Milvus 업서트까지 한 번에 실행.
# ------------------------------------------------------------
from pathlib import Path  # 이 문법: 경로 타입.
from fastapi import FastAPI  # 이 문법: FastAPI 서버.
from pydantic import BaseModel  # 이 문법: 요청/응답 스키마.

from app.config import HOST, PORT  # 이 코드: 서버 바인드 설정.
from app.github_downloader import dump_tarball  # 이 코드: 레포 내려받기 호출.
from app.embed_t5 import embed_directory        # 이 코드: 청킹+임베딩 호출.
from app.milvus_client import upsert_chunks     # 이 코드: 밀버스 업서트 호출.

app = FastAPI(title="batch-min")

class RunReq(BaseModel):
    # 이 문법: Pydantic 모델.
    # 이 코드: 요청에서 받아야 할 필드 정의.
    repo_url: str
    ref: str | None = None



@app.post("/batch/run", response_model=RunResp)
def batch_run(body: RunReq):
    # 이 코드가 뜻하는 바: 한 번에 파이프라인 실행(러프/최소).
    saved_dir, ref_used = dump_tarball(body.repo_url, body.ref)
    uids, vecs, metas = embed_directory(Path(saved_dir), body.repo_url, ref_used)
    inserted = upsert_chunks(uids, vecs, metas)
    return RunResp(
        repo_url=body.repo_url,
        ref_used=ref_used,
        saved_dir=str(saved_dir),
        chunk_count=len(uids),
        inserted=inserted,
    )
