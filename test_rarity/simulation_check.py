from collections import Counter, defaultdict
import csv
import os

from modules.models import load_pokemon_data
from modules.matcher import match_pokemon, choose_random_pokemon

RUNS_PER_ENV = 1000


def get_benchmark_envs():
    return [
        {
            "name": "Dense Urban Core",
            "env": {
                "habitat": "urban",
                "weather": "cloudy",
                "temperature_c": 18,
                "elevation_m": 40,
                "terrain": "flat",
                "near_water": False,
                "urban": True,
                "broad_region": "temperate",
                "osm_tags": []
            }
        },
        {
            "name": "Rainy Waterfront City",
            "env": {
                "habitat": "urban",
                "weather": "rain",
                "temperature_c": 14,
                "elevation_m": 5,
                "terrain": "flat",
                "near_water": True,
                "urban": True,
                "broad_region": "temperate",
                "osm_tags": []
            }
        },
        {
            "name": "Open Grassland",
            "env": {
                "habitat": "grassland",
                "weather": "clear",
                "temperature_c": 22,
                "elevation_m": 250,
                "terrain": "flat",
                "near_water": False,
                "urban": False,
                "broad_region": "temperate",
                "osm_tags": []
            }
        },
        {
            "name": "Windy Plains",
            "env": {
                "habitat": "plains",
                "weather": "cloudy",
                "temperature_c": 17,
                "elevation_m": 300,
                "terrain": "flat",
                "near_water": False,
                "urban": False,
                "broad_region": "temperate",
                "osm_tags": []
            }
        },
        {
            "name": "Temperate Forest",
            "env": {
                "habitat": "forest",
                "weather": "cloudy",
                "temperature_c": 16,
                "elevation_m": 380,
                "terrain": "hilly",
                "near_water": False,
                "urban": False,
                "broad_region": "temperate",
                "osm_tags": []
            }
        },
        {
            "name": "Rainforest Edge",
            "env": {
                "habitat": "forest",
                "weather": "rain",
                "temperature_c": 28,
                "elevation_m": 120,
                "terrain": "flat",
                "near_water": True,
                "urban": False,
                "broad_region": "tropical",
                "osm_tags": []
            }
        },
        {
            "name": "High Mountain Ridge",
            "env": {
                "habitat": "mountain",
                "weather": "clear",
                "temperature_c": 4,
                "elevation_m": 2400,
                "terrain": "mountain",
                "near_water": False,
                "urban": False,
                "broad_region": "mountain",
                "osm_tags": []
            }
        },
        {
            "name": "Rocky Badlands",
            "env": {
                "habitat": "rocky",
                "weather": "clear",
                "temperature_c": 24,
                "elevation_m": 900,
                "terrain": "hilly",
                "near_water": False,
                "urban": False,
                "broad_region": "temperate",
                "osm_tags": []
            }
        },
        {
            "name": "Desert Dunes",
            "env": {
                "habitat": "sand",
                "weather": "clear",
                "temperature_c": 39,
                "elevation_m": 450,
                "terrain": "flat",
                "near_water": False,
                "urban": False,
                "broad_region": "hot",
                "osm_tags": []
            }
        },
        {
            "name": "Night Cave",
            "env": {
                "habitat": "cave",
                "weather": "night",
                "temperature_c": 11,
                "elevation_m": 700,
                "terrain": "hilly",
                "near_water": False,
                "urban": False,
                "broad_region": "temperate",
                "osm_tags": []
            }
        },
        {
            "name": "Freshwater Lake",
            "env": {
                "habitat": "lake",
                "weather": "cloudy",
                "temperature_c": 15,
                "elevation_m": 190,
                "terrain": "flat",
                "near_water": True,
                "urban": False,
                "broad_region": "temperate",
                "osm_tags": []
            }
        },
        {
            "name": "Riverbank",
            "env": {
                "habitat": "river",
                "weather": "rain",
                "temperature_c": 17,
                "elevation_m": 95,
                "terrain": "flat",
                "near_water": True,
                "urban": False,
                "broad_region": "temperate",
                "osm_tags": []
            }
        },
        {
            "name": "Delta Wetland",
            "env": {
                "habitat": "wetland",
                "weather": "cloudy",
                "temperature_c": 18,
                "elevation_m": 8,
                "terrain": "flat",
                "near_water": True,
                "urban": False,
                "broad_region": "temperate",
                "osm_tags": []
            }
        },
        {
            "name": "Temperate Coast",
            "env": {
                "habitat": "coast",
                "weather": "clear",
                "temperature_c": 21,
                "elevation_m": 12,
                "terrain": "flat",
                "near_water": True,
                "urban": False,
                "broad_region": "temperate",
                "osm_tags": []
            }
        },
        {
            "name": "Open Ocean",
            "env": {
                "habitat": "ocean",
                "weather": "cloudy",
                "temperature_c": 19,
                "elevation_m": 0,
                "terrain": "flat",
                "near_water": True,
                "urban": False,
                "broad_region": "temperate",
                "osm_tags": []
            }
        },
        {
            "name": "Cold Snowy Coast",
            "env": {
                "habitat": "coast",
                "weather": "snow",
                "temperature_c": -2,
                "elevation_m": 3,
                "terrain": "flat",
                "near_water": True,
                "urban": False,
                "broad_region": "cold",
                "osm_tags": []
            }
        },
    ]


