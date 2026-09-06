import random
import requests
from typing import Dict, Any

__MAX_POKEMON_ID = 151

def fetch_random_pokemon() -> Dict[str, Any]:
    """Fetch random Pokemon data from PokeAPI."""
    pokemon_id = random.randint(1, __MAX_POKEMON_ID)
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}")
    pokemon_data = response.json()

    types = [t["type"]["name"] for t in pokemon_data["types"]]
    abilities = [a["ability"]["name"] for a in pokemon_data["abilities"]]
    
    species_url = pokemon_data["species"]["url"]
    species_response = requests.get(species_url)
    species_data = species_response.json()
    
    # 1. Fetch Traditional Chinese name (zh-Hant)
    zh_name = pokemon_data["name"]  # Fallback
    for entry in species_data.get("names", []):
        if entry.get("language", {}).get("name") == "zh-Hant":
            zh_name = entry.get("name")
            break

    # 2. Fetch Traditional Chinese genus (zh-Hant)
    zh_species_name = pokemon_data["name"]  # Fallback
    for genus in species_data.get("genera", []):
        if genus.get("language", {}).get("name") == "zh-Hant":
            zh_species_name = genus.get("genus")
            break
   
    return {
        "id": str(pokemon_data["id"]).zfill(4),
        "name": zh_name,  # Traditional Chinese name
        "types": ", ".join(type.title() for type in types),
        "species": zh_species_name,  # Traditional Chinese genus
        "height": f"{pokemon_data['height'] / 10} m",  # Convert to meters
        "weight": f"{pokemon_data['weight'] / 10} kg",  # Convert to kilograms
        "abilities": ", ".join(ability.title() for ability in abilities),
        "artwork": pokemon_data["sprites"]["other"]["official-artwork"]["front_default"]
    }
