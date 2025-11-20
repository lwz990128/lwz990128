from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import storage

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="卡密核验与Token收录")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class ValidateRequest(BaseModel):
    cardKey: str = Field(..., min_length=5, description="用户输入的卡密")


class TokenRequest(BaseModel):
    cardKey: str = Field(..., min_length=5)
    token: str = Field(..., min_length=10, description="用户提交的token")


class IssueRequest(BaseModel):
    count: int = Field(1, ge=1, le=100)
    prefix: str = Field("VIP", min_length=1, max_length=10)
    valid_days: Optional[int] = Field(30, ge=1, le=365)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/validate")
def validate_card(payload: ValidateRequest = Body(...)) -> dict:
    result = storage.validate_card(payload.cardKey.strip())
    if not result.get("valid"):
        return {"valid": False, "message": result.get("reason", "未知原因")}
    return {"valid": True, "card": result["card"]}


@app.post("/api/tokens")
def submit_token(payload: TokenRequest = Body(...)) -> dict:
    try:
        token_record = storage.store_token(payload.cardKey.strip(), payload.token.strip())
    except ValueError as exc:  # pragma: no cover - simple validation path
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"message": "Token 已收录", "record": token_record}


@app.post("/api/cards")
def issue_new_cards(payload: IssueRequest = Body(...)) -> dict:
    try:
        keys = storage.issue_cards(payload.count, prefix=payload.prefix, valid_days=payload.valid_days)
    except ValueError as exc:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"keys": keys}


@app.get("/api/cards")
def list_all_cards() -> dict:
    return {"cards": storage.list_cards()}


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}
