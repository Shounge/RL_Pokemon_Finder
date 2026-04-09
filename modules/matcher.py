import random


def score_pokemon(pokemon, env):
    score = 0
    reasons = []

    habitats = pokemon.get("habitats", [])
    weather_list = pokemon.get("weather", ["any"])
    near_water = pokemon.get("near_water", False)

    env_habitat = env["habitat"]
    env_weather = env["weather"]
    env_terrain = env["terrain"]
    env_near_water = env["near_water"]
    env_urban = env["urban"]

    # --- 1. Core habitat match ---
    if env_habitat in habitats:
        score += 8
        reasons.append(f"strong habitat match: {env_habitat}")

        if len(habitats) == 1:
            score += 2
            reasons.append("specialized habitat fit")
    else:
        score -= 6
        reasons.append(f"habitat mismatch for {env_habitat}")

    # --- 2. Weather ---
    if env_weather in weather_list or "any" in weather_list:
        score += 1
        reasons.append(f"matches weather: {env_weather}")
    else:
        score -= 1
        reasons.append(f"weather mismatch: {env_weather}")

    # --- 3. Water access ---
    if env_near_water == near_water:
        score += 2
        if env_near_water:
            reasons.append("matches water access")
        else:
            reasons.append("matches dry land conditions")
    else:
        score -= 2
        if env_near_water:
            reasons.append("not suited for water-heavy area")
        else:
            reasons.append("prefers water access")

    # --- 4. Terrain boosts ---
    if env_terrain == "mountain" and "mountain" in habitats:
        score += 2
        reasons.append("mountain terrain fits this pokemon")

    if env_urban and "urban" in habitats:
        score += 2
        reasons.append("urban surroundings fit this pokemon")

    # --- 5. Explicit biome conflict penalties ---
    if env_habitat == "sand":
        if any(h in habitats for h in ["forest", "grassland", "plains", "wetland"]):
            score -= 4
            reasons.append("poor fit for desert environment")

    if env_habitat == "forest":
        if any(h in habitats for h in ["sand", "rocky"]):
            score -= 3
            reasons.append("poor fit for dense forest")

    if env_habitat in ["river", "lake", "wetland", "coast", "ocean"] and not near_water:
        score -= 4
        reasons.append("not a water-adapted pokemon")

    return score, reasons

def match_pokemon(pokemon_list, env):
    results = []

    for pokemon in pokemon_list:
        score, reasons = score_pokemon(pokemon, env)

        if score >= 3:
            results.append({
                "name": pokemon["name"],
                "score": score,
                "reasons": reasons
            })

    results.sort(key=lambda p: p["score"], reverse=True)

    total_score = sum(p["score"] for p in results)
    if total_score > 0:
        for pokemon in results:
            pokemon["chance"] = round((pokemon["score"] / total_score) * 100, 2)
    else:
        for pokemon in results:
            pokemon["chance"] = 0.0

    return results


def choose_random_pokemon(results):
    if not results:
        return None

    weights = [pokemon["score"] for pokemon in results]
    return random.choices(results, weights=weights, k=1)[0]