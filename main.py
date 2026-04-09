from modules.models import load_pokemon_data
from modules.matcher import match_pokemon, choose_random_pokemon
from modules.geocoding import get_coords
from modules.environment import analyze_environment


def main():
    location_name = input("Enter a location: ").strip()
    if not location_name:
        print("Please enter a location.")
        return

    location = get_coords(location_name)

    print("Loading Pokemon data...")
    pokemon_list = load_pokemon_data()

    environment = analyze_environment(location)
    results = match_pokemon(pokemon_list, environment)
    encounter = choose_random_pokemon(results)

    print("\nLocation found:")
    print(f"{location['name']}, {location['country']}")
    print(f"Latitude: {location['latitude']}")
    print(f"Longitude: {location['longitude']}")

    print("\nEnvironment:")
    for key, value in environment.items():
        print(f"  {key}: {value}")

    if not results:
        print("\nNo Pokémon matches found.")
        return

    print("\nWild encounter!")
    print(f"{encounter['name']} appeared! ({encounter['chance']}% chance)")
    for reason in encounter["reasons"]:
        print(f"   - {reason}")

    print("\nAll possible Pokémon here:\n")
    for pokemon in results:
        print(f"{pokemon['name']} - score: {pokemon['score']} - chance: {pokemon['chance']}%")


if __name__ == "__main__":
    main()