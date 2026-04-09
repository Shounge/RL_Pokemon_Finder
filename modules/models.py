import json
import os
import requests

POKEAPI_BASE = "https://pokeapi.co/api/v2"

HABITAT_MAP = {
    "forest": {
        "habitats": ["forest"],
        "weather": ["clear", "cloudy", "rain"],
        "near_water": False,
    },
    "grassland": {
        "habitats": ["grassland", "plains"],
        "weather": ["clear", "cloudy"],
        "near_water": False,
    },
    "mountain": {
        "habitats": ["mountain", "rocky"],
        "weather": ["clear", "cloudy"],
        "near_water": False,
    },
    "cave": {
        "habitats": ["cave"],
        "weather": ["any"],
        "near_water": False,
    },
    "sea": {
        "habitats": ["ocean", "coast"],
        "weather": ["any"],
        "near_water": True,
    },
    "waters-edge": {
        "habitats": ["river", "lake", "wetland", "coast"],
        "weather": ["any"],
        "near_water": True,
    },
    "urban": {
        "habitats": ["urban"],
        "weather": ["any"],
        "near_water": False,
    },
    "rough-terrain": {
        "habitats": ["rocky", "mountain", "sand"],
        "weather": ["clear", "cloudy"],
        "near_water": False,
    },
    None: {
        "habitats": ["plains"],
        "weather": ["any"],
        "near_water": False,
    },
}

TYPE_HINTS = {
    "water": {"habitats_add": ["river", "lake", "coast"], "near_water": True},
    "rock": {"habitats_add": ["rocky"]},
    "ground": {"habitats_add": ["sand"]},
    "grass": {"habitats_add": ["forest"], "weather_add": ["rain"]},
    "bug": {"habitats_add": ["forest"]},
    "fire": {"habitats_add": ["rocky"], "weather_add": ["clear"]},
    "electric": {"habitats_add": ["plains"]},
    "ghost": {"habitats_add": ["cave"], "weather_add": ["cloudy", "night", "any"]},
    "poison": {},
    "flying": {},
    "psychic": {},
}

def get_json(url):
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.json()

def merge_unique(*lists):
    merged = []
    seen = set()
    for lst in lists:
        for item in lst:
            if item not in seen:
                seen.add(item)
                merged.append(item)
    return merged

def build_pokemon_record(name):
    pokemon = get_json(f"{POKEAPI_BASE}/pokemon/{name}")
    species = get_json(f"{POKEAPI_BASE}/pokemon-species/{name}")

    types = [entry["type"]["name"] for entry in pokemon["types"]]
    official_habitat = species["habitat"]["name"] if species["habitat"] else None

    base = HABITAT_MAP.get(official_habitat, HABITAT_MAP[None])

    habitats = list(base["habitats"])
    weather = list(base["weather"])
    near_water = base["near_water"]

    for ptype in types:
        hint = TYPE_HINTS.get(ptype, {})
        habitats = merge_unique(habitats, hint.get("habitats_add", []))

        if hint.get("weather_add"):
            if "any" in weather:
                weather = []
            weather = merge_unique(weather, hint["weather_add"])

        if hint.get("near_water"):
            near_water = True

    if not weather:
        weather = ["any"]

        habitats = habitats[:3]

    return {
        "name": pokemon["name"].capitalize(),
        "types": types,
        "habitats": habitats,
        "weather": weather,
        "near_water": near_water,
    }

def build_pokemon_data(filepath="data/pokemon_data.json", limit=151):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    listing = get_json(f"{POKEAPI_BASE}/pokemon?limit={limit}&offset=0")
    pokemon_list = []

    for item in listing["results"]:
        name = item["name"]
        try:
            pokemon_list.append(build_pokemon_record(name))
            print(f"Built {name}")
        except Exception as exc:
            print(f"Skipping {name}: {exc}")

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(pokemon_list, file, indent=2)

    return pokemon_list

def load_pokemon_data(filepath="data/pokemon_data.json"):
    if not os.path.exists(filepath):
        print("Pokemon data file missing. Building dataset...")
        return build_pokemon_data(filepath=filepath)

    if os.path.getsize(filepath) == 0:
        print("Pokemon data file is empty. Building dataset...")
        return build_pokemon_data(filepath=filepath)

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("Pokemon data file is invalid. Rebuilding dataset...")
        return build_pokemon_data(filepath=filepath)