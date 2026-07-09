from typing import Any


def run_dq_checks(payload: dict[str, Any] | None) -> tuple[dict[str, list[str]], bool]:
    """Validate a Pokémon payload and return DQ issues plus a pass/fail flag."""
    issues: dict[str, list[str]] = {"errors": []}

    if payload is None:
        issues["errors"].append("raw row: payload is empty")
        return issues, False

    if not isinstance(payload, dict):
        issues["errors"].append("raw row: payload must be a dictionary")
        return issues, False

    if not payload:
        issues["errors"].append("raw row: empty JSON")
        return issues, False

    required_fields = ["id", "name", "height", "weight"]
    for field in required_fields:
        if field not in payload:
            issues["errors"].append(f"raw row: missing field '{field}'")

    if "id" in payload:
        if not isinstance(payload["id"], int):
            issues["errors"].append("raw row: field 'id' must be an integer")

    if "name" in payload:
        if not isinstance(payload["name"], str):
            issues["errors"].append("raw row: field 'name' must be a string")
        elif not payload["name"].strip():
            issues["errors"].append("raw row: field 'name' cannot be empty")
        elif payload["name"] != payload["name"].strip():
            issues["errors"].append("raw row: field 'name' has leading or trailing whitespace")
        elif payload["name"] != payload["name"].lower() and payload["name"] != payload["name"].capitalize():
            issues["errors"].append("raw row: field 'name' has casing inconsistency")

    for field in ["height", "weight"]:
        if field in payload:
            value = payload[field]
            if not isinstance(value, int):
                issues["errors"].append(f"raw row: field '{field}' must be an integer")
            elif value <= 0:
                issues["errors"].append(f"raw row: field '{field}' must be greater than zero")

    return issues, not issues["errors"]