def classify_pokemon(result_count, chosen_count):
    if result_count == 0:
        return "missing"
    if chosen_count == 0:
        return "underpowered"
    if result_count <= 2:
        return "niche"
    return "healthy"


def save_csv(filename, rows, fieldnames):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def print_bar_chart(title, items, width=40, max_items=20):
    print(f"\n=== {title} ===")
    if not items:
        print("No data")
        return

    top_items = items[:max_items]
    max_value = top_items[0][1] if top_items else 1

    for name, value in top_items:
        bar_len = int((value / max_value) * width) if max_value else 0
        bar = "#" * bar_len
        print(f"{name:20} | {bar} {value}")


def optional_plots(summary_rows, env_top_rows):
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        print("\nMatplotlib not available, skipping PNG plots.")
        print(f"Reason: {exc}")
        return

    top_chosen = sorted(summary_rows, key=lambda r: r["times_chosen"], reverse=True)[:20]
    top_chosen = list(reversed(top_chosen))

    plt.figure(figsize=(10, 8))
    plt.barh(
        [row["pokemon"] for row in top_chosen],
        [row["times_chosen"] for row in top_chosen]
    )
    plt.xlabel("Times chosen across all simulations")
    plt.ylabel("Pokémon")
    plt.title("Top 20 chosen Pokémon")
    plt.tight_layout()
    plt.savefig("top_20_chosen.png", dpi=150)
    plt.close()

    status_counts = Counter(row["status"] for row in summary_rows)
    labels = sorted(status_counts.keys())
    values = [status_counts[label] for label in labels]

    plt.figure(figsize=(8, 5))
    plt.bar(labels, values)
    plt.xlabel("Coverage status")
    plt.ylabel("Number of Pokémon")
    plt.title("Coverage health")
    plt.tight_layout()
    plt.savefig("coverage_status.png", dpi=150)
    plt.close()

    dominance = []
    for row in env_top_rows:
        dominance.append((row["environment"], row["top_share"]))
    dominance.sort(key=lambda x: x[1])

    plt.figure(figsize=(10, 7))
    plt.barh([x[0] for x in dominance], [x[1] for x in dominance])
    plt.xlabel("Share of most common encounter")
    plt.ylabel("Environment")
    plt.title("Encounter dominance by environment")
    plt.tight_layout()
    plt.savefig("environment_dominance.png", dpi=150)
    plt.close()

    print("\nSaved PNG plots:")
    print("- top_20_chosen.png")
    print("- coverage_status.png")
    print("- environment_dominance.png")


