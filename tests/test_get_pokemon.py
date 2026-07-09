import sqlite3

from src.db.final_loader import insert_final_pokemon
from src.db.staging_loader import insert_staging_pokemon
from src.logic.get_pokemon import get_pokemon


def test_get_pokemon_returns_final_record_without_api_call(tmp_path):
    final_db = tmp_path / "final.sqlite3"
    staging_db = tmp_path / "staging.sqlite3"
    raw_db = tmp_path / "raw.sqlite3"

    insert_final_pokemon({"id": 25, "name": "pikachu", "height": 4, "weight": 60}, final_db)

    def fail_fetch(_name):
        raise AssertionError("API should not be called")

    result = get_pokemon(
        "pikachu",
        raw_db_path=raw_db,
        staging_db_path=staging_db,
        final_db_path=final_db,
        fetch_fn=fail_fetch,
    )

    assert result == {"id": 25, "name": "PIKACHU", "height": 4, "weight": 60}


def test_get_pokemon_promotes_staging_row_to_final(tmp_path):
    final_db = tmp_path / "final.sqlite3"
    staging_db = tmp_path / "staging.sqlite3"
    raw_db = tmp_path / "raw.sqlite3"

    insert_staging_pokemon({"id": 25, "name": "pikachu", "height": 4, "weight": 60}, staging_db)

    def fake_fetch(_name):
        return {"id": 25, "name": "pikachu", "height": 4, "weight": 60}

    result = get_pokemon(
        "pikachu",
        raw_db_path=raw_db,
        staging_db_path=staging_db,
        final_db_path=final_db,
        fetch_fn=fake_fetch,
    )

    assert result == {"id": 25, "name": "PIKACHU", "height": 4, "weight": 60}

    with sqlite3.connect(final_db) as conn:
        rows = conn.execute("SELECT id, name, height, weight FROM final_pokemon").fetchall()

    assert rows == [(25, "PIKACHU", 4, 60)]
