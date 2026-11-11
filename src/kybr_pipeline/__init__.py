import logging
import time
from pathlib import Path
from tempfile import TemporaryDirectory

import humanfriendly

from kybr_pipeline import configs
from kybr_pipeline.transfer import download_file, upload_2_s3

logger = logging.getLogger(__name__)


class Pipeline:
    """Pipeline that downloads the source data and loads it.

    The settings come from `kybr_pipeline.configs`.
    """

    def ingest(self, endpoint: str, ref: str) -> None:
        """Download one open data set and upload it to S3.

        The file goes to its own temporary directory inside `TMP_DIR`,
        removed at the end, so runs in parallel don't touch each other's
        files.

        Logs one INFO line per reference with the URL, the file name and
        size, the S3 object and the elapsed time.

        Args:
            endpoint: The open data set, one of `configs.MONTHLY_ENDPOINTS`
                or `configs.SNAPSHOT_ENDPOINTS`.
            ref: The reference, as 'YYYYMM' or 'YYYYMMDD'.
        """
        url = f"{configs.BASE_URL}/{endpoint}/{ref}"

        start = time.perf_counter()
        configs.TMP_DIR.mkdir(parents=True, exist_ok=True)

        with TemporaryDirectory(dir=configs.TMP_DIR) as run_dir:
            output_path = download_file(url, Path(run_dir), configs.CHUNK_SIZE)
            size = humanfriendly.format_size(output_path.stat().st_size)
            logger.debug(
                "Downloaded %s (%s) in %.1fs",
                output_path.name,
                size,
                time.perf_counter() - start,
            )

            object_name = f"raw/{endpoint}/{output_path.name}"

            upload_2_s3(output_path, configs.BUCKET_NAME, object_name)

        logger.info(
            "%s %s: %s -> %s (%s) -> s3://%s/%s in %.1fs",
            endpoint,
            ref,
            url,
            output_path.name,
            size,
            configs.BUCKET_NAME,
            object_name,
            time.perf_counter() - start,
        )
