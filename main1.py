# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel, Field

# import uuid
# import datetime
# import re


# app = FastAPI(
#     title="Batch API (step1: code-only)"
# )

# #--------------------------------------------------------------------------------#
# #헬스체크 함수
# #--------------------------------------------------------------------------------#

# @app.get("/health")
# def health():
#     now_utc_iso = datetime.datetime.utcnow().isoformat() + "Z"

#     return {
#         "OK": True,
#         "ts": now_utc_iso
#     }

# class RunStartRequest(BaseModel):
#     #레포지토리 원본 주소
#     #description: 문서화 용 설명
#     repo_url: str = Field(..., description="레포지토리 URL (UNIQUE)")
#     #커밋에서 너무 짧거나 너무 긴 입력 방지한다
#     commit: str = Field(
#         ...,
#         min_length=2
#         max_length=64
#         description="커밋, 해시 또는 브랜치명"
#     )

#     scope: str = Field(
#         ...,
#         pattern=r""
#         description="범위"
#     )
