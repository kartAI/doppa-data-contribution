# doppa-data-contribution

doppa-data-contribution is the **data-publishing stage** of the doppa benchmarking system. It is a set of
Jupyter notebooks that download raw Norwegian building footprints and administrative boundaries from public
sources, normalize them to a shared GeoParquet schema, and upload the result to Azure Blob Storage. The
[doppa](https://github.com/kartAI/doppa) benchmarking framework consumes these published datasets as its
inputs.

Keeping data preparation in a separate repository means the benchmark framework never has to re-derive its
inputs: every engine under test (DuckDB, PostGIS, GeoPandas + Shapefile, Apache Sedona) reads the exact same
bytes, written once here and conflated/synthesized downstream into the small/medium/large tiers.

## The doppa ecosystem

The thesis (TBA4925, NTNU Geomatics) — benchmarking cloud-native versus traditional geospatial technologies on
Azure — spans three repositories that depend on each other in a pipeline:

```
doppa-data-contribution  ──►  doppa  ──►  doppa-analytics
   (this repo)               (benchmarks)   (stats + figures)
   publish datasets          run engines    read results, build
   to blob storage           write metrics  thesis figures/tables
```

| Repository | Role | Link |
|------------|------|------|
| **doppa-data-contribution** | Downloads and normalizes source datasets; publishes GeoParquet to blob storage *(this repo)* | — |
| **doppa** | Reproducible benchmarking framework. Consumes the published datasets, runs the spatial-query benchmarks on Azure, writes per-iteration samples and cost rows back to blob storage | [kartAI/doppa](https://github.com/kartAI/doppa) |
| **doppa-analytics** | Reads the benchmark result Parquet, runs the statistical tests, and generates the thesis figures and LaTeX tables | [kartAI/doppa-analytics](https://github.com/kartAI/doppa-analytics) |

## Table of contents

- [Datasets and notebooks](#datasets-and-notebooks)
- [Output](#output)
    - [Shared schema](#shared-schema)
    - [Blob storage layout](#blob-storage-layout)
    - [How doppa consumes the output](#how-doppa-consumes-the-output)
- [Setup](#setup)
    - [Local development](#local-development)
    - [Environment variables](#environment-variables)
- [Running the notebooks](#running-the-notebooks)
- [Data sources](#data-sources)

## Datasets and notebooks

Each notebook is an independent contribution: download → normalize to the schema → upload one Parquet blob.
They can be run in any order, and each is idempotent (the upload overwrites the existing blob).

| Notebook | Dataset | Source | Output blob |
|----------|---------|--------|-------------|
| `01-osm-contribution.ipynb` | OpenStreetMap building footprints (Norway) | [Geofabrik](https://download.geofabrik.de/europe/norway.html) `norway-latest.osm.pbf` | `osm.parquet` |
| `02-fkb-contribution.ipynb` | FKB cadastral building polygons (selected Norwegian cities) | [kartai/DX_datasett](https://huggingface.co/datasets/kartai/DX_datasett) on Hugging Face (FlatGeobuf) | `fkb.parquet` |
| `03-microsoft-buildings-contribution.ipynb` | Microsoft Global ML Building Footprints (Norway) | [Microsoft GlobalMLBuildingFootprints](https://github.com/microsoft/GlobalMLBuildingFootprints) | `microsoft.parquet` |
| `04-kommuner-contribution.ipynb` | Norwegian municipality polygons (357 features) | [Administrative enheter — kommuner (Geonorge)](https://kartkatalog.geonorge.no/metadata/administrative-enheter-kommuner/041f1e6e-bdbc-4091-b48f-8a5990f3cc5b) | `municipalities.parquet` |

**OSM** (`01`) streams the national PBF extract, keeps the building features and a fixed set of attribute
columns (`OSM_COLUMNS_TO_KEEP` in `src/config.py`), and processes them in batches
(`OSM_FEATURE_BATCH_SIZE`) to keep memory bounded.

**FKB** (`02`) downloads per-city FlatGeobuf archives, unzips the relevant building layers (`Bygning`,
`AnnenBygning`, `Takkant`, `Bygningsdelelinje`, `FiktivBygningsavgrensning`), and reconstructs closed
building polygons from the edge layers with DuckDB's `ST_Polygonize`.

**Microsoft Buildings** (`03`) reads the `dataset-links.csv` index, filters to the Norway tiles, and converts
the newline-delimited GeoJSON to Parquet via DuckDB, deriving a stable `external_id` as the MD5 of the geometry.

**Kommuner** (`04`) downloads the municipality GeoJSON from Geonorge, strips the UTF-8 BOM before handing the
bytes to GeoPandas, and writes `region` (kommunenummer), `name` (kommunenavn), and `wkb` (geometry as WKB).
The `region` column mirrors `counties.parquet` in doppa so the spatial-join entrypoints need no schema changes.

## Output

### Shared schema

All building contributions conform to the doppa schema published at
`https://doppablobstorage.blob.core.windows.net/schema/latest/schema.yml` (`DOPPA_SCHEMA_PATH` in
`src/config.py`). The data owner is free to carry extra attributes as long as the required schema columns are
present, so OSM/FKB/Microsoft can each preserve source-specific fields while remaining conflatable downstream.

### Blob storage layout

Every notebook uploads its Parquet to the **`contributions`** container of the configured storage account, named
after the dataset (`osm.parquet`, `fkb.parquet`, `microsoft.parquet`, `municipalities.parquet`). Uploads use
`overwrite=True`, so re-running a notebook republishes that dataset in place.

### How doppa consumes the output

- **Building footprints** — doppa's `TestDatasetService` conflates the OSM and FKB contributions into the
  `small` (~5M row) benchmark dataset, then `DatasetSynthesisService` clones it into the `medium` (~40M) and
  `large` (~100M) tiers.
- **Municipality boundaries** — doppa's `setup_benchmarking_framework` copies `municipalities.parquet` from
  `contributions` to the `metadata` container, where the RQ2 national-scale spatial join reads it. Running
  `04-kommuner-contribution` once is a prerequisite for that benchmark; if the blob is missing the doppa setup
  step fails fast with an actionable error pointing back here.

## Setup

### Local development

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/kartAI/doppa-data-contribution.git
cd doppa-data-contribution

python -m venv .venv                         # Create virtual environment
source .venv/bin/activate                    # Activate venv (Linux/macOS)
# .\.venv\Scripts\Activate.ps1               # Activate venv (Windows PowerShell)
pip install -r requirements.txt              # Install dependencies
```

### Environment variables

Add a `.env` file to the project root. The contribution targets the same storage account that doppa
benchmarks against.

```dotenv
AZURE_BLOB_STORAGE_CONNECTION_STRING=<azure-blob-storage-connection-string>
HUGGING_FACE_API_TOKEN=<hugging-face-api-token>
```

- `AZURE_BLOB_STORAGE_CONNECTION_STRING` — connection string for the storage account that owns the
  `contributions` container.
- `HUGGING_FACE_API_TOKEN` — token for the `kartai/DX_datasett` Hugging Face dataset used by the FKB notebook.

## Running the notebooks

Launch Jupyter (or run a single notebook headless) and execute the cells top to bottom:

```bash
jupyter lab                                  # interactive
# or run one notebook end to end:
jupyter execute 04-kommuner-contribution.ipynb
```

Each notebook downloads its source into `data/input/`, writes the normalized Parquet to `data/output/`, and
then uploads it to the `contributions` blob container.

## Data sources

- OpenStreetMap — Norway extract via [Geofabrik](https://download.geofabrik.de/europe/norway.html).
  © OpenStreetMap contributors, [ODbL](https://www.openstreetmap.org/copyright).
- FKB building data — [kartai/DX_datasett](https://huggingface.co/datasets/kartai/DX_datasett) (Kartverket FKB,
  redistributed for the DX project).
- Microsoft Global ML Building Footprints —
  [microsoft/GlobalMLBuildingFootprints](https://github.com/microsoft/GlobalMLBuildingFootprints) (ODbL).
- Administrative units (municipalities) —
  [Geonorge](https://kartkatalog.geonorge.no/metadata/administrative-enheter-kommuner/041f1e6e-bdbc-4091-b48f-8a5990f3cc5b),
  Kartverket (NLOD / CC BY 4.0).
