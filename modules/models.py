import json


def load_pokemon_data(filepath="data/pokemon_data.json"):
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)