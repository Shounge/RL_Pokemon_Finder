import random

RARITY_WEIGHTS = {
    "common": 1.0,
    "uncommon": 0.65,
    "rare": 0.35,
    "ultra_rare": 0.15,
}


def score_pokemon(pokemon, env):
    score = 0
    reasons = []

    habitats = pokemon.get("habitats", [])
    weather_list = pokemon.get("weather", ["any"])
    near_water = pokemon.get("near_water", False)
    preferred_temp = pokemon.get("temperature_bands", ["any"])
    preferred_biomes = pokemon.get("biomes", [])
    rarity = pokemon.get("rarity", "common")

    env_habitat = env["habitat"]
    env_weather = env["weather"]
    env_terrain = env["terrain"]
    env_near_water = env["near_water"]
    env_urban = env["urban"]
    env_temp_band = env["temperature_band"]
    env_biomes = env.get("biomes", [])

    # 1. Core habitat match
    if env_habitat in habitats:
        score += 8
        reasons.append(f"strong habitat match: {env_habitat}")

        if len(habitats) == 1:
            score += 2
            reasons.append("specialized habitat fit")
    else:
        if any(h in habitats for h in ["plains", "grassland"]) and env_habitat in ["plains", "grassland"]:
            score += 4
            reasons.append("decent open-land habitat fit")
        elif any(h in habitats for h in ["mountain", "rocky"]) and env_habitat in ["mountain", "rocky"]:
            score += 4
            reasons.append("decent rocky terrain fit")
        else:
            score -= 6
            reasons.append(f"habitat mismatch for {env_habitat}")

    # 2. Weather
    if env_weather in weather_list or "any" in weather_list:
        score += 1
        reasons.append(f"matches weather: {env_weather}")
    else:
        score -= 1
        reasons.append(f"weather mismatch: {env_weather}")

    # 3. Water access
    if env_near_water == near_water:
        score += 2
        reasons.append("matches water access" if env_near_water else "matches dry land conditions")
    else:
        score -= 2
        reasons.append("not suited for water-heavy area" if env_near_water else "prefers water access")

    # 4. Terrain boosts
    if env_terrain == "mountain" and "mountain" in habitats:
        score += 2
        reasons.append("mountain terrain fits this pokemon")

    if env_urban and "urban" in habitats:
        score += 2
        reasons.append("urban surroundings fit this pokemon")

    # 5. Temperature band
    if "any" in preferred_temp or env_temp_band in preferred_temp:
        score += 2
        reasons.append(f"comfortable in {env_temp_band} temperatures")
    else:
        score -= 2
        reasons.append(f"temperature mismatch: {env_temp_band}")

    # 6. Biome weighting
    shared_biomes = [biome for biome in env_biomes if biome in preferred_biomes]
    if shared_biomes:
        biome_bonus = min(4, len(shared_biomes) * 2)
        score += biome_bonus
        reasons.append(f"biome fit: {', '.join(shared_biomes)}")
    elif preferred_biomes:
        score -= 1
        reasons.append("biome mismatch")

    # 7. Explicit biome conflict penalties
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

    return score, reasons, rarity


def match_pokemon(pokemon_list, env):
    results = []

    for pokemon in pokemon_list:
        score, reasons, rarity = score_pokemon(pokemon, env)

        if score >= 3:
            rarity_weight = RARITY_WEIGHTS.get(rarity, 1.0)
            weighted_score = max(score * rarity_weight, 0.1)

            results.append({
                "name": pokemon["name"],
                "sprite": pokemon.get("sprite"),
                "types": pokemon.get("types", []),
                "score": score,
                "weighted_score": round(weighted_score, 3),
                "rarity": rarity,
                "reasons": reasons
            })

    results.sort(key=lambda p: (p["score"], p["weighted_score"]), reverse=True)

    total_weight = sum(p["weighted_score"] for p in results)
    if total_weight > 0:
        for pokemon in results:
            pokemon["chance"] = round((pokemon["weighted_score"] / total_weight) * 100, 2)
    else:
        for pokemon in results:
            pokemon["chance"] = 0.0

    return results


def choose_random_pokemon(results):
    if not results:
        return None

    weights = [pokemon["weighted_score"] for pokemon in results]
    return random.choices(results, weights=weights, k=1)[0]