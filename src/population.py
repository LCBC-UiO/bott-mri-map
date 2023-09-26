from pathlib import Path
import geopandas as gp
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_DIR = DATA_DIR / "output"
INPUT_DIR = DATA_DIR / "input"

POPULATION_MATRIX_FILE = INPUT_DIR / "population" / "NOR1000M_POP_2019.csv"
MATRIX_DEFINITION_FILE = INPUT_DIR / "ruter" / "rute_1000m_Norge.shp"


def load_and_merge_data():
    gdf_boxes = gp.read_file(MATRIX_DEFINITION_FILE)
    df_population = pd.read_csv(POPULATION_MATRIX_FILE, sep=";")

    # Convert the merging column to the correct type and then merge
    gdf_boxes["SSBid"] = gdf_boxes["SSBid"].astype(int)

    # Merge
    return gdf_boxes.merge(
        df_population, left_on="SSBid", right_on="SSBID1000M", how="left"
    )


def save_to_file(dataframe):
    dataframe.to_file(OUTPUT_DIR / "population.shp")


def main():
    merged_gdf = load_and_merge_data()
    save_to_file(merged_gdf)


if __name__ == "__main__":
    main()
