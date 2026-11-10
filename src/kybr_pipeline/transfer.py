from pathlib import Path
from urllib.parse import urlparse

import boto3
import requests
from botocore.exceptions import ClientError, NoCredentialsError
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# Status of transient portal errors, worth another try.
RETRY_STATUS = frozenset({429, 500, 502, 503, 504})


def retry_session(retries: int, backoff_factor: float) -> requests.Session:
    """Build a session that retries transient errors with backoff.

    Connection errors, timeouts and the status in `RETRY_STATUS` are
    retried, waiting `backoff_factor * 2 ** (n - 1)` seconds before the
    n-th retry, or what the `Retry-After` header asks. Other errors,
    such as 403 and 404, are not retried.

    Args:
        retries: The number of retries after the first try.
        backoff_factor: The base, in seconds, of the exponential wait.

    Returns:
        A session that applies the retries to HTTP and HTTPS URLs.
    """
    retry = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=RETRY_STATUS,
        allowed_methods=frozenset({"GET"}),
        # Give back the last response, so the caller gets an HTTPError.
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def download_file(
    url: str,
    output_dir: Path,
    chunk_size: int,
    timeout: float = 30,
    retries: int = 5,
    backoff_factor: float = 1,
) -> Path:
    """Download a file from a URL into a directory, keeping its name.

    The portal redirects the request to the zip file, and the name is the
    last part of that final URL. For example, a request to
    `.../download-de-dados/compras/202508` is redirected to
    `.../saida/compras/202508_Compras.zip`, which is saved as
    `202508_Compras.zip`.

    Transient errors are retried with exponential backoff (see
    `retry_session`), so a temporary portal failure doesn't stop a
    backfill. A 403 or 404 fails at once.

    Args:
        url: The URL of the file to download.
        output_dir: The directory where the file will be saved.
        chunk_size: The number of bytes written to disk at a time.
        timeout: Seconds to wait for the server before giving up.
        retries: The number of retries after the first try.
        backoff_factor: The base, in seconds, of the wait between
            retries.

    Returns:
        The path of the saved file.

    Raises:
        requests.HTTPError: If the server answers with an error status,
            at once or after the last retry.
        requests.ConnectionError: If the server can't be reached or
            keeps timing out after the last retry.
    """
    with (
        retry_session(retries, backoff_factor) as session,
        session.get(url, stream=True, timeout=timeout) as response,
    ):
        response.raise_for_status()

        # File name from the final URL, after the redirect.
        output_path = output_dir / Path(urlparse(response.url).path).name
        with output_path.open("wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                f.write(chunk)

    return output_path


def upload_2_s3(file_path: Path, bucket_name: str, object_name: str) -> None:
    """Upload a file to an S3 bucket.

    The credentials come from the environment (`AWS_ACCESS_KEY_ID` and
    `AWS_SECRET_ACCESS_KEY`) or from `~/.aws/credentials`, and the
    region from `AWS_REGION`.

    Args:
        file_path: The local path of the file to upload.
        bucket_name: The name of the S3 bucket.
        object_name: The name of the object in the S3 bucket.

    Raises:
        RuntimeError: If the credentials are missing or S3 rejects the
            upload.
    """
    s3_client = boto3.client(service_name="s3")
    try:
        s3_client.upload_file(str(file_path), bucket_name, object_name)
    except (NoCredentialsError, ClientError) as e:
        raise RuntimeError(
            f"Failed to upload {file_path} to s3://{bucket_name}/{object_name}"
        ) from e
