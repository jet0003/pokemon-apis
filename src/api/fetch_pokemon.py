import json
import requests


def fetch_pokemon(name: str = "clefairy") -> dict | None:
    """Fetch a Pokémon payload from the PokeAPI and print the raw JSON data."""
    if not isinstance(name, str) or not name.strip():
        print("A Pokémon name is required")
        return None

    url = f"https://pokeapi.co/api/v2/pokemon/{name.strip().lower()}"

    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException as exc:
        print(f"API request failed: {exc}")
        return None

    if response.status_code == 404:
        print("Pokémon not found")
        return None

    if response.status_code != 200:
        print(f"API request failed with status {response.status_code}")
        return None

    try:
        payload = response.json()
    except ValueError:
        print("Received invalid JSON")
        return None

    if not payload:
        print("Received empty JSON")
        return None

    print(json.dumps(payload, separators=(",", ":"), ensure_ascii=False))
    return payload