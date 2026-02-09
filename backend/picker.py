import sqlite3

# Pfad zu deiner SQLite-Datenbank
DB_PATH = "..//meals.db"

# Tabellen- & Spaltenname
TABLE_NAME = "meine_tabelle"
ID_COLUMN = "id"

def get_random_entry():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # erlaubt Zugriff über Spaltennamen
    cursor = conn.cursor()

    query = f"""
        SELECT *
        FROM {TABLE_NAME}
        WHERE {ID_COLUMN} = (
            SELECT {ID_COLUMN}
            FROM {TABLE_NAME}
            ORDER BY RANDOM()
            LIMIT 1
        );
    """

    cursor.execute(query)
    row = cursor.fetchone()

    conn.close()
    return dict(row) if row else None


if __name__ == "__main__":
    entry = get_random_entry()

    if entry:
        print("🎲 Zufälliger Eintrag:")
        for key, value in entry.items():
            print(f"{key}: {value}")
    else:
        print("❌ Kein Eintrag gefunden")
