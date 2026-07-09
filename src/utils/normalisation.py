from typing import Any


def normalise_pokemon(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    """Return a cleaned Pokémon payload with consistent types and structure."""
    if not isinstance(payload, dict) or not payload:
        return None

    name = payload.get("name")
    if isinstance(name, str):
        name = name.strip().upper()
    else:
        name = None

    height = payload.get("height")
    if isinstance(height, bool):
        height = int(height)
    elif isinstance(height, (int, float)):
        height = int(height)
    else:
        height = None

    weight = payload.get("weight")
    if isinstance(weight, bool):
        weight = int(weight)
    elif isinstance(weight, (int, float)):
        weight = int(weight)
    else:
        weight = None

    return {
        "id": int(payload.get("id")) if isinstance(payload.get("id"), (int, float)) and not isinstance(payload.get("id"), bool) else None,
        "name": name,
        "height": height,
        "weight": weight,
    }
