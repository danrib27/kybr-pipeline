import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
import requests
from botocore.exceptions import ClientError, NoCredentialsError

from kybr_pipeline import transfer

# Larger than the chunk size the tests use, so it takes many chunks.
CONTENT = bytes(range(256)) * 40
SLOW_SECONDS = 0.5


class PortalHandler(BaseHTTPRequestHandler):
    """Serves the routes of a small fake portal.

    - `/download-de-dados/compras/202508` redirects to the zip file.
    - `/saida/compras/202508_Compras.zip` serves `CONTENT`.
    - `/slow` waits `SLOW_SECONDS` before it answers.
    - any other path answers 404.
    """

    def do_GET(self):
        if self.path == "/download-de-dados/compras/202508":
            self.send_response(HTTPStatus.FOUND)
            self.send_header("Location", "/saida/compras/202508_Compras.zip")
            self.end_headers()

        elif self.path == "/saida/compras/202508_Compras.zip":
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Length", str(len(CONTENT)))
            self.end_headers()
            self.wfile.write(CONTENT)

        elif self.path == "/slow":
            time.sleep(SLOW_SECONDS)
            self.send_response(HTTPStatus.OK)
            self.end_headers()

        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def log_message(self, format, *args):  # noqa: A002
        """Keep the test output clean."""


@pytest.fixture(scope="module")
def portal_url():
    """Start the fake portal on a free local port and give its base URL.

    The server runs in a thread for the whole module and is shut down
    after the last test.
    """
    server = ThreadingHTTPServer(("127.0.0.1", 0), PortalHandler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    yield f"http://{host}:{port}"
    server.shutdown()
    server.server_close()


def test_download_file_follows_the_redirect_and_keeps_its_name(
    portal_url, tmp_path
):
    """The file is saved under the name of the URL it redirects to.

    Checks that:
    - the name comes from the final URL (`202508_Compras.zip`), not
      from the requested one (`202508`);
    - the content, larger than the chunk size, arrives intact;
    - nothing else is written to the directory.
    """
    url = f"{portal_url}/download-de-dados/compras/202508"

    output_path = transfer.download_file(url, tmp_path, chunk_size=100)

    assert output_path == tmp_path / "202508_Compras.zip"
    assert output_path.read_bytes() == CONTENT
    assert list(tmp_path.iterdir()) == [output_path]


def test_download_file_raises_on_an_http_error(portal_url, tmp_path):
    """A reference the portal doesn't have fails before writing a file.

    Checks that:
    - `requests.HTTPError` is raised, carrying the 404 response that
      `scripts.ingest_snapshot` reads to fall back to yesterday;
    - no partial file is left in the directory.
    """
    url = f"{portal_url}/download-de-dados/compras/209901"

    with pytest.raises(requests.HTTPError) as excinfo:
        transfer.download_file(url, tmp_path, chunk_size=100)

    response = excinfo.value.response
    assert response is not None
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert list(tmp_path.iterdir()) == []


def test_download_file_gives_up_after_the_timeout(portal_url, tmp_path):
    """A server slower than `timeout` makes the download give up.

    Checks that the `timeout` argument reaches `requests`, which raises
    `requests.Timeout`, and that no file is left in the directory.
    """
    with pytest.raises(requests.Timeout):
        transfer.download_file(
            f"{portal_url}/slow", tmp_path, chunk_size=100, timeout=0.05
        )

    assert list(tmp_path.iterdir()) == []


class FakeS3Client:
    """Records the `upload_file` calls, or raises `error`."""

    def __init__(self, error=None):
        self.error = error
        self.uploads: list[tuple[str, str, str]] = []

    def upload_file(self, filename, bucket, key):
        if self.error is not None:
            raise self.error

        self.uploads.append((filename, bucket, key))


@pytest.fixture
def s3(monkeypatch):
    """Replace `boto3.client` with one that returns a `FakeS3Client`.

    Gives the fake client and the keyword arguments of every
    `boto3.client` call.
    """
    client = FakeS3Client()
    clients = []

    def fake_client(**kwargs):
        clients.append(kwargs)
        return client

    monkeypatch.setattr(transfer.boto3, "client", fake_client)
    return client, clients


def test_upload_2_s3_uploads_the_file(s3):
    """The file goes to the given bucket under the given name.

    Checks that:
    - the S3 client is created without a fixed region, so boto3 reads
      it from `AWS_REGION`;
    - `upload_file` gets the path as a string, the bucket and the key.
    """
    client, clients = s3

    transfer.upload_2_s3(Path("/data/a.zip"), "bucket", "key.zip")

    assert clients == [{"service_name": "s3"}]
    assert client.uploads == [("/data/a.zip", "bucket", "key.zip")]


@pytest.mark.parametrize(
    "error",
    [
        NoCredentialsError(),
        ClientError(
            {"Error": {"Code": "NoSuchBucket", "Message": "no bucket"}},
            "PutObject",
        ),
    ],
    ids=["no credentials", "client error"],
)
def test_upload_2_s3_wraps_credential_and_s3_errors(s3, error):
    """Missing credentials and S3 errors become a `RuntimeError`.

    Checks that:
    - the message names the file and its `s3://` destination;
    - the original error is kept as the cause, for debugging.
    """
    client, _ = s3
    client.error = error

    with pytest.raises(RuntimeError) as excinfo:
        transfer.upload_2_s3(Path("/data/a.zip"), "bucket", "key.zip")

    assert str(excinfo.value) == (
        "Failed to upload /data/a.zip to s3://bucket/key.zip"
    )
    assert excinfo.value.__cause__ is error


def test_upload_2_s3_lets_other_errors_through(s3):
    """Errors other than credentials or S3 ones are not wrapped.

    Checks that a `FileNotFoundError` reaches the caller as it is, so
    `upload_2_s3` doesn't hide unexpected errors behind a generic
    `RuntimeError`.
    """
    client, _ = s3
    client.error = FileNotFoundError("/data/a.zip")

    with pytest.raises(FileNotFoundError):
        transfer.upload_2_s3(Path("/data/a.zip"), "bucket", "key.zip")
