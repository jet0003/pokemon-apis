import json
from unittest.mock import Mock, patch

from src.api.fetch_pokemon import fetch_pokemon


def make_response(status_code=200, payload=None):
    response = Mock()
    response.status_code = status_code
    response.json.return_value = payload
    return response


def test_fetch_pokemon_returns_payload_and_prints_raw_json(capsys):
    payload = {"id": 25, "name": "pikachu", "height": 4, "weight": 60}

    with patch("src.api.fetch_pokemon.requests.get", return_value=make_response(payload=payload)):
        result = fetch_pokemon("pikachu")

    captured = capsys.readouterr()
    assert result == payload
    assert captured.out.strip() == json.dumps(payload, separators=(",", ":"), ensure_ascii=False)


def test_fetch_pokemon_handles_not_found(capsys):
    with patch("src.api.fetch_pokemon.requests.get", return_value=make_response(status_code=404)):
        result = fetch_pokemon("missingmon")

    captured = capsys.readouterr()
    assert result is None
    assert "Pokémon not found" in captured.out


def test_fetch_pokemon_handles_empty_json(capsys):
    with patch("src.api.fetch_pokemon.requests.get", return_value=make_response(payload={})):
        result = fetch_pokemon("pikachu")

    captured = capsys.readouterr()
    assert result is None
    assert "empty JSON" in captured.out

def test_fetch_pokemon_handles_non_200(capsys):
    with patch("src.api.fetch_pokemon.requests.get", return_value=make_response(status_code=500)):
        result = fetch_pokemon("pikachu")

    captured = capsys.readouterr()
    assert result is None
    assert "status 500" in captured.out
