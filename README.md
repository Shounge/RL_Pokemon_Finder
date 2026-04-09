# Real-World Pokémon Habitat Finder

This project is a rule-based Pokémon encounter simulator that maps real-world locations to likely Pokémon habitats.

You give it a valid city name (works with countries too), and it analyzes real environmental data to determine which Pokémon would realistically live there.

---

## What This App Does

The app takes a real-world location and builds an environmental profile using:

* Geographic data (latitude, elevation)
* Weather conditions (via API)
* Terrain classification (flat, hilly, mountain)
* Habitat inference (urban, forest, desert, etc.)
* Biome detection (plains, alpine, coastal, etc.)
* Temperature band (cold, mild, warm, hot)
* Water proximity and urban density

This environment is then compared against a custom Pokémon dataset to determine which Pokémon best fit that location.

---

## How Pokémon Matching Works

Each Pokémon has structured habitat data stored locally (not AI-generated), including:

* Supported habitats (forest, plains, cave, etc.)
* Weather preferences
* Biomes
* Temperature ranges
* Water requirements
* Rarity multiplier



The matcher scores each Pokémon based on how well it fits the environment:

* Strong habitat match = high score
* Partial match = moderate score
* Mismatch = penalty
* Biome overlap adds additional score
* Temperature mismatch reduces score
* Rarity reduces final encounter chance



After scoring:

* Pokémon are ranked
* A weighted probability is computed
* A random encounter can be generated based on those weights

---

## Environment Analysis

The environment pipeline pulls real-world data and converts it into game-like attributes.

Key logic includes:

* Weather mapping (clear, rain, snow, etc.)
* Terrain classification based on elevation
* Habitat inference using keywords and geographic hints
* Biome construction from multiple signals



This is entirely deterministic and rule-based.

---

## Pokémon Data System

Pokémon data is built using the PokéAPI, but transformed into custom habitat system.

What happens:

* Fetch Pokémon + species data
* Map official habitat → custom system
* Apply type-based environmental hints
* Compute rarity using capture rate + flags
* Store everything locally in JSON

Key features:

* No hardcoding per Pokémon
* Scales automatically to full Pokédex
* Easily extendable rules



---

## What the App Returns

For a given location, the app outputs:

* A ranked list of Pokémon
* Score for each Pokémon
* Encounter probability (%)
* Rarity classification (common → ultra_rare)
* Explanation of why it fits the environment
* Sprite image (from PokéAPI)

---

## How to Run the Project

### 1. Install dependencies

```bash
pip install flask requests
```

---

### 2. Run the app

For CLI version:

```bash
python main.py
```

For web app:

```bash
python app.py
```

Then open:

```
http://127.0.0.1:5000
```

---

### 3. First run

On first run, the app will:

* Fetch Pokémon data from PokéAPI
* Build a local dataset
* Save it to JSON

This may take a bit, but only happens once.

---

## Example Usage

Input:

```
tokyo
```

Output:

* Environment: urban, mild temperature, cloudy
* Likely Pokémon: Pidgey, Rattata, Meowth, etc.
* Each with reasoning like:

  * "strong habitat match: urban"
  * "matches weather: cloudy"
  * "urban surroundings fit this pokemon"

---

## Design Philosophy

* No machine learning — everything is explainable
* Fully rule-based scoring system
* Data-driven and extensible
* Built to scale to the full Pokédex
* Focused on realism over game canon

---

## Expanding the Project

You can extend this by:

* Adding more Pokémon (increase PokéAPI limit)
* Refining habitat rules
* Improving biome detection
* Adding time-of-day logic
* Adding seasonal effects
* Improving UI/UX

---

## Summary

This is essentially a real-world → Pokémon ecosystem mapper.

It answers a simple question in a structured way:

"If Pokémon existed in the real world, which ones would live here?"

And it does it with actual environmental data and transparent logic.
