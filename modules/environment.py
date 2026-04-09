import requests

CLOUDY_CODES = [1, 2, 3, 45, 48]
RAIN_CODES = [51, 53, 55, 56, 57, 61, 63, 65, 80, 81, 82]
SNOW_CODES = [71, 73, 75, 77, 85, 86]
STORM_CODES = [95, 96, 99]


def get_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,weather_code",
        "timezone": "auto"
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()["current"]


def get_elevation(lat, lon):
    url = "https://api.open-meteo.com/v1/elevation"
    params = {
        "latitude": lat,
        "longitude": lon
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    elevations = data.get("elevation", [])
    if not elevations:
        return 0

    return elevations[0]


def map_weather(weather_code):
    if weather_code == 0:
        return "clear"
    if weather_code in CLOUDY_CODES:
        return "cloudy"
    if weather_code in RAIN_CODES:
        return "rain"
    if weather_code in SNOW_CODES:
        return "snow"
    if weather_code in STORM_CODES:
        return "storm"
    return "unknown"


def classify_terrain(elevation):
    if elevation >= 1800:
        return "mountain"
    if elevation >= 600:
        return "hilly"
    return "flat"


def infer_broad_region(latitude, elevation):
    if elevation >= 1800:
        return "mountain"
    if abs(latitude) < 23:
        return "tropical"
    if abs(latitude) > 55:
        return "cold"
    return "temperate"


def infer_habitat(location, terrain, broad_region):
    query = (location.get("query") or "").lower()
    name = (location.get("name") or "").lower()
    country = (location.get("country") or "").lower()
    feature_code = (location.get("feature_code") or "").upper()

    text = f"{query} {name} {country}"

    if "sahara" in query or "desert" in query or "dune" in query:
        return "sand"
    if "delta" in text or "marsh" in text or "swamp" in text or "wetland" in text:
        return "wetland"
    if "forest" in text or "rainforest" in text or "woods" in text or "jungle" in text:
        return "forest"
    if "mountain" in text or "alps" in text or "carpathian" in text or "himalaya" in text:
        return "mountain"
    if "lake" in text:
        return "lake"
    if "river" in text:
        return "river"
    if "coast" in text or "beach" in text or "ocean" in text or "sea" in text:
        return "coast"
    if "cave" in text:
        return "cave"

    if feature_code.startswith("PPL"):
        return "urban"

    if terrain == "mountain":
        return "mountain"
    if terrain == "hilly":
        return "grassland"

    if broad_region == "tropical":
        return "forest"
    if broad_region == "cold":
        return "rocky"

    return "plains"


def infer_near_water(location):
    query = (location.get("query") or "").lower()
    name = (location.get("name") or "").lower()
    text = f"{query} {name}"

    water_words = [
        "lake", "river", "delta", "coast", "beach",
        "ocean", "sea", "bay", "gulf", "canal"
    ]
    return any(word in text for word in water_words)


def infer_urban(location, habitat):
    feature_code = (location.get("feature_code") or "").upper()
    population = location.get("population") or 0
    return habitat == "urban" or feature_code.startswith("PPL") or population > 100000


def infer_temperature_band(temp_c):
    if temp_c <= 5:
        return "cold"
    if temp_c <= 18:
        return "mild"
    if temp_c <= 28:
        return "warm"
    return "hot"


def infer_biomes(location, habitat, terrain, broad_region, near_water, urban, temp_c):
    biomes = set()
    query = (location.get("query") or "").lower()
    name = (location.get("name") or "").lower()
    text = f"{query} {name}"

    if urban:
        biomes.add("urban")

    if habitat in ["forest"]:
        if broad_region == "tropical":
            biomes.add("tropical_forest")
        else:
            biomes.add("temperate_forest")

    if habitat in ["grassland", "plains"]:
        biomes.add("plains")

    if habitat in ["mountain", "rocky"] or terrain == "mountain":
        biomes.add("alpine")

    if habitat == "sand":
        biomes.add("arid")

    if habitat in ["wetland", "river", "lake"]:
        biomes.add("freshwater")

    if habitat == "wetland":
        biomes.add("wetland")

    if habitat in ["coast", "ocean"]:
        biomes.add("coastal")

    if "desert" in text or "sahara" in text:
        biomes.add("arid")
    if "rainforest" in text or "jungle" in text:
        biomes.add("tropical_forest")
    if "swamp" in text or "marsh" in text or "delta" in text:
        biomes.add("wetland")
    if "coast" in text or "beach" in text or "sea" in text or "ocean" in text:
        biomes.add("coastal")
    if "river" in text or "lake" in text:
        biomes.add("freshwater")

    if near_water and not {"freshwater", "coastal", "wetland"} & biomes:
        biomes.add("freshwater")

    if not biomes:
        if broad_region == "tropical":
            biomes.add("tropical_forest")
        elif broad_region == "cold":
            biomes.add("alpine")
        else:
            biomes.add("plains")

    return sorted(biomes)


def analyze_environment(location):
    lat = location["latitude"]
    lon = location["longitude"]

    current = get_weather(lat, lon)
    elevation = get_elevation(lat, lon)

    terrain = classify_terrain(elevation)
    broad_region = infer_broad_region(lat, elevation)
    weather = map_weather(current["weather_code"])
    temp_c = current["temperature_2m"]

    habitat = infer_habitat(location, terrain, broad_region)
    near_water = infer_near_water(location)
    urban = infer_urban(location, habitat)
    temperature_band = infer_temperature_band(temp_c)
    biomes = infer_biomes(location, habitat, terrain, broad_region, near_water, urban, temp_c)

    print(f"[ENV DEBUG] query: {location.get('query')}")
    print(f"[ENV DEBUG] matched place: {location.get('name')}, {location.get('country')}")
    print(f"[ENV DEBUG] base habitat: {habitat}")
    print(f"[ENV DEBUG] biomes: {biomes}")
    print(f"[ENV DEBUG] temperature band: {temperature_band}")

    return {
        "habitat": habitat,
        "weather": weather,
        "temperature_c": temp_c,
        "temperature_band": temperature_band,
        "elevation_m": elevation,
        "terrain": terrain,
        "near_water": near_water,
        "urban": urban,
        "broad_region": broad_region,
        "biomes": biomes,
        "osm_tags": []
    }