import sqlite3

DB = "meals.db"

def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()

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

    con.commit()
    con.close()

def add_recipe(name, ingredients):
    con = sqlite3.connect(DB)
    cur = con.cursor()

    # 1) Rezept einfügen
    cur.execute("INSERT INTO recipes (name) VALUES (?)", (name,))
    recipe_id = cur.lastrowid  # ID des gerade eingefügten Rezepts

    # 2) Zutaten einfügen (jede Zutat ist eine Zeile)
    for ing in ingredients:
        cur.execute(
            "INSERT INTO recipe_ingredients (recipe_id, ingredient) VALUES (?, ?)",
            (recipe_id, ing)
        )

    con.commit()
    con.close()

def show_recipe(recipe_id):
    con = sqlite3.connect(DB)
    cur = con.cursor()

    # Rezeptname holen
    cur.execute("SELECT name FROM recipes WHERE id = ?", (recipe_id,))
    row = cur.fetchone()
    if row is None:
        print("Rezept nicht gefunden.")
        con.close()
        return

    name = row[0]

    # Zutaten holen
    cur.execute("SELECT ingredient FROM recipe_ingredients WHERE recipe_id = ?", (recipe_id,))
    ingredients = [r[0] for r in cur.fetchall()]

    con.close()

    print(f"Rezept: {name}")
    print("Zutaten:")
    for ing in ingredients:
        print(f" - {ing}")

if __name__ == "__main__":
    init_db()

    add_recipe(
        "Pasta mit Tomatensoße",
        ["Nudeln", "Passierte Tomaten", "Zwiebel", "Knoblauch", "Salz"]
    )

    # Zeig das erste Rezept (id = 1), weil wir gerade eins eingefügt haben
    show_recipe(1)