def main():
    pokemon_list = load_pokemon_data()
    benchmark_envs = get_benchmark_envs()

    result_appearances = Counter()
    chosen_counts = Counter()
    best_scores = defaultdict(int)
    env_winners = {case["name"]: Counter() for case in benchmark_envs}
    env_candidate_counts = {}

    for case in benchmark_envs:
        env_name = case["name"]
        env = case["env"]

        results = match_pokemon(pokemon_list, env)
        env_candidate_counts[env_name] = len(results)

        for pokemon in results:
            name = pokemon["name"]
            result_appearances[name] += 1
            best_scores[name] = max(best_scores[name], pokemon["score"])

        for _ in range(RUNS_PER_ENV):
            chosen = choose_random_pokemon(results)
            if chosen:
                chosen_counts[chosen["name"]] += 1
                env_winners[env_name][chosen["name"]] += 1

    total_encounters = len(benchmark_envs) * RUNS_PER_ENV
    all_names = [pokemon["name"] for pokemon in pokemon_list]

    summary_rows = []
    for name in all_names:
        result_count = result_appearances[name]
        chosen_count = chosen_counts[name]
        best_score = best_scores[name]

        summary_rows.append({
            "pokemon": name,
            "times_in_result_lists": result_count,
            "times_chosen": chosen_count,
            "best_score_seen": best_score,
            "coverage_ratio": round(result_count / len(benchmark_envs), 3),
            "chosen_share": round(chosen_count / total_encounters, 5),
            "status": classify_pokemon(result_count, chosen_count)
        })

    summary_rows.sort(
        key=lambda row: (
            row["times_chosen"],
            row["times_in_result_lists"],
            row["best_score_seen"],
            row["pokemon"]
        ),
        reverse=True
    )

    env_rows = []
    env_top_rows = []

    for env_name, counter in env_winners.items():
        total = sum(counter.values())
        for pokemon, count in counter.most_common():
            env_rows.append({
                "environment": env_name,
                "pokemon": pokemon,
                "count": count,
                "share": round(count / total, 5) if total else 0.0
            })

        if total > 0:
            top_name, top_count = counter.most_common(1)[0]
            env_top_rows.append({
                "environment": env_name,
                "top_pokemon": top_name,
                "top_count": top_count,
                "top_share": round(top_count / total, 5),
                "candidate_count": env_candidate_counts[env_name]
            })
        else:
            env_top_rows.append({
                "environment": env_name,
                "top_pokemon": None,
                "top_count": 0,
                "top_share": 0.0,
                "candidate_count": env_candidate_counts[env_name]
            })

    save_csv(
        "simulation_summary.csv",
        summary_rows,
        [
            "pokemon",
            "times_in_result_lists",
            "times_chosen",
            "best_score_seen",
            "coverage_ratio",
            "chosen_share",
            "status"
        ]
    )

    save_csv(
        "environment_winners.csv",
        env_rows,
        ["environment", "pokemon", "count", "share"]
    )

    save_csv(
        "environment_summary.csv",
        env_top_rows,
        ["environment", "top_pokemon", "top_count", "top_share", "candidate_count"]
    )

    missing = [row for row in summary_rows if row["status"] == "missing"]
    underpowered = [row for row in summary_rows if row["status"] == "underpowered"]
    niche = [row for row in summary_rows if row["status"] == "niche"]

    print("\n=== BENCHMARK SUMMARY ===")
    print(f"Benchmark environments: {len(benchmark_envs)}")
    print(f"Runs per environment: {RUNS_PER_ENV}")
    print(f"Total encounters simulated: {total_encounters}")

    print(f"\nMissing Pokémon: {len(missing)}")
    if missing:
        print(", ".join(row["pokemon"] for row in missing))

    print(f"\nUnderpowered Pokémon: {len(underpowered)}")
    if underpowered:
        print(", ".join(row["pokemon"] for row in underpowered))

    print(f"\nNiche Pokémon: {len(niche)}")
    if niche:
        print(", ".join(row["pokemon"] for row in niche[:25]))

    print_bar_chart(
        "TOP 20 MOST CHOSEN",
        [(row["pokemon"], row["times_chosen"]) for row in summary_rows],
        max_items=20
    )

    print("\n=== ENVIRONMENT CANDIDATE COUNTS ===")
    for env_name, count in env_candidate_counts.items():
        print(f"{env_name:20} | {count}")

    print("\n=== TOP ENCOUNTER PER ENVIRONMENT ===")
    for row in env_top_rows:
        print(
            f"{row['environment']:20} | "
            f"top={row['top_pokemon']} | "
            f"share={row['top_share']} | "
            f"candidates={row['candidate_count']}"
        )

    optional_plots(summary_rows, env_top_rows)

    print("\nSaved files:")
    print("- simulation_summary.csv")
    print("- environment_winners.csv")
    print("- environment_summary.csv")


if __name__ == "__main__":
    main()