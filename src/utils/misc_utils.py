import geopandas as gpd
import pandas as pd


def cast_to_string(df: pd.DataFrame | gpd.GeoDataFrame) -> pd.DataFrame | gpd.GeoDataFrame:
    for col in df.columns:
        if df[col].dtype == "object" and col != "geometry":
            df[col] = df[col].astype(str)

    return df
