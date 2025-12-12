import logging

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
