from src.utils.normalisation import normalise_pokemon


def test_normalise_pokemon_standardises_values():
    payload = {"id": "25", "name": "  pikachu  ", "height": "4", "weight": 60.0}

    result = normalise_pokemon(payload)

    assert result == {"id": 25, "name": "PIKACHU", "height": 4, "weight": 60}


def test_normalise_pokemon_returns_none_for_empty_payload():
    assert normalise_pokemon({}) is None
