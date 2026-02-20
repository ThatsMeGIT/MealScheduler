# db_builder.py
# Erstellt die SQLite-DB-Struktur wie im Screenshot.

from __future__ import annotations

import sqlite3
from abc import ABC, abstractmethod
from typing import Iterable, Optional


def connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


class TableCreator(ABC):
    table_name: str

    @abstractmethod
    def create(self, conn: sqlite3.Connection) -> None:
        ...

    @abstractmethod
    def drop(self, conn: sqlite3.Connection) -> None:
        ...


class RecipesCreator(TableCreator):
    table_name = "recipes"

    def create(self, conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS recipes (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            );
            """
        )

    def drop(self, conn: sqlite3.Connection) -> None:
        conn.execute("DROP TABLE IF EXISTS recipes;")


class IngredientsCreator(TableCreator):
    table_name = "ingredients"

    def create(self, conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ingredients (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
            """
        )

    def drop(self, conn: sqlite3.Connection) -> None:
        conn.execute("DROP TABLE IF EXISTS ingredients;")


class TagsCreator(TableCreator):
    table_name = "tags"

    def create(self, conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tags (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
            """
        )

    def drop(self, conn: sqlite3.Connection) -> None:
        conn.execute("DROP TABLE IF EXISTS tags;")


class UnitsCreator(TableCreator):
    table_name = "units"

    def create(self, conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS units (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                abbr TEXT NOT NULL UNIQUE
            );
            """
        )

    def drop(self, conn: sqlite3.Connection) -> None:
        conn.execute("DROP TABLE IF EXISTS units;")


class StepsCreator(TableCreator):
    table_name = "steps"

    def create(self, conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS steps (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id   INTEGER NOT NULL,
                step_no     INTEGER NOT NULL CHECK(step_no > 0),
                instruction TEXT NOT NULL,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
            );
            """
        )

    def drop(self, conn: sqlite3.Connection) -> None:
        conn.execute("DROP TABLE IF EXISTS steps;")


class RecipeIngredientsCreator(TableCreator):
    table_name = "recipe_ingredients"

    def create(self, conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS recipe_ingredients (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id     INTEGER NOT NULL,
                ingredient_id INTEGER NOT NULL,
                quantity      REAL CHECK(quantity IS NULL OR quantity >= 0),
                unit_id       INTEGER,
                note          TEXT,
                position      INTEGER NOT NULL DEFAULT 1 CHECK(position > 0),

                FOREIGN KEY (recipe_id)     REFERENCES recipes(id)     ON DELETE CASCADE,
                FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE RESTRICT,
                FOREIGN KEY (unit_id)       REFERENCES units(id)       ON DELETE SET NULL
            );
            """
        )

    def drop(self, conn: sqlite3.Connection) -> None:
        conn.execute("DROP TABLE IF EXISTS recipe_ingredients;")


class RecipeTagsCreator(TableCreator):
    table_name = "recipe_tags"

    def create(self, conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS recipe_tags (
                recipe_id INTEGER NOT NULL,
                tag_id    INTEGER NOT NULL,
                PRIMARY KEY (recipe_id, tag_id),
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id)    REFERENCES tags(id)    ON DELETE CASCADE
            );
            """
        )

    def drop(self, conn: sqlite3.Connection) -> None:
        conn.execute("DROP TABLE IF EXISTS recipe_tags;")


class DbBuilder:
    """
    Erstellt/entfernt das Schema. Reihenfolge ist wichtig wegen FK-Abhängigkeiten.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.creators: list[TableCreator] = [
            RecipesCreator(),
            IngredientsCreator(),
            TagsCreator(),
            UnitsCreator(),
            StepsCreator(),
            RecipeIngredientsCreator(),
            RecipeTagsCreator(),
        ]

    def create_all(self) -> None:
        with connect(self.db_path) as conn:
            # Eltern zuerst, dann abhängige Tabellen
            for c in self.creators:
                c.create(conn)

    def drop_all(self) -> None:
        with connect(self.db_path) as conn:
            # Abhängige zuerst löschen, dann Eltern
            for c in reversed(self.creators):
                c.drop(conn)


if __name__ == "__main__":
    # Beispiel:
    # python db_builder.py
    builder = DbBuilder("recipes.db")
    builder.create_all()
    print("DB-Schema erstellt:", builder.db_path)