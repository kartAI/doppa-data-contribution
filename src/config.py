from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    INPUT_DATA_DIR: Path = Path.cwd() / "data" / "input"
    OUTPUT_DATA_DIR: Path = Path.cwd() / "data" / "output"
