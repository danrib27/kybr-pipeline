from pathlib import Path
from tempfile import TemporaryDirectory

from kybr_pipeline import configs
from kybr_pipeline.transfer import download_file, upload_2_s3


class Pipeline:
    """Pipeline that downloads the source data and loads it.

    The settings come from `kybr_pipeline.configs`.
    """

    def ingest(self, endpoint: str, ref: str) -> None:
        """Download one open data set and upload it to S3.

        The file goes to its own temporary directory inside `TMP_DIR`,
        removed at the end, so runs in parallel don't touch each other's
        files.

        Args:
            endpoint: The open data set, one of `configs.MONTHLY_ENDPOINTS`
                or `configs.SNAPSHOT_ENDPOINTS`.
            ref: The reference, as 'YYYYMM' or 'YYYYMMDD'.
        """
        url = f'{configs.BASE_URL}/{endpoint}/{ref}'

        configs.TMP_DIR.mkdir(parents=True, exist_ok=True)

        with TemporaryDirectory(dir=configs.TMP_DIR) as run_dir:
            output_path = download_file(url, Path(run_dir), configs.CHUNK_SIZE)
            upload_2_s3(output_path, configs.BUCKET_NAME, output_path.name)

    def etl(self) -> None:
        """Extract, transform and load the downloaded data.

        Extract data from the temporary location, transform it, and load it
        into the database.
        """
