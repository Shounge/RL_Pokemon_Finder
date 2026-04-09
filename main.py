from modules.models import load_pokemon_data
from modules.matcher import match_pokemon
from modules.geocoding import get_coords
from modules.environment import analyze_environment


def main():
    location_name = input("Enter a location: ").strip()

    location = get_coords(location_name)
    print("Loading Pokemon data...")
    pokemon_list = load_pokemon_data()
    environment = analyze_environment(location)
    results = match_pokemon(pokemon_list, environment)

    print("\nLocation found:")
    print(f"{location['name']}, {location['country']}")
    print(f"Latitude: {location['latitude']}")
    print(f"Longitude: {location['longitude']}")

    print("\nEnvironment:")
    for key, value in environment.items():
        print(f"  {key}: {value}")

    print("\nTop Pokémon matches:\n")
    for pokemon in results[:5]:
        print(f"{pokemon['name']} - score: {pokemon['score']}")
        for reason in pokemon["reasons"]:
            print(f"   - {reason}")
        print()


if __name__ == "__main__":
    main()