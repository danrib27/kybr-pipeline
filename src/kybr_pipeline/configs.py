"""Pipeline settings, read once from config.yaml when first imported."""

from pathlib import Path

import humanfriendly
import yaml

with Path("config.yaml").open() as f:
    _config = yaml.safe_load(f)

BASE_URL: str = _config["requests"]["base_url"]
MONTHLY_ENDPOINTS: list[str] = _config["requests"]["endpoints"]["monthly"]
SNAPSHOT_ENDPOINTS: list[str] = _config["requests"]["endpoints"]["snapshot"]
CHUNK_SIZE: int = humanfriendly.parse_size(
    _config["requests"]["chunk_size"]
)
TMP_DIR = Path(_config["requests"]["tmp_dir"])
BUCKET_NAME: str = _config["s3"]["bucket_name"]
