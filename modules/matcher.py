def score_pokemon(pokemon, env):
    score = 0
    reasons = []

    if env["habitat"] in pokemon["habitats"]:
        score += 5
        reasons.append(f"matches habitat: {env['habitat']}")

    if env["weather"] in pokemon["weather"] or "any" in pokemon["weather"]:
        score += 1
        reasons.append(f"matches weather: {env['weather']}")

    if env["near_water"] == pokemon["near_water"]:
        score += 2
        if env["near_water"]:
            reasons.append("matches water access")
        else:
            reasons.append("matches dry land conditions")

    if env["terrain"] == "mountain" and "mountain" in pokemon["habitats"]:
        score += 2
        reasons.append("mountain terrain fits this pokemon")

    if env["urban"] and "urban" in pokemon["habitats"]:
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