# Pokémon API Project

## Overview
This project fetches Pokémon data from the PokeAPI, stores the raw response, validates it with lightweight data-quality checks, normalises the fields, and loads the cleaned result into SQLite tables.

## Requirements
- Python 3.10+
- Standard library only

## Installation
```bash
python -m pip install -r requirements.txt
```


## Project structure
- src/api/fetch_pokemon.py: API wrapper for the raw payload
- src/db/connection.py: SQLite connection and schema setup
- src/db/raw_loader.py: inserts raw payloads into raw_pokemon
- src/db/dq_checks.py: validates payloads before staging
- src/db/staging_loader.py: loads cleaned rows into staging_pokemon
- src/db/final_loader.py: loads final validated rows into final_pokemon
- src/logic/get_pokemon.py: main workflow
- src/utils/normalisation.py: cleans and standardises values
- src/utils/pretty_print.py: CLI display helper

## Pipeline explanation
1. Check the final table for a previously stored Pokémon.
2. If unavailable, check staging.
3. Otherwise, fetch from the API.
4. Store raw data in raw_pokemon.
5. Run DQ checks.
6. If passed, normalise and load into staging and final tables.

## Error handling
- Missing or invalid Pokémon names return a friendly CLI message.
- API failures are logged and surfaced to the CLI.
- DQ failures stop staging and raise a friendly error.

## DQ checks
- Missing fields
- Empty JSON
- Non-positive height/weight
- Unexpected data types
- Inconsistent casing
- Duplicate entries


