import random


def score_pokemon(pokemon, env):
    score = 0
    reasons = []

    habitats = pokemon.get("habitats", [])
    weather_list = pokemon.get("weather", ["any"])
    near_water = pokemon.get("near_water", False)
    biomes = pokemon.get("biomes", [])
    temperature_bands = pokemon.get("temperature_bands", ["any"])

    env_habitat = env["habitat"]
    env_weather = env["weather"]
    env_terrain = env["terrain"]
    env_near_water = env["near_water"]
    env_urban = env["urban"]
    env_biomes = env.get("biomes", [])
    env_temp_band = env.get("temperature_band", "mild")

    if env_habitat in habitats:
        score += 8
        reasons.append(f"strong habitat match: {env_habitat}")
    else:
        if any(h in habitats for h in ["plains", "grassland"]) and env_habitat in ["plains", "grassland"]:
            score += 4
            reasons.append("decent open-land habitat fit")
        elif any(h in habitats for h in ["mountain", "rocky"]) and env_habitat in ["mountain", "rocky"]:
            score += 4
            reasons.append("decent rocky terrain fit")
        else:
            score -= 5
            reasons.append(f"habitat mismatch for {env_habitat}")

    if env_weather in weather_list or "any" in weather_list:
        score += 1
        reasons.append(f"matches weather: {env_weather}")
    else:
        score -= 1
        reasons.append(f"weather mismatch: {env_weather}")

    if env_near_water == near_water:
        score += 2
        reasons.append("matches water access" if env_near_water else "matches dry land conditions")
    else:
        score -= 2
        reasons.append("not suited for water-heavy area" if env_near_water else "prefers water access")

    if env_terrain == "mountain" and "mountain" in habitats:
        score += 2
        reasons.append("mountain terrain fits this pokemon")

    if env_urban and "urban" in habitats:
        score += 2
        reasons.append("urban surroundings fit this pokemon")

    shared_biomes = [b for b in env_biomes if b in biomes]
    if shared_biomes:
        score += min(4, len(shared_biomes) * 2)
        reasons.append(f"biome fit: {', '.join(shared_biomes)}")
    elif biomes:
        score -= 1
        reasons.append("biome mismatch")

    if "any" in temperature_bands or env_temp_band in temperature_bands:
        score += 2
        reasons.append(f"comfortable in {env_temp_band} temperatures")
    else:
        score -= 3
        reasons.append(f"temperature mismatch: {env_temp_band}")

    return score, reasons


def match_pokemon(pokemon_list, env):
    results = []

    for pokemon in pokemon_list:
        score, reasons = score_pokemon(pokemon, env)

        if score >= 3:
            rarity_multiplier = pokemon.get("rarity_multiplier", 1.0)
            weighted_score = max(score * rarity_multiplier, 0.1)

            results.append({
                "name": pokemon["name"],
                "sprite": pokemon.get("sprite"),
                "types": pokemon.get("types", []),
                "score": score,
                "weighted_score": round(weighted_score, 3),
                "rarity_label": pokemon.get("rarity_label", "common"),
                "rarity_multiplier": rarity_multiplier,
                "reasons": reasons,
            })

    results.sort(key=lambda p: (p["score"], p["weighted_score"]), reverse=True)

    total_weight = sum(p["weighted_score"] for p in results)
    for pokemon in results:
        pokemon["chance"] = round((pokemon["weighted_score"] / total_weight) * 100, 2) if total_weight else 0.0

    return results


def choose_random_pokemon(results):
    if not results:
        return None

    weights = [pokemon["weighted_score"] for pokemon in results]
    return random.choices(results, weights=weights, k=1)[0]