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
    def add_recipe(cls, name: str, ingredients: list[str]) -> int:
        """
        Fügt ein Rezept + Zutaten hinzu und gibt die neue recipe_id zurück.
        SQL-Injection-sicher durch Parameterbindung.
        """
        # Basic Validierung
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name darf nicht leer sein")

        if ingredients is None:
            ingredients = []
        if not isinstance(ingredients, list):
            raise ValueError("ingredients muss eine Liste sein")

        # Zutaten säubern: Strings trimmen, leere entfernen, Duplikate entfernen (Reihenfolge behalten)
        cleaned = []
        seen = set()
        for ing in ingredients:
            if ing is None:
                continue
            ing = str(ing).strip()
            if not ing:
                continue
            if ing.lower() in seen:
                continue
            seen.add(ing.lower())
            cleaned.append(ing)

        con = cls.connect_to_db()
        try:
            cur = con.cursor()

            # Transaktion: mit "with con:" committet sqlite automatisch, oder rollt bei Exception zurück
            with con:
                # 1) Rezept einfügen (Injection-sicher)
                cur.execute(
                    "INSERT INTO recipes (name) VALUES (?)",
                    (name.strip(),)
                )
                recipe_id = cur.lastrowid

                # 2) Zutaten einfügen (Injection-sicher)
                if cleaned:
                    cur.executemany(
                        "INSERT INTO recipe_ingredients (recipe_id, ingredient) VALUES (?, ?)",
                        [(recipe_id, ing) for ing in cleaned]
                    )
                return recipe_id

        finally:
            cls.disconnect_from_db()


    @classmethod
    def delete_recipe(cls):
        pass

    @classmethod
    def show_recipe(cls, recipe_id):
        pass
