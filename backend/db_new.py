import sqlite3

class Database:
    DB = "meals.db"
    connection = None

    @classmethod
    def build_db(cls):
        execute = cls.connect_to_db(cls).cursor
        
        # Tabelle 1: Rezepte
        cur.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)

        # Tabelle 2: Zutaten zu Rezepten (1 Rezept -> viele Zutaten)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS recipe_ingredients (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                ingredient TEXT NOT NULL,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id)
            )
        """)
        
        cls.disconnect_from_db
        
        

    @classmethod
    def connect_to_db(cls):
        cls.connection = sqlite3.connect(cls.DB)
        return cls.connection

    @classmethod
    def disconnect_from_db(cls):
        if cls.connection is not None:
            cls.connection.close()
            cls.connection = None
            
    @classmethod
    def add_recipe():
        
        
    @classmethod
    def delete_recipe():
        
