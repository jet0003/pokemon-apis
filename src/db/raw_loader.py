import sqlite3
from pathlib import Path
from typing import Any


DB_PATH = Path(__file__).resolve().parents[2] / "data" / "raw_pokemon.sqlite3"


def get_connection(db_path: str | Path | None = None) -> sqlite3.Connection:
    """Create a SQLite connection and ensure the parent folder exists."""
    target_path = Path(db_path or DB_PATH)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(target_path)


def create_raw_pokemon_table(conn: sqlite3.Connection) -> None:
    """Create the raw_pokemon table if it does not already exist."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS raw_pokemon (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            height INTEGER,
            weight INTEGER
        )
        """
    )
    conn.commit()


def insert_raw_pokemon(payload: dict[str, Any], db_path: str | Path | None = None) -> int:
    """Insert a raw Pokémon payload into the raw_pokemon table."""
    if not isinstance(payload, dict):
        raise TypeError("payload must be a dictionary")

    with get_connection(db_path) as conn:
        create_raw_pokemon_table(conn)
        cursor = conn.execute(
            """
            INSERT INTO raw_pokemon (id, name, height, weight)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                height = excluded.height,
                weight = excluded.weight
            """,
            (
                payload.get("id"),
                payload.get("name"),
                payload.get("height"),
                payload.get("weight"),
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)
