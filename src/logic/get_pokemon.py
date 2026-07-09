import sqlite3
from pathlib import Path
from typing import Any, Callable

from src.api.fetch_pokemon import fetch_pokemon
from src.db.dq_checks import run_dq_checks
from src.db.final_loader import insert_final_pokemon
from src.db.raw_loader import insert_raw_pokemon
from src.db.staging_loader import insert_staging_pokemon
from src.utils.normalisation import normalise_pokemon


RAW_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "raw_pokemon.sqlite3"
STAGING_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "staging_pokemon.sqlite3"
FINAL_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "final_pokemon.sqlite3"


def _connect(db_path: str | Path) -> sqlite3.Connection:
    return sqlite3.connect(db_path)


def _read_row_from_table(table_name: str, pokemon_id: int | None, db_path: str | Path) -> dict[str, Any] | None:
    if pokemon_id is None:
        return None

    with _connect(db_path) as conn:
        row = conn.execute(
            f"SELECT id, name, height, weight FROM {table_name} WHERE id = ?",
            (pokemon_id,),
        ).fetchone()

    if row is None:
        return None

    return {"id": row[0], "name": row[1], "height": row[2], "weight": row[3]}


def get_pokemon(
    name: str,
    raw_db_path: str | Path | None = None,
    staging_db_path: str | Path | None = None,
    final_db_path: str | Path | None = None,
    fetch_fn: Callable[[str], dict[str, Any] | None] | None = None,
) -> dict[str, Any] | None:
    """Retrieve a Pokémon by checking the final table, then staging, then the API."""
    if not isinstance(name, str) or not name.strip():
        return None

    raw_db = Path(raw_db_path or RAW_DB_PATH)
    staging_db = Path(staging_db_path or STAGING_DB_PATH)
    final_db = Path(final_db_path or FINAL_DB_PATH)
    fetcher = fetch_fn or fetch_pokemon

    normalised_name = name.strip().lower()
    payload_from_api = fetcher(normalised_name)
    if payload_from_api is None:
        return None

    payload_id = payload_from_api.get("id")
    if payload_id is None:
        return None

    final_row = _read_row_from_table("final_pokemon", payload_id, final_db)
    if final_row is not None:
        return final_row

    staging_row = _read_row_from_table("staging_pokemon", payload_id, staging_db)
    if staging_row is not None:
        insert_final_pokemon(staging_row, final_db)
        return _read_row_from_table("final_pokemon", payload_id, final_db)

    insert_raw_pokemon(payload_from_api, raw_db)
    persisted_payload = {
        "id": payload_from_api.get("id"),
        "name": payload_from_api.get("name"),
        "height": payload_from_api.get("height"),
        "weight": payload_from_api.get("weight"),
    }

    issues, passed = run_dq_checks(persisted_payload)
    if not passed:
        return None

    normalised_payload = normalise_pokemon(persisted_payload)
    if normalised_payload is None:
        return None

    insert_staging_pokemon(normalised_payload, staging_db)
    insert_final_pokemon(normalised_payload, final_db)

    return _read_row_from_table("final_pokemon", payload_id, final_db)
