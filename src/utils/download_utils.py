import logging
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import requests

from src import Config


def download_fgb_zip_file(path: str) -> bytes:
    headers = {"Authorization": f"Bearer {Config.HUGGING_FACE_API_TOKEN}"}
    response = requests.get(path, headers=headers, stream=True)
    response.raise_for_status()

    return response.content


def download_osm_pbf_file() -> None:
    if Config.OSM_FILE_PATH.is_file():
        logging.info("OSM-data have already been downloaded. Skipping download...")
        return

    logging.info(f"Downloading OSM-data from '{Config.OSM_PBF_URL}'")
    response = requests.get(Config.OSM_PBF_URL, stream=True)
    response.raise_for_status()

    with open(Config.OSM_FILE_PATH, "wb") as f:
        chunks = response.iter_content(chunk_size=Config.OSM_STREAMING_CHUNK_SIZE)
        for chunk in chunks:
            f.write(chunk)


def download_kommune_geojson_file(zip_url: str, target_path: Path) -> None:
    if target_path.is_file():
        logging.info("Kommune GeoJSON already downloaded. Skipping download...")
        return

    logging.info(f"Downloading kommune GeoJSON from '{zip_url}'")
    response = requests.get(zip_url, stream=True)
    response.raise_for_status()

    with ZipFile(BytesIO(response.content)) as zip_file:
        geojson_members = [name for name in zip_file.namelist() if name.lower().endswith(".geojson")]
        if not geojson_members:
            raise ValueError(f"No .geojson file found inside archive at '{zip_url}'")

        geojson_member = geojson_members[0]
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with zip_file.open(geojson_member) as src, open(target_path, "wb") as dst:
            dst.write(src.read())
