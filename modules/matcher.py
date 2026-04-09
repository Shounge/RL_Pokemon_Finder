def score_pokemon(pokemon, env):
    score = 0
    reasons = []

    habitats = pokemon.get("habitats", [])
    weather_list = pokemon.get("weather", ["any"])
    near_water = pokemon.get("near_water", False)

    if env["habitat"] in habitats:
        score += 5
        reasons.append(f"matches habitat: {env['habitat']}")

        if len(habitats) == 1:
            score += 1
            reasons.append("specialized habitat fit")

    if env["weather"] in weather_list or "any" in weather_list:
        score += 1
        reasons.append(f"matches weather: {env['weather']}")

    if env["near_water"] == near_water:
        score += 2
        if env["near_water"]:
            reasons.append("matches water access")
        else:
            reasons.append("matches dry land conditions")

    if env["terrain"] == "mountain" and "mountain" in habitats:
        score += 2
        reasons.append("mountain terrain fits this pokemon")

    if env["urban"] and "urban" in habitats:
        score += 1
        reasons.append("urban surroundings fit this pokemon")

    return score, reasons


def match_pokemon(pokemon_list, env):
    results = []

    for pokemon in pokemon_list:
        score, reasons = score_pokemon(pokemon, env)
        results.append({
            "name": pokemon["name"],
            "score": score,
            "reasons": reasons
        })

    results.sort(key=lambda p: p["score"], reverse=True)
    return results