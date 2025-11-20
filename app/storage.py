from __future__ import annotations

import json
import secrets
import string
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data"
STORE_PATH = DATA_PATH / "store.json"


def _default_store() -> Dict[str, List[dict]]:
    return {"cards": [], "tokens": []}


def _ensure_store_file() -> None:
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    if not STORE_PATH.exists():
        save_store(_default_store())


def load_store() -> Dict[str, List[dict]]:
    _ensure_store_file()
    with STORE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_store(store: Dict[str, List[dict]]) -> None:
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    with STORE_PATH.open("w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)


def generate_card_key(prefix: str = "VIP", length: int = 16) -> str:
    alphabet = string.ascii_uppercase + string.digits
    random_part = "".join(secrets.choice(alphabet) for _ in range(length))
    return f"{prefix}-{random_part}"


def issue_cards(count: int, prefix: str = "VIP", valid_days: int | None = 30) -> List[str]:
    if count < 1:
        raise ValueError("count must be at least 1")

    store = load_store()
    issued_at = datetime.utcnow().isoformat()
    expires_at = (
        (datetime.utcnow() + timedelta(days=valid_days)).isoformat() if valid_days else None
    )

    new_cards: List[dict] = []
    for _ in range(count):
        key = generate_card_key(prefix=prefix)
        new_cards.append(
            {
                "key": key,
                "status": "unused",
                "issued_at": issued_at,
                "expires_at": expires_at,
                "token": None,
                "used_at": None,
                "note": None,
            }
        )

    store["cards"].extend(new_cards)
    save_store(store)
    return [c["key"] for c in new_cards]


def list_cards() -> List[dict]:
    store = load_store()
    return store.get("cards", [])


def validate_card(card_key: str) -> dict:
    store = load_store()
    card = next((c for c in store.get("cards", []) if c["key"] == card_key), None)

    if not card:
        return {"valid": False, "reason": "未找到对应的卡密"}

    if card.get("expires_at"):
        expires_at = datetime.fromisoformat(card["expires_at"])
        if expires_at < datetime.utcnow():
            return {"valid": False, "reason": "卡密已过期"}

    if card.get("status") == "used":
        return {"valid": False, "reason": "卡密已被使用"}

    return {"valid": True, "card": card}


def store_token(card_key: str, token_value: str) -> dict:
    store = load_store()
    card = next((c for c in store.get("cards", []) if c["key"] == card_key), None)
    if not card:
        raise ValueError("卡密不存在")

    if card.get("status") == "used":
        raise ValueError("卡密已被使用")

    now_iso = datetime.utcnow().isoformat()
    card["status"] = "used"
    card["token"] = token_value
    card["used_at"] = now_iso

    token_record = {
        "card_key": card_key,
        "token": token_value,
        "recorded_at": now_iso,
    }

    store_tokens = store.get("tokens", [])
    store_tokens.append(token_record)
    store["tokens"] = store_tokens

    save_store(store)
    return token_record
