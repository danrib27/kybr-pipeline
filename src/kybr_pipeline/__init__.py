from pathlib import Path
from tempfile import TemporaryDirectory

import humanfriendly
import yaml

from kybr_pipeline.cli import parse_args
from kybr_pipeline.ingest import download_file, upload_2_s3


class Pipeline:
    """Pipeline that downloads the source data and loads it.

    Args:
        env: The environment for the pipeline.
    """

    def __init__(self, ) -> None:
        with Path('config.yaml').open() as f:
            self.config = yaml.safe_load(f)

        self.base_url = self.config['requests']['base_url']
        self.endpoints = {
            endpoint: f'{self.config['requests']['base_url']}/{endpoint}'
            for endpoint in self.config['requests']['endpoints']
        }
        self.chunk_size = humanfriendly.parse_size(
            self.config['requests']['chunk_size']
        )
        self.tmp_dir = self.config['requests']['tmp_dir']
        self.bucket_name = self.config['s3']['bucket_name']

    def ingest(self, endpoint: str, ref: str) -> None:
        """Download one open data set and upload it to S3.

        The file goes to its own temporary directory inside `tmp_dir`,
        removed at the end, so runs in parallel don't touch each other's
        files.

        Args:
            endpoint: The open data set, one of the endpoints in
                config.yaml.
            ref: The reference, as 'YYYYMM' or 'YYYYMMDD'.
        """
        url = f'{self.endpoints[endpoint]}/{ref}'

        Path(self.tmp_dir).mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(dir=self.tmp_dir) as run_dir:
            output_path = download_file(url, Path(run_dir), self.chunk_size)
            upload_2_s3(output_path, self.bucket_name, output_path.name)

    def etl(self) -> None:
        """Extract, transform and load the downloaded data.

        Extract data from the temporary location, transform it, and load it
        into the database.
        """


def main() -> None:
    """Run the `kybr-pipeline` command typed on the command line."""
    pipeline = Pipeline()
    args = parse_args(list(pipeline.endpoints))
    pipeline.ingest(args.endpoint, args.ref)
