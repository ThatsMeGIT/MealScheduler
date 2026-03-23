from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterator

from backend.app.domain.models import DAY_KEYS, MEAL_KEYS, Ingredient, Recipe, WeeklyPlan


class MealRepository:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            yield conn
            conn.commit()
        finally:
            conn.close()

    def initialize(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    servings INTEGER NOT NULL DEFAULT 2,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS recipe_ingredients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recipe_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    quantity REAL,
                    unit TEXT DEFAULT '',
                    category TEXT DEFAULT '',
                    note TEXT DEFAULT '',
                    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS recipe_tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recipe_id INTEGER NOT NULL,
                    tag TEXT NOT NULL,
                    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS weekly_plans (
                    week_start TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    sent_at TEXT
                );
                """
            )
            for key, value in self.default_settings().items():
                conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))

    def get_settings(self) -> dict[str, str]:
        with self._connect() as conn:
            rows = conn.execute("SELECT key, value FROM settings").fetchall()
        settings = {row["key"]: row["value"] for row in rows}
        for key, value in self.default_settings().items():
            settings.setdefault(key, value)
        return settings

    def save_settings(self, settings: dict[str, str]) -> None:
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                list(settings.items()),
            )

    def create_recipe(self, name: str, description: str, servings: int, ingredients: list[dict], tags: list[str]) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO recipes (name, description, servings, created_at) VALUES (?, ?, ?, ?)",
                (name, description, servings, datetime.now().isoformat(timespec="seconds")),
            )
            recipe_id = int(cursor.lastrowid)
            conn.executemany(
                "INSERT INTO recipe_ingredients (recipe_id, name, quantity, unit, category, note) VALUES (?, ?, ?, ?, ?, ?)",
                [
                    (recipe_id, item["name"], item.get("quantity"), item.get("unit", ""), item.get("category", ""), item.get("note", ""))
                    for item in ingredients
                    if item["name"].strip()
                ],
            )
            conn.executemany("INSERT INTO recipe_tags (recipe_id, tag) VALUES (?, ?)", [(recipe_id, tag) for tag in tags])
        return recipe_id

    def list_recipes(self) -> list[Recipe]:
        with self._connect() as conn:
            recipes = conn.execute("SELECT id, name, description, servings, created_at FROM recipes ORDER BY name COLLATE NOCASE").fetchall()
            ingredients = conn.execute("SELECT recipe_id, name, quantity, unit, category, note FROM recipe_ingredients ORDER BY recipe_id, id").fetchall()
            tags = conn.execute("SELECT recipe_id, tag FROM recipe_tags ORDER BY tag COLLATE NOCASE").fetchall()
        ingredient_map: dict[int, list[Ingredient]] = {}
        for row in ingredients:
            ingredient_map.setdefault(row["recipe_id"], []).append(
                Ingredient(name=row["name"], quantity=row["quantity"], unit=row["unit"], category=row["category"], note=row["note"])
            )
        tag_map: dict[int, list[str]] = {}
        for row in tags:
            tag_map.setdefault(row["recipe_id"], []).append(row["tag"])
        return [
            Recipe(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                servings=row["servings"],
                created_at=row["created_at"],
                ingredients=ingredient_map.get(row["id"], []),
                tags=tag_map.get(row["id"], []),
            )
            for row in recipes
        ]

    def delete_recipe(self, recipe_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))

    def save_weekly_plan(self, plan: WeeklyPlan) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO weekly_plans (week_start, payload, sent_at)
                VALUES (?, ?, NULL)
                ON CONFLICT(week_start) DO UPDATE SET payload = excluded.payload, sent_at = NULL
                """,
                (plan.week_start, json.dumps(plan.to_dict(), ensure_ascii=False)),
            )

    def get_weekly_plan(self, week_start: str) -> WeeklyPlan | None:
        with self._connect() as conn:
            row = conn.execute("SELECT payload FROM weekly_plans WHERE week_start = ?", (week_start,)).fetchone()
        return WeeklyPlan.from_dict(json.loads(row["payload"])) if row else None

    def mark_current_week_sent(self) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE weekly_plans SET sent_at = ? WHERE week_start = ?",
                (datetime.now().isoformat(timespec="seconds"), self._current_week_start()),
            )

    def current_week_was_sent(self) -> bool:
        with self._connect() as conn:
            row = conn.execute("SELECT sent_at FROM weekly_plans WHERE week_start = ?", (self._current_week_start(),)).fetchone()
        return bool(row and row["sent_at"])

    @staticmethod
    def _current_week_start() -> str:
        today = datetime.now().date()
        return (today - timedelta(days=today.weekday())).isoformat()

    @staticmethod
    def default_settings() -> dict[str, str]:
        defaults = {
            "smtp_host": "",
            "smtp_port": "465",
            "smtp_username": "",
            "smtp_password": "",
            "mail_from": "",
            "mail_to": "",
            "mail_subject": "Dein Wochenplan",
            "schedule_day": "6",
            "schedule_time": "09:00",
            "use_ssl": "1",
        }
        for day_key, _ in DAY_KEYS:
            for meal_key, _ in MEAL_KEYS:
                defaults[f"slot_{day_key}_{meal_key}"] = "1" if meal_key == "dinner" else "0"
        return defaults
