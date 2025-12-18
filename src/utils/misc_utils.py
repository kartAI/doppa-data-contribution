import geopandas as gpd
import pandas as pd


def cast_to_string(df: pd.DataFrame | gpd.GeoDataFrame) -> pd.DataFrame | gpd.GeoDataFrame:
    for col in df.columns:
        if df[col].dtype == "object" and col != "geometry":
            df[col] = df[col].astype(str)

    return df


def make_unique_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = []
    seen = {}
    for col in df.columns:
        name = str(col)
        if name in seen:
            seen[name] += 1
            cols.append(f"{name}_{seen[name]}")
        else:
            seen[name] = 0
            cols.append(name)
    df = df.copy()
    df.columns = cols
    return df
