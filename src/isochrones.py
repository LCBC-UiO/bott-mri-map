import geopandas as gp
import pandas as pd
from shapely.geometry import Polygon
from routingpy.routers import Valhalla
import numpy as np
from pathlib import Path
import os

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_DIR = DATA_DIR / "output"


def create_dataframe():
    data = {
        "City": ["Oslo", "Bergen", "Trondheim", "Tromsø"],
        "LAT_VALUE": [
            59.94325569843703,
            60.373620086371766,
            63.42115156339022,
            69.68334764603148,
        ],
        "LON_VALUE": [
            10.713583958247312,
            5.357896567780437,
            10.388075242832075,
            18.986223899373528,
        ],
    }
    gdf = gp.GeoDataFrame(
        data,
        geometry=gp.points_from_xy(data["LON_VALUE"], data["LAT_VALUE"]),
        crs="EPSG:4326",
    )
    return gdf


def valhalla_isochrone(client, gdf, time=[60], profile="driving"):
    gdf["LON_VALUE"] = gdf.to_crs(4326).geometry.x
    gdf["LAT_VALUE"] = gdf.to_crs(4326).geometry.y

    coordinates = gdf[["LON_VALUE", "LAT_VALUE"]].values.tolist()
    isochrone_shapes = []

    if type(time) is not list:
        time = [time]

    time_seconds = [60 * x for x in time]

    for c in coordinates:
        iso_request = client.isochrones(
            locations=c, profile=profile, intervals=time_seconds
        )
        for i in iso_request:
            iso_geom = Polygon(i.geometry)
            isochrone_shapes.append(iso_geom)

    df_values = gdf.drop(columns=["geometry", "LON_VALUE", "LAT_VALUE"])
    time_col = time * len(df_values)
    df_values_rep = pd.DataFrame(np.repeat(df_values.values, len(time_seconds), axis=0))
    df_values_rep.columns = df_values.columns
    isochrone_gdf = gp.GeoDataFrame(
        data=df_values_rep, geometry=isochrone_shapes, crs=4326
    )
    isochrone_gdf["time"] = time_col
    isochrone_gdf = isochrone_gdf.sort_values("time", ascending=False)
    return isochrone_gdf


def main():
    gdf = create_dataframe()
    client = Valhalla(base_url="http://0.0.0.0:8002")
    isochrones = valhalla_isochrone(client, gdf, time=[30, 60, 90, 120], profile="auto")

    # Ensure the output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    isochrones.to_file(OUTPUT_DIR / "isochrones.shp")


if __name__ == "__main__":
    main()
