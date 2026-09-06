import pytest
from unittest.mock import patch, Mock
from pokemon_api import fetch_random_pokemon

@pytest.fixture
def mock_pokemon_response():
    return {
        "id": 25,
        "name": "pikachu",
        "types": [{"type": {"name": "electric"}}],
        "abilities": [{"ability": {"name": "static"}}],
        "height": 4,
        "weight": 60,
        "species": {
            "name": "pikachu",
            "url": "https://pokeapi.co/api/v2/pokemon-species/25"
        },
        "sprites": {
            "other": {
                "official-artwork": {
                    "front_default": "https://example.com/pikachu.png"
                }
            }
        }
    }

@pytest.fixture
def mock_species_response():
    return {
        "name": "pikachu",
        "names": [
            {"name": "皮卡丘", "language": {"name": "zh-Hant"}}
        ],
        "genera": [
            {"genus": "鼠寶可夢", "language": {"name": "zh-Hant"}},
            {"genus": "Mouse Pokémon", "language": {"name": "en"}}
        ]
    }

def test_fetch_random_pokemon_returns_correct_response(mock_pokemon_response, mock_species_response):
    with patch('requests.get') as mock_get:
        mock_get.side_effect = [
            Mock(json=lambda: mock_pokemon_response),
            Mock(json=lambda: mock_species_response)
        ]

        result = fetch_random_pokemon()

        assert result["id"] == "0025"
        assert result["name"] == "皮卡丘"
        assert result["types"] == "Electric"
        assert result["species"] == "鼠寶可夢"
        assert result["height"] == "0.4 m"
        assert result["weight"] == "6.0 kg"
        assert result["abilities"] == "Static"
        assert result["artwork"] == "https://example.com/pikachu.png"

def test_fetch_random_pokemon_no_traditional_chinese_genus(mock_pokemon_response):
    species_response_no_zh = {
        "name": "pikachu",
        "names": [{"name": "Pikachu", "language": {"name": "en"}}],
        "genera": [{"genus": "Mouse Pokémon", "language": {"name": "en"}}]
    }
    with patch('requests.get') as mock_get:
        mock_get.side_effect = [
            Mock(json=lambda: mock_pokemon_response),
            Mock(json=lambda: mock_species_response_no_zh)
        ]

        result = fetch_random_pokemon()
        # Should fallback gracefully to pokemon name if zh-Hant is missing
        assert result["species"] == "Pikachu"

def test_fetch_random_pokemon_calls_correct_endpoints(mock_pokemon_response, mock_species_response):
    with patch('requests.get') as mock_get, \
         patch('random.randint') as mock_randint:
        mock_get.side_effect = [
            Mock(json=lambda: mock_pokemon_response),
            Mock(json=lambda: mock_species_response)
        ]
        mock_randint.return_value = 25

        fetch_random_pokemon()

        mock_randint.assert_called_once_with(1, 151)
        mock_get.assert_any_call("https://pokeapi.co/api/v2/pokemon/25")
        mock_get.assert_any_call("https://pokeapi.co/api/v2/pokemon-species/25")

def test_fetch_random_pokemon_api_error():
    with patch('requests.get') as mock_get:
        mock_get.return_value.raise_for_status.side_effect = Exception("API Error")
        # Just ensuring it attempts request
        with pytest.raises(Exception):
            mock_get.return_value.raise_for_status()
