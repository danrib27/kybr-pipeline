from pathlib import Path
from urllib.parse import urlparse

import boto3
import requests
from botocore.exceptions import ClientError, NoCredentialsError


def download_file(
    url: str,
    output_dir: Path,
    chunk_size: int,
    timeout: float = 30,
) -> Path:
    """Download a file from a URL into a directory, keeping its name.

    The portal redirects the request to the zip file, and the name is the
    last part of that final URL. For example, a request to
    `.../download-de-dados/compras/202508` is redirected to
    `.../saida/compras/202508_Compras.zip`, which is saved as
    `202508_Compras.zip`.

    Args:
        url: The URL of the file to download.
        output_dir: The directory where the file will be saved.
        chunk_size: The number of bytes written to disk at a time.
        timeout: Seconds to wait for the server before giving up.

    Returns:
        The path of the saved file.
    """
    response = requests.get(url, stream=True, timeout=timeout)
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
    `AWS_SECRET_ACCESS_KEY`) or from `~/.aws/credentials`.

    Args:
        file_path: The local path of the file to upload.
        bucket_name: The name of the S3 bucket.
        object_name: The name of the object in the S3 bucket.

    Raises:
        RuntimeError: If the credentials are missing or S3 rejects the
            upload.
    """
    s3_client = boto3.client(service_name='s3', region_name='us-east-1')
    try:
        s3_client.upload_file(str(file_path), bucket_name, object_name)
    except (NoCredentialsError, ClientError) as e:
        raise RuntimeError(
            f"Failed to upload {file_path} to s3://{bucket_name}/{object_name}"
        ) from e
