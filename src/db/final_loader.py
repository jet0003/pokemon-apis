import sqlite3
from pathlib import Path
from typing import Any


DB_PATH = Path(__file__).resolve().parents[2] / "data" / "final_pokemon.sqlite3"


def get_connection(db_path: str | Path | None = None) -> sqlite3.Connection:
    """Create a SQLite connection and ensure the parent folder exists."""
    target_path = Path(db_path or DB_PATH)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(target_path)


def create_final_table(conn: sqlite3.Connection) -> None:
    """Create the final_pokemon table if it does not already exist."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS final_pokemon (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            height INTEGER NOT NULL,
            weight INTEGER NOT NULL
        )
        """
    )
    conn.commit()


def insert_final_pokemon(payload: dict[str, Any], db_path: str | Path | None = None) -> int:
    """Insert a validated, cleaned Pokémon payload into the final table."""
    if not isinstance(payload, dict):
        raise TypeError("payload must be a dictionary")

    required_fields = {"id", "name", "height", "weight"}
    if not required_fields.issubset(payload.keys()):
        raise ValueError("payload must contain id, name, height, and weight")

    with get_connection(db_path) as conn:
        create_final_table(conn)
        cursor = conn.execute(
            """
            INSERT INTO final_pokemon (id, name, height, weight)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                height = excluded.height,
                weight = excluded.weight
            """,
            (
                payload["id"],
                payload["name"].strip().upper(),
                payload["height"],
                payload["weight"],
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)
