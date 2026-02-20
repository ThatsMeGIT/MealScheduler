from abc import ABC, abstractmethod

class TableCreator(ABC):
    @abstractmethod
    def create(self, cur): ...
    @abstractmethod
    def drop(self, cur): ...

class RecipesCreator(TableCreator):
    def create(self, cur):
        cur.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)
    def drop(self, cur):
        cur.execute("DROP TABLE IF EXISTS recipes;")

class IngredientsCreator(TableCreator):
    def create(self, cur):
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
    def drop(self, cur):
        cur.execute("DROP TABLE IF EXISTS ingredients;")

# ... UnitsCreator, TagsCreator, RecipeIngredientsCreator, StepsCreator, RecipeTagsCreator analog ...