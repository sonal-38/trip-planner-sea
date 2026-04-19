from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ITINERARY_DIR = DATA_DIR / "itineraries"


def ensure_storage() -> None:
    ITINERARY_DIR.mkdir(parents=True, exist_ok=True)


def slugify(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in value.strip())
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-") or "trip"


def save_itinerary(payload: dict[str, Any]) -> Path:
    ensure_storage()
    destination = payload.get("destination", "trip")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    file_path = ITINERARY_DIR / f"{slugify(str(destination))}-{timestamp}.json"
    file_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return file_path


def list_itineraries() -> list[Path]:
    ensure_storage()
    return sorted(ITINERARY_DIR.glob("*.json"), reverse=True)
