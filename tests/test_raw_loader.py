import sqlite3
from pathlib import Path

from src.db.raw_loader import insert_raw_pokemon


def test_insert_raw_pokemon_loads_data_into_sqlite(tmp_path):
    db_path = tmp_path / "raw_pokemon.sqlite3"
    payload = {"id": 25, "name": "pikachu", "height": 4, "weight": 60}

    inserted_id = insert_raw_pokemon(payload, db_path)

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT id, name, height, weight FROM raw_pokemon WHERE id = ?",
            (payload["id"],),
        ).fetchone()

    assert inserted_id == payload["id"]
    assert row == (25, "pikachu", 4, 60)
