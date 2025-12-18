from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from azure.storage.blob import BlobServiceClient


def unzip_flat_geobuf(data: bytes, *layers: str) -> list[bytes]:
    data = BytesIO(data)
    layer_bytes: list[bytes] = []
    with ZipFile(data) as zip_file:
        if len(layers) == 0:
            layer_paths = [f for f in zip_file.namelist() if f.endswith(f".fgb")]
            for layer_path in layer_paths:
                with zip_file.open(layer_path) as f:
                    current_layer_bytes = f.read()
                    layer_bytes.append(current_layer_bytes)
        else:
            for layer in layers:
                layer_name = f"fgb/{layer}.fgb"
                layer_path_matches = [f for f in zip_file.namelist() if f.endswith(layer_name)]
                if len(layer_path_matches) == 0:
                    raise ValueError(f"'{layer}' not found in the file")

                layer_path = layer_path_matches[0]
                with zip_file.open(layer_path) as f:
                    current_layer_bytes = f.read()
                    layer_bytes.append(current_layer_bytes)

    return layer_bytes


def upload_parquet_to_container(
        blob_service_client: BlobServiceClient,
        parquet_path: str | Path,
        blob_name: str | None,
        container_name: str,
) -> None:
    parquet_path = Path(parquet_path)

    if not parquet_path.exists():
        raise FileNotFoundError(f"Parquet file not found: {parquet_path}")

    if blob_name is None:
        blob_name = parquet_path.name

    container_client = blob_service_client.get_container_client(container_name)

    with parquet_path.open("rb") as f:
        container_client.upload_blob(
            name=blob_name,
            data=f,
            overwrite=True,
        )
