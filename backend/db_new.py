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

        # Wichtig: Foreign Keys in SQLite aktivieren (pro Connection!)
        cur.execute("PRAGMA foreign_keys = ON;")

        # 1) Entity Tables 
        # 1.1) Create Reciipes
        cur.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
            """)

        # 1.2) Create Ingredients
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ingredients (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)

        # 1.3) Create Units
        cur.execute("""
            CREATE TABLE IF NOT EXISTS units (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                abbr TEXT NOT NULL UNIQUE
            )
        """)
        
        # 1.4) Create Tags
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)

        # 2) Junction Tables
        # 2.1) Create Recipe/Ingredient
        cur.execute("""
            CREATE TABLE IF NOT EXISTS recipe_ingredients (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id     INTEGER NOT NULL,
                ingredient_id INTEGER NOT NULL,
                quantity      REAL CHECK (quantity IS NULL OR quantity >= 0),
                unit_id       INTEGER,
                note          TEXT,
                position      INTEGER NOT NULL DEFAULT 1 CHECK (position > 0),
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
                FOREIGN KEY (ingredient_id) REFERENCES ingredients(id),
                FOREIGN KEY (unit_id) REFERENCES units(id)
            )
        """)

        # 2.2) Create Steps (for the recipe)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS steps (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id   INTEGER NOT NULL,
                step_no     INTEGER NOT NULL CHECK (step_no > 0),
                instruction TEXT NOT NULL,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
                UNIQUE (recipe_id, step_no)
            )
        """)

        # 2.3) Creates Recpie/Tags
        cur.execute("""
            CREATE TABLE IF NOT EXISTS recipe_tags (
                recipe_id INTEGER NOT NULL,
                tag_id    INTEGER NOT NULL,
                PRIMARY KEY (recipe_id, tag_id),
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        """)

        # 3) Sinnvolle Indizes (Performance) > ChatGPT
        #cur.execute("CREATE INDEX IF NOT EXISTS idx_ri_recipe ON recipe_ingredients(recipe_id);")
        #cur.execute("CREATE INDEX IF NOT EXISTS idx_ri_ingredient ON recipe_ingredients(ingredient_id);")
        #cur.execute("CREATE INDEX IF NOT EXISTS idx_steps_recipe ON steps(recipe_id);")
        #cur.execute("CREATE INDEX IF NOT EXISTS idx_rt_tag ON recipe_tags(tag_id);")

        # Send the statements
        con.commit()

        # Closing connection
        con.close()



    @classmethod
    def number_of_recipes(cls):
        con = cls.connect_to_db()
        cur = con.cursor()

        cur.execute("SELECT COUNT(*) FROM recipes")
        count = cur.fetchone()[0]

        cls.disconnect_from_db()
        return count

    @classmethod
    def add_recipe(cls, name, ingredients, steps, tags=None):
        """
        Adds a recipe with ingredients, steps, and optional tags.

        ingredients: list of dicts, e.g.
        [
          {"name": "Tomate", "quantity": 3, "unit": "Stk", "note": "gewürfelt"},
          {"name": "Olivenöl", "quantity": 2, "unit": "EL"},
          {"name": "Salz", "quantity": None, "unit": None, "note": "nach Geschmack"},
        ]

        steps: list[str]
        tags:  list[str] (optional)
        """


    @classmethod
    def delete_recipe(cls):
        pass

    @classmethod
    def show_recipe(cls, recipe_id):
        pass
