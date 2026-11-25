"""Pipeline settings, read once from config.yaml when first imported.

The file is `config.yaml` in the current directory, unless the
`KYBR_PIPELINE_CONFIG` environment variable gives another path.
"""

import os
from pathlib import Path
from typing import TypedDict

import humanfriendly
import yaml


class Column(TypedDict):
    """A column of a bronze table, as in docs/data/."""

    name: str
    bronze_name: str
    type: str


class Table(TypedDict):
    """A bronze table: one CSV file inside a data set's zip."""

    name: str
    columns: list[Column]


CONFIG_PATH = Path(os.environ.get("KYBR_PIPELINE_CONFIG", "config.yaml"))

with CONFIG_PATH.open() as f:
    _config = yaml.safe_load(f)

BASE_URL: str = _config["requests"]["base_url"]
MONTHLY_ENDPOINTS: list[str] = _config["requests"]["endpoints"]["monthly"]
SNAPSHOT_ENDPOINTS: list[str] = _config["requests"]["endpoints"]["snapshot"]
CHUNK_SIZE: int = humanfriendly.parse_size(_config["requests"]["chunk_size"])
TMP_DIR = Path(_config["requests"]["tmp_dir"])
BUCKET_NAME: str = _config["s3"]["bucket_name"]
COMPRAS_SCHEMAS: list[Table] = _config["schemas"]["compras"]
LICITACOES_SCHEMAS: list[Table] = _config["schemas"]["licitacoes"]
CEIS_SCHEMAS: list[Table] = _config["schemas"]["ceis"]
CNEP_SCHEMAS: list[Table] = _config["schemas"]["cnep"]
