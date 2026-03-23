from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AppConfig:
    host: str
    port: int
    database_path: Path

    @classmethod
    def from_env(cls) -> "AppConfig":
        backend_dir = Path(__file__).resolve().parents[2]
        data_dir = backend_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        return cls(
            host=os.getenv("MEALSCHEDULER_HOST", "127.0.0.1"),
            port=int(os.getenv("MEALSCHEDULER_PORT", "8080")),
            database_path=Path(os.getenv("MEALSCHEDULER_DB", data_dir / "mealscheduler.db")),
        )
