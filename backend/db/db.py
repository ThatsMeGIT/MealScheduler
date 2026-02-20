# db.py
# Kombiniert alle Funktionen der db_editor.py und db_watcher.py, um die Datenbank zu verwalten

from .db_builder import 
from .db_editor import 
from .db_watcher import 


def connect(db_path: str) -> sqlite3.Connection:

def disconnect(conn: sqlite3.Connection) -> None:

def build_db(db_path: str) -> None:

def edit_entry(db_path: str) -> None:

def delete_entry(db_path: str) -> None:

def create_entry(db_path: str) -> None: