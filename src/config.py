import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    # === PATHS ====================================================================================================== #
    INPUT_DATA_DIR: Path = Path.cwd() / "data" / "input"
    OUTPUT_DATA_DIR: Path = Path.cwd() / "data" / "output"

    OSM_FILE_PATH: Path = INPUT_DATA_DIR / "norway-latest.osm.pbf"

    DOPPA_SCHEMA_PATH: str = "https://doppablobstorage.blob.core.windows.net/schema/latest/schema.yml"

    # === DATA DOWNLOAD ============================================================================================== #
    OSM_PBF_URL: str = "https://download.geofabrik.de/europe/norway-latest.osm.pbf"
    OSM_STREAMING_CHUNK_SIZE: int = 8192

    HUGGING_FACE_API_TOKEN: str = os.getenv("HUGGING_FACE_API_TOKEN")

    HUGGING_FACE_UTM32N_PATHS: tuple[str, ...] = (
        "https://huggingface.co/datasets/kartai/DX_datasett/resolve/main/Geodata/Bergen.zip",
        "https://huggingface.co/datasets/kartai/DX_datasett/resolve/main/Geodata/Kristiansand.zip",
        "https://huggingface.co/datasets/kartai/DX_datasett/resolve/main/Geodata/Sandvika.zip",
        "https://huggingface.co/datasets/kartai/DX_datasett/resolve/main/Geodata/Verdal.zip"
    )

    HUGGING_FACE_UTM33N_PATHS: tuple[str, ...] = (
        "https://huggingface.co/datasets/kartai/DX_datasett/resolve/main/Geodata/Mo_i_Rana.zip",
        "https://huggingface.co/datasets/kartai/DX_datasett/resolve/main/Geodata/Tromsdalen.zip"
    )

    FKB_LAYERS: tuple[str, ...] = (
        "Bygning", "AnnenBygning", "Takkant", "Bygningsdelelinje", "FiktivBygningsavgrensning"
    )
