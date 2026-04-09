import requests


MANUAL_LOCATIONS = {
    "sahara": {
        "query": "sahara",
        "name": "Sahara Desert",
        "latitude": 23.4162,
        "longitude": 25.6628,
        "country": "Algeria",
        "admin1": None,
        "admin2": None,
        "feature_code": "DSRT",
        "population": 0,
    },
    "sahara desert": {
        "query": "sahara desert",
        "name": "Sahara Desert",
        "latitude": 23.4162,
        "longitude": 25.6628,
        "country": "Algeria",
        "admin1": None,
        "admin2": None,
        "feature_code": "DSRT",
        "population": 0,
    },
    "danube delta": {
        "query": "danube delta",
        "name": "Danube Delta",
        "latitude": 45.1657,
        "longitude": 29.2380,
        "country": "Romania",
        "admin1": None,
        "admin2": None,
        "feature_code": "DLTA",
        "population": 0,
    },
    "swiss alps": {
        "query": "swiss alps",
        "name": "Swiss Alps",
        "latitude": 46.8876,
        "longitude": 9.6570,
        "country": "Switzerland",
        "admin1": None,
        "admin2": None,
        "feature_code": "MT",
        "population": 0,
    },
}


def get_coords(location):
    query = location.strip().lower()

    if query in MANUAL_LOCATIONS:
        return MANUAL_LOCATIONS[query]

    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": location,
        "count": 5,
        "language": "en",
        "format": "json"
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    results = data.get("results")
    if not results:
        raise ValueError(f"Could not find location: {location}")

    chosen = results[0]

    for place in results:
        place_name = (place.get("name") or "").lower()
        if query == place_name:
            chosen = place
            break

    return {
        "query": location,
        "name": chosen["name"],
        "latitude": chosen["latitude"],
        "longitude": chosen["longitude"],
        "country": chosen.get("country", "Unknown"),
        "admin1": chosen.get("admin1"),
        "admin2": chosen.get("admin2"),
        "feature_code": chosen.get("feature_code"),
        "population": chosen.get("population", 0),
    }