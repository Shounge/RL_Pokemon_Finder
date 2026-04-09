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
        "weather": ["clear", "cloudy", "snow"],
        "near_water": False,
        "biomes": ["alpine", "rocky"],
        "temperature_bands": ["cold", "mild"],
    },
    "cave": {
        "habitats": ["cave"],
        "weather": ["any"],
        "near_water": False,
        "biomes": ["cave"],
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
        "temperature_bands": ["mild", "warm"],
    },
    "rough-terrain": {
        "habitats": ["rocky", "mountain", "sand"],
        "weather": ["clear", "cloudy"],
        "near_water": False,
        "biomes": ["rocky", "alpine", "arid"],
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
        "temperature_bands_override": ["mild", "warm"],
    },
    "fire": {
        "habitats_add": ["rocky"],
        "weather_add": ["clear"],
        "biomes_add": ["arid", "rocky"],
        "temperature_bands_override": ["warm", "hot"],
    },
    "ice": {
        "biomes_add": ["alpine", "snow"],
        "temperature_bands_override": ["cold"],
    },
    "grass": {
        "habitats_add": ["forest"],
        "weather_add": ["rain"],
        "biomes_add": ["temperate_forest", "plains"],
        "temperature_bands_add": ["mild", "warm"],
    },
    "ground": {
        "habitats_add": ["sand"],
        "biomes_add": ["arid"],
        "temperature_bands_add": ["warm", "hot"],
    },
    "rock": {
        "habitats_add": ["rocky"],
        "biomes_add": ["rocky", "alpine"],
        "temperature_bands_add": ["mild", "cold"],
    },
    "electric": {
        "habitats_add": ["plains"],
        "biomes_add": ["plains", "urban"],
        "temperature_bands_add": ["mild", "warm"],
    },
    "ghost": {
        "habitats_add": ["cave"],
        "weather_add": ["cloudy"],
        "biomes_add": ["cave", "urban"],
        "temperature_bands_add": ["cold", "mild"],
    },
    "bug": {
        "habitats_add": ["forest"],
        "biomes_add": ["temperate_forest"],
        "temperature_bands_add": ["mild", "warm"],
    },
    "flying": {
        "biomes_add": ["plains", "coastal", "alpine"],
    },
    "poison": {
        "biomes_add": ["urban", "wetland"],
    },
    "psychic": {
        "biomes_add": ["urban"],
    },
    "dragon": {
        "biomes_add": ["coastal", "freshwater", "alpine"],
        "temperature_bands_add": ["mild", "warm"],
    },
    "fighting": {
        "biomes_add": ["urban", "alpine"],
        "temperature_bands_add": ["mild", "warm"],
    },
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


def compute_rarity_multiplier(species, types):
    if species.get("is_legendary") or species.get("is_mythical"):
        return 0.05

    capture_rate = species.get("capture_rate", 255)
    is_baby = species.get("is_baby", False)

    multiplier = max(0.25, min(1.0, capture_rate / 255))

    if is_baby:
        multiplier *= 0.8

    if "dragon" in types:
        multiplier *= 0.8

    return round(multiplier, 3)


def rarity_label_from_multiplier(multiplier):
    if multiplier <= 0.10:
        return "ultra_rare"
    if multiplier <= 0.35:
        return "rare"
    if multiplier <= 0.70:
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
    biomes = list(base.get("biomes", []))
    temperature_bands = list(base.get("temperature_bands", ["any"]))

    for ptype in types:
        hint = TYPE_HINTS.get(ptype, {})

        habitats = merge_unique(habitats, hint.get("habitats_add", []))
        biomes = merge_unique(biomes, hint.get("biomes_add", []))

        if hint.get("weather_add"):
            if "any" in weather:
                weather = []
            weather = merge_unique(weather, hint["weather_add"])

        if hint.get("near_water"):
            near_water = True

        if hint.get("temperature_bands_override"):
            temperature_bands = list(hint["temperature_bands_override"])
        else:
            temperature_bands = merge_unique(
                temperature_bands,
                hint.get("temperature_bands_add", [])
            )

    if "any" in temperature_bands and len(temperature_bands) > 1:
        temperature_bands = [t for t in temperature_bands if t != "any"]

    if not weather:
        weather = ["any"]

    rarity_multiplier = compute_rarity_multiplier(species, types)
    rarity_label = rarity_label_from_multiplier(rarity_multiplier)

    return {
        "name": pokemon["name"].capitalize(),
        "types": types,
        "habitats": habitats,
        "weather": weather,
        "near_water": near_water,
        "biomes": biomes,
        "temperature_bands": temperature_bands,
        "rarity_multiplier": rarity_multiplier,
        "rarity_label": rarity_label,
        "sprite": sprite,
    }


def build_pokemon_data(filepath="data/pokemon_data.json", limit=9999):
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