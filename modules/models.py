import json
import os
import requests

POKEAPI_BASE = "https://pokeapi.co/api/v2"

HABITAT_MAP = {
    "forest": {
        "habitats": ["forest"],
        "weather": ["clear", "cloudy", "rain"],
        "near_water": False,
        "biomes": ["temperate_forest", "tropical_forest"],
        "temperature_bands": ["mild", "warm"],
    },
    "grassland": {
        "habitats": ["grassland", "plains"],
        "weather": ["clear", "cloudy"],
        "near_water": False,
        "biomes": ["plains"],
        "temperature_bands": ["mild", "warm"],
    },
    "mountain": {
        "habitats": ["mountain", "rocky"],
        "weather": ["clear", "cloudy"],
        "near_water": False,
        "biomes": ["alpine"],
        "temperature_bands": ["cold", "mild"],
    },
    "cave": {
        "habitats": ["cave"],
        "weather": ["any"],
        "near_water": False,
        "biomes": ["alpine"],
        "temperature_bands": ["cold", "mild"],
    },
    "sea": {
        "habitats": ["ocean", "coast"],
        "weather": ["any"],
        "near_water": True,
        "biomes": ["coastal"],
        "temperature_bands": ["mild", "warm"],
    },
    "waters-edge": {
        "habitats": ["river", "lake", "wetland", "coast"],
        "weather": ["any"],
        "near_water": True,
        "biomes": ["freshwater", "wetland", "coastal"],
        "temperature_bands": ["mild", "warm"],
    },
    "urban": {
        "habitats": ["urban"],
        "weather": ["any"],
        "near_water": False,
        "biomes": ["urban"],
        "temperature_bands": ["any"],
    },
    "rough-terrain": {
        "habitats": ["rocky", "mountain", "sand"],
        "weather": ["clear", "cloudy"],
        "near_water": False,
        "biomes": ["alpine", "arid"],
        "temperature_bands": ["mild", "warm"],
    },
    None: {
        "habitats": ["plains"],
        "weather": ["any"],
        "near_water": False,
        "biomes": ["plains"],
        "temperature_bands": ["any"],
    },
}

TYPE_HINTS = {
    "water": {
        "habitats_add": ["river", "lake", "coast"],
        "near_water": True,
        "biomes_add": ["freshwater", "coastal"],
        "temperature_bands_add": ["mild", "warm"],
    },
    "rock": {
        "habitats_add": ["rocky"],
        "biomes_add": ["alpine"],
        "temperature_bands_add": ["cold", "mild"],
    },
    "ground": {
        "habitats_add": ["sand"],
        "biomes_add": ["arid"],
        "temperature_bands_add": ["warm", "hot"],
    },
    "grass": {
        "habitats_add": ["forest"],
        "weather_add": ["rain"],
        "biomes_add": ["temperate_forest", "plains"],
        "temperature_bands_add": ["mild", "warm"],
    },
    "bug": {
        "habitats_add": ["forest"],
        "biomes_add": ["temperate_forest"],
        "temperature_bands_add": ["mild", "warm"],
    },
    "fire": {
        "habitats_add": ["rocky"],
        "weather_add": ["clear"],
        "biomes_add": ["arid"],
        "temperature_bands_add": ["warm", "hot"],
    },
    "electric": {
        "habitats_add": ["plains"],
        "biomes_add": ["plains", "urban"],
        "temperature_bands_add": ["mild", "warm"],
    },
    "ghost": {
        "habitats_add": ["cave"],
        "weather_add": ["cloudy", "any"],
        "biomes_add": ["urban", "alpine"],
        "temperature_bands_add": ["cold", "mild"],
    },
    "ice": {
        "biomes_add": ["alpine", "coastal"],
        "temperature_bands_add": ["cold"],
    },
    "fighting": {
        "biomes_add": ["urban", "alpine"],
        "temperature_bands_add": ["mild", "warm"],
    },
    "poison": {
        "biomes_add": ["urban", "wetland"],
    },
    "flying": {
        "biomes_add": ["plains", "coastal", "alpine"],
    },
    "psychic": {
        "biomes_add": ["urban"],
    },
    "dragon": {
        "biomes_add": ["coastal", "freshwater", "alpine"],
        "temperature_bands_add": ["mild", "warm"],
    },
}

RARITY_OVERRIDES = {
    "articuno": "ultra_rare",
    "zapdos": "ultra_rare",
    "moltres": "ultra_rare",
    "mewtwo": "ultra_rare",
    "mew": "ultra_rare",
    "dragonite": "rare",
    "dratini": "rare",
    "dragonair": "rare",
    "lapras": "rare",
    "snorlax": "rare",
    "aerodactyl": "rare",
    "chansey": "rare",
    "eevee": "rare",
    "porygon": "rare",
    "scyther": "rare",
    "pinsir": "rare",
}

TYPE_RARITY_DEFAULTS = {
    "dragon": "rare",
    "ice": "uncommon",
    "ghost": "uncommon",
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


def infer_rarity(name, types, is_legendary, is_mythical, evolves_from_species):
    if is_legendary or is_mythical:
        return "ultra_rare"

    if name in RARITY_OVERRIDES:
        return RARITY_OVERRIDES[name]

    for ptype in types:
        if ptype in TYPE_RARITY_DEFAULTS:
            return TYPE_RARITY_DEFAULTS[ptype]

    if evolves_from_species is None:
        return "uncommon"

    return "common"


def build_pokemon_record(name):
    pokemon = get_json(f"{POKEAPI_BASE}/pokemon/{name}")
    species = get_json(f"{POKEAPI_BASE}/pokemon-species/{name}")
    sprite = pokemon["sprites"]["front_default"]

    types = [entry["type"]["name"] for entry in pokemon["types"]]
    official_habitat = species["habitat"]["name"] if species["habitat"] else None

    base = HABITAT_MAP.get(official_habitat, HABITAT_MAP[None])

    habitats = list(base["habitats"])
    weather = list(base["weather"])
    near_water = base["near_water"]
    biomes = list(base["biomes"])
    temperature_bands = list(base["temperature_bands"])

    for ptype in types:
        hint = TYPE_HINTS.get(ptype, {})
        habitats = merge_unique(habitats, hint.get("habitats_add", []))
        biomes = merge_unique(biomes, hint.get("biomes_add", []))
        temperature_bands = merge_unique(temperature_bands, hint.get("temperature_bands_add", []))

        if hint.get("weather_add"):
            if "any" in weather:
                weather = []
            weather = merge_unique(weather, hint["weather_add"])

        if hint.get("near_water"):
            near_water = True

    if not weather:
        weather = ["any"]

    rarity = infer_rarity(
        name=name,
        types=types,
        is_legendary=species.get("is_legendary", False),
        is_mythical=species.get("is_mythical", False),
        evolves_from_species=species.get("evolves_from_species"),
    )

    return {
        "name": pokemon["name"].capitalize(),
        "types": types,
        "habitats": habitats,
        "weather": weather,
        "near_water": near_water,
        "biomes": biomes,
        "temperature_bands": temperature_bands,
        "rarity": rarity,
        "sprite": sprite,
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