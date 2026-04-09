from flask import Flask, render_template, request

from modules.models import load_pokemon_data
from modules.matcher import match_pokemon, choose_random_pokemon
from modules.geocoding import get_coords
from modules.environment import analyze_environment

app = Flask(__name__)

POKEMON_LIST = load_pokemon_data()


def get_location_results(location_name):
    location = get_coords(location_name)
    environment = analyze_environment(location)
    results = match_pokemon(POKEMON_LIST, environment)
    encounter = choose_random_pokemon(results) if results else None
    return location, environment, results, encounter


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        location_name = request.form.get("location", "").strip()

        if not location_name:
            return render_template(
                "index.html",
                error="Please enter a location."
            )

        try:
            location, environment, results, encounter = get_location_results(location_name)

            return render_template(
                "index.html",
                location=location,
                environment=environment,
                results=results,
                encounter=encounter,
                location_name=location_name
            )
        except Exception as exc:
            return render_template(
                "index.html",
                error=str(exc),
                location_name=location_name
            )

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)