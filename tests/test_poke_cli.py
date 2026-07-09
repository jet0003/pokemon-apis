from poke import build_parser, normalise_pokemon_name


def test_build_parser_accepts_pokemon_name_argument():
    parser = build_parser()
    args = parser.parse_args(["pikachu"])

    assert args.pokemon_name == "pikachu"


def test_normalise_pokemon_name_lowercases_and_strips_whitespace():
    assert normalise_pokemon_name("  Pikachu  ") == "pikachu"


def test_normalise_pokemon_name_returns_none_for_empty_input():
    assert normalise_pokemon_name("   ") is None
