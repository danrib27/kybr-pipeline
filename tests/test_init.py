import logging
import re
from pathlib import Path

import pytest
import requests

import kybr_pipeline
from kybr_pipeline import Pipeline, configs


class FakeTransfer:
    """Stands in for `download_file` and `upload_2_s3`.

    `download_file` writes a file named like the portal's zip into the
    directory it gets, so the test can check where it went and that it
    is gone at the end.
    """

    def __init__(self):
        self.downloads: list[tuple[str, Path, int]] = []
        self.uploads: list[tuple[Path, str, str, bool]] = []
        self.download_error: Exception | None = None
        self.upload_error: Exception | None = None

    def download_file(self, url, output_dir, chunk_size):
        self.downloads.append((url, output_dir, chunk_size))
        if self.download_error is not None:
            raise self.download_error

        output_path = output_dir / "202508_Compras.zip"
        output_path.write_bytes(b"zip")
        return output_path

    def upload_2_s3(self, file_path, bucket_name, object_name):
        self.uploads.append(
            (file_path, bucket_name, object_name, file_path.is_file())
        )
        if self.upload_error is not None:
            raise self.upload_error


@pytest.fixture
def tmp_dir(monkeypatch, tmp_path):
    path = tmp_path / "kybr_pipeline"
    monkeypatch.setattr(configs, "TMP_DIR", path)
    return path


@pytest.fixture
def transfer(monkeypatch):
    fake = FakeTransfer()
    monkeypatch.setattr(kybr_pipeline, "download_file", fake.download_file)
    monkeypatch.setattr(kybr_pipeline, "upload_2_s3", fake.upload_2_s3)
    return fake


def test_ingest_downloads_the_file_and_uploads_it_to_s3(tmp_dir, transfer):
    """Default behavior: download into a run directory, upload, clean up."""
    Pipeline().ingest("compras", "202508")

    [(url, run_dir, chunk_size)] = transfer.downloads
    assert url == f"{configs.BASE_URL}/compras/202508"
    assert run_dir.parent == tmp_dir
    assert chunk_size == configs.CHUNK_SIZE

    assert transfer.uploads == [
        (
            run_dir / "202508_Compras.zip",
            configs.BUCKET_NAME,
            "raw/compras/202508_Compras.zip",
            True,
        )
    ]
    assert list(tmp_dir.iterdir()) == []


@pytest.mark.usefixtures("tmp_dir")
def test_ingest_uses_a_new_run_directory_each_time(transfer):
    Pipeline().ingest("compras", "202508")
    Pipeline().ingest("compras", "202508")

    first, second = (run_dir for _, run_dir, _ in transfer.downloads)
    assert first != second


def test_ingest_does_not_upload_when_the_download_fails(tmp_dir, transfer):
    transfer.download_error = requests.HTTPError("404 Not Found")

    with pytest.raises(requests.HTTPError):
        Pipeline().ingest("compras", "202508")

    assert transfer.uploads == []
    assert list(tmp_dir.iterdir()) == []


def test_ingest_cleans_up_when_the_upload_fails(tmp_dir, transfer):
    transfer.upload_error = RuntimeError("upload failed")

    with pytest.raises(RuntimeError, match="upload failed"):
        Pipeline().ingest("compras", "202508")

    assert list(tmp_dir.iterdir()) == []


def test_ingest_logs_one_line_with_the_result(tmp_dir, transfer, caplog):
    """One INFO line has the URL, file, size, S3 object and elapsed time."""
    caplog.set_level(logging.INFO, logger="kybr_pipeline")

    Pipeline().ingest("compras", "202508")

    [record] = caplog.records
    assert record.levelno == logging.INFO
    assert re.fullmatch(
        rf"compras 202508: {configs.BASE_URL}/compras/202508"
        rf" -> 202508_Compras\.zip \(3 bytes\)"
        rf" -> s3://{configs.BUCKET_NAME}/raw/compras/202508_Compras\.zip"
        r" in \d+\.\ds",
        record.getMessage(),
    )


@pytest.mark.usefixtures("tmp_dir")
def test_ingest_logs_the_download_at_debug(transfer, caplog):
    caplog.set_level(logging.DEBUG, logger="kybr_pipeline")

    Pipeline().ingest("compras", "202508")

    assert re.fullmatch(
        r"Downloaded 202508_Compras\.zip \(3 bytes\) in \d+\.\ds",
        caplog.messages[0],
    )


@pytest.mark.usefixtures("tmp_dir")
def test_ingest_logs_nothing_when_it_fails(transfer, caplog):
    caplog.set_level(logging.DEBUG, logger="kybr_pipeline")
    transfer.upload_error = RuntimeError("upload failed")

    with pytest.raises(RuntimeError):
        Pipeline().ingest("compras", "202508")

    assert [r.levelno for r in caplog.records] == [logging.DEBUG]
