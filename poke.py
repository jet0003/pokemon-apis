import argparse
import sqlite3
import sys
from pathlib import Path

from src.api.fetch_pokemon import fetch_pokemon
from src.db.dq_checks import run_dq_checks
from src.db.raw_loader import insert_raw_pokemon
from src.db.staging_loader import insert_staging_pokemon
from src.utils.normalisation import normalise_pokemon


DB_PATH = Path(__file__).resolve().parent / "data" / "raw_pokemon.sqlite3"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch, validate, and stage Pokémon data")
    parser.add_argument("pokemon_name", nargs="?", help="Name of the Pokémon to look up")
    return parser


def normalise_pokemon_name(name: str | None) -> str | None:
    if not isinstance(name, str):
        return None

    cleaned_name = name.strip().lower()
    if not cleaned_name:
        return None
    return cleaned_name


def print_raw_table_preview(conn: sqlite3.Connection, limit: int = 5) -> None:
    """Print the first few rows from the raw_pokemon table."""
    rows = conn.execute(
        "SELECT id, name, height, weight FROM raw_pokemon ORDER BY id ASC LIMIT ?",
        (limit,),
    ).fetchall()

    print("\nRaw table preview")
    print("-" * 24)
    if not rows:
        print("No raw Pokémon data yet.")
        return

    for row in rows:
        print(f"id={row[0]} | name={row[1]} | height={row[2]} | weight={row[3]}")


def read_raw_row_from_db(conn: sqlite3.Connection, payload: dict) -> dict | None:
    """Read the persisted raw row back from the database for DQ validation."""
    row = conn.execute(
        "SELECT id, name, height, weight FROM raw_pokemon WHERE id = ?",
        (payload.get("id"),),
    ).fetchone()

    if row is None:
        return None

    return {
        "id": row[0],
        "name": row[1],
        "height": row[2],
        "weight": row[3],
    }


def main() -> None:
    """Fetch Pokémon data, load it into SQLite, run DQ checks, and print a preview."""
    parser = build_parser()
    args = parser.parse_args()

    while True:
        pokemon_name = normalise_pokemon_name(args.pokemon_name)
        if pokemon_name is None:
            pokemon_name = input("Enter a Pokémon name: ")
            pokemon_name = normalise_pokemon_name(pokemon_name)
            if pokemon_name is None:
                print("Please enter a valid Pokémon name.")
                continue

        payload = fetch_pokemon(pokemon_name)
        if payload is None:
            print("No data found for that Pokémon. Please enter a different name.")
            args.pokemon_name = input("Enter a Pokémon name: ")
            continue

        break

    insert_raw_pokemon(payload, DB_PATH)

    with sqlite3.connect(DB_PATH) as conn:
        persisted_payload = read_raw_row_from_db(conn, payload)
        if persisted_payload is None:
            print("Unable to read the inserted raw row from the database.")
            raise SystemExit(1)

        issues, passed = run_dq_checks(persisted_payload)
        if not passed:
            print("DQ check failed. Fix the raw row before staging:")
            for issue in issues.get("errors", []):
                print(f"- {issue}")
            print("Once corrected, run the pipeline again to re-check the data.")
            raise SystemExit(1)

        normalised_payload = normalise_pokemon(persisted_payload)
        if normalised_payload is None:
            print("Unable to normalise the payload.")
            raise SystemExit(1)

        staging_db_path = Path(__file__).resolve().parent / "data" / "staging_pokemon.sqlite3"
        insert_staging_pokemon(normalised_payload, staging_db_path)

        print("Normalised payload:")
        print(normalised_payload)

        staging_conn = sqlite3.connect(staging_db_path)
        try:
            rows = staging_conn.execute(
                "SELECT id, name, height, weight FROM staging_pokemon ORDER BY id ASC"
            ).fetchall()

            print("\nStaging table preview")
            print("-" * 24)
            if not rows:
                print("No staged Pokémon data yet.")
            else:
                for row in rows:
                    print(f"id={row[0]} | name={row[1]} | height={row[2]} | weight={row[3]}")
        finally:
            staging_conn.close()


if __name__ == "__main__":
    main()
