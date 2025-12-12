import geopandas as gpd
import pandas as pd


def convert_fgb_bytes_to_gdf(
        layers: list[bytes],
        crs_in: int,
        crs_out: int
) -> gpd.GeoDataFrame:
    geo_dataframes: list[gpd.GeoDataFrame] = []
    for layer in layers:
        gdf = gpd.read_file(layer, engine="pyogrio")
        geo_dataframes.append(gdf)

    combined_gdf = gpd.GeoDataFrame(pd.concat(geo_dataframes, ignore_index=True), crs=crs_in)
    if crs_in != crs_out:
        combined_gdf = combined_gdf.to_crs(crs_out)

    return combined_gdf
