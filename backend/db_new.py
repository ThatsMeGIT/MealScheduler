import sqlite3

class Database:
    DB = "meals.db"
    connection = None

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
    def build_db(cls):
        con = cls.connect_to_db()
        cur = con.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS recipe_ingredients (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id  INTEGER NOT NULL,
                ingredient TEXT NOT NULL,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id)
            )
        """)

        con.commit()
        cls.disconnect_from_db()

    @classmethod
    def number_of_recipes(cls):
        con = cls.connect_to_db()
        cur = con.cursor()

        cur.execute("SELECT COUNT(*) FROM recipes")
        count = cur.fetchone()[0]

        cls.disconnect_from_db()
        return count

    @classmethod
    def add_recipe(cls):
        pass

    @classmethod
    def delete_recipe(cls):
        pass

    @classmethod
    def show_recipe(cls, recipe_id):
        pass
