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
        if not name or not str(name).strip():
            raise ValueError("Recipe name must not be empty.")
        if not ingredients or len(ingredients) == 0:
            raise ValueError("ingredients must not be empty.")
        if not steps or len(steps) == 0:
            raise ValueError("steps must not be empty.")

        con = cls.connect_to_db()
        cur = con.cursor()

        # Important: enable FK per connection
        cur.execute("PRAGMA foreign_keys = ON;")

        try:
            # Start transaction
            cur.execute("BEGIN;")

            # 1) Insert recipe
            cur.execute("INSERT INTO recipes (name) VALUES (?);", (name.strip(),))
            recipe_id = cur.lastrowid

            # helper: get unit_id by abbr
            def unit_id_from_abbr(unit_abbr):
                if unit_abbr is None:
                    return None
                unit_abbr = str(unit_abbr).strip()
                if unit_abbr == "":
                    return None

                row = cur.execute(
                    "SELECT id FROM units WHERE lower(abbr) = lower(?);",
                    (unit_abbr,),
                ).fetchone()

                if row is None:
                    # Option A (strict): error, so you keep your units clean
                    raise ValueError(f"Unit '{unit_abbr}' not found in units table.")
                    # Option B (auto-create): uncomment if you want:
                    # cur.execute("INSERT INTO units (name, abbr) VALUES (?, ?);", (unit_abbr, unit_abbr))
                    # return cur.lastrowid

                return row[0]

            # 2) Ingredients + recipe_ingredients
            for pos, ing in enumerate(ingredients, start=1):
                ing_name = (ing.get("name") if isinstance(ing, dict) else None)
                if not ing_name or not str(ing_name).strip():
                    raise ValueError("Each ingredient must have a non-empty 'name'.")

                ing_name = str(ing_name).strip()
                quantity = ing.get("quantity") if isinstance(ing, dict) else None
                unit_abbr = ing.get("unit") if isinstance(ing, dict) else None
                note = ing.get("note") if isinstance(ing, dict) else None

                # ensure ingredient exists
                cur.execute("INSERT OR IGNORE INTO ingredients (name) VALUES (?);", (ing_name,))
                row = cur.execute(
                    "SELECT id FROM ingredients WHERE lower(name) = lower(?);",
                    (ing_name,),
                ).fetchone()
                ingredient_id = row[0]

                unit_id = unit_id_from_abbr(unit_abbr)

                cur.execute(
                    """
                    INSERT INTO recipe_ingredients
                      (recipe_id, ingredient_id, quantity, unit_id, note, position)
                    VALUES (?, ?, ?, ?, ?, ?);
                    """,
                    (recipe_id, ingredient_id, quantity, unit_id, note, pos),
                )

            # 3) Steps
            for i, s in enumerate(steps, start=1):
                instruction = (s if s is not None else "")
                instruction = str(instruction).strip()
                if instruction == "":
                    raise ValueError("Steps must not contain empty strings.")

                cur.execute(
                    "INSERT INTO steps (recipe_id, step_no, instruction) VALUES (?, ?, ?);",
                    (recipe_id, i, instruction),
                )

            # 4) Tags (optional)
            if tags:
                for t in tags:
                    tag_name = (t if t is not None else "")
                    tag_name = str(tag_name).strip()
                    if tag_name == "":
                        continue

                    cur.execute("INSERT OR IGNORE INTO tags (name) VALUES (?);", (tag_name,))
                    tag_row = cur.execute(
                        "SELECT id FROM tags WHERE lower(name) = lower(?);",
                        (tag_name,),
                    ).fetchone()
                    tag_id = tag_row[0]

                    cur.execute(
                        "INSERT OR IGNORE INTO recipe_tags (recipe_id, tag_id) VALUES (?, ?);",
                        (recipe_id, tag_id),
                    )

            con.commit()
            return recipe_id

        except Exception:
            con.rollback()
            raise

        finally:
            cls.disconnect_from_db()


    @classmethod
    def delete_recipe(cls):
        pass

    @classmethod
    def show_recipe(cls, recipe_id):
        pass
