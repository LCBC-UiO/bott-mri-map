import geopandas as gp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_DIR = DATA_DIR / "output"
INPUT_DIR = DATA_DIR / "input"

MAP_FILE = INPUT_DIR / "countries" / "ne_10m_admin_0_map_units.shp"
POPULATION_MATRIX_FILE = INPUT_DIR / "population" / "NOR1000M_POP_2019.csv"
MATRIX_DEFINITION_FILE = INPUT_DIR / "ruter" / "rute_1000m_Norge.shp"
ISOCHRONES_FILE = OUTPUT_DIR / "isochrones.shp"
POPULATION_MERGED = OUTPUT_DIR / "population.shp"


def load_data():
    # Load population data
    pop_gdf = gp.read_file(POPULATION_MERGED)

    # Load isochrones
    ic = gp.read_file(ISOCHRONES_FILE)
    ic = ic.to_crs(pop_gdf.crs)

    categories = [30, 60, 90, 120]
    ic["time"] = pd.Categorical(ic["time"], categories=categories, ordered=True)
    ic = ic[ic["time"].isin([30, 60, 90, 120])]

    # Load base map of Norway
    countries = gp.read_file(MAP_FILE)
    norway = countries[
        (countries["SOVEREIGNT"] == "Norway") & (countries["TYPE"] == "Country")
    ]
    norway = norway.to_crs(pop_gdf.crs)

    return pop_gdf, ic, norway


def compute_population_within_isochrones(isochrones_gdf, pop_gdf, times):
    pop_sums = {}

    for time in times:
        # Filter the isochrones by the given time
        iso_time = isochrones_gdf[isochrones_gdf["time"] == time]

        # Perform a spatial join with the population data
        joined = gp.sjoin(iso_time, pop_gdf, how="inner", predicate="intersects")

        # Sum the population within this isochrone
        total_pop = joined["pop_tot"].sum()

        pop_sums[time] = total_pop

    return pop_sums


def plot_norway_outline(norway, ic, pop_totals):
    fig, ax = plt.subplots(figsize=(10, 10))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    norway.boundary.plot(ax=ax, color="black", linewidth=0.5)

    # Plot isochrones without legend first
    ic.plot(
        ax=ax, alpha=0.6, linewidth=0, categorical=True, cmap="viridis", column="time"
    )

    # Create custom legend labels based on travel times and the associated population
    colors = plt.cm.viridis(np.linspace(0, 1, len(pop_totals)))
    legend_elements = [
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor=color,
            markersize=10,
            label=f"{time} mins ({pop_totals[time] / 1_000_000:.3f} M people)",
        )
        for time, color in zip(pop_totals.keys(), colors)
    ]

    # Add the custom legend to the plot
    ax.legend(
        handles=legend_elements, title="Travel Time and Population", loc="lower right"
    )

    ax.set_axis_off()
    plt.savefig(OUTPUT_DIR / "norway_map_with_isochrones.png", dpi=300)
    plt.show()


def main():
    # Load population data
    pop_gdf, ic, norway = load_data()

    # Compute population within isochrones
    times = [30, 60, 90, 120]
    pop_totals = compute_population_within_isochrones(ic, pop_gdf, times)

    # Plot the map
    plot_norway_outline(norway, ic, pop_totals)


if __name__ == "__main__":
    main()
