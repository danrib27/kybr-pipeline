import argparse
import logging
from datetime import UTC, datetime
from http import HTTPStatus

import pytest
import requests

from kybr_pipeline import scripts

# 2026-11-05 01:00 UTC is still 2026-11-04 in Belém (UTC-3).
NOW_UTC = datetime(2026, 11, 5, 1, 0, tzinfo=UTC)


class FrozenDatetime(datetime):
    """A `datetime` whose `now` always returns `NOW_UTC`."""

    @classmethod
    def now(cls, tz=None):
        return NOW_UTC.astimezone(tz)


def http_error(status=None):
    """Build the `HTTPError` that `raise_for_status` raises."""
    if status is None:
        return requests.HTTPError("no response")

    response = requests.Response()
    response.status_code = status
    return requests.HTTPError(f"{status}", response=response)


@pytest.fixture(autouse=True)
def frozen_clock(monkeypatch):
    monkeypatch.setattr(scripts, "datetime", FrozenDatetime)


def monthly_args(ref_ini=None, ref_fin=None):
    return argparse.Namespace(
        endpoint="compras", ref_ini=ref_ini, ref_fin=ref_fin
    )


def snapshot_args():
    return argparse.Namespace(endpoint="ceis")


def test_validate_ref_accepts_a_real_month():
    scripts.validate_ref("202508")


@pytest.mark.parametrize(
    "ref",
    [
        pytest.param("202413", id="month 13"),
        pytest.param("2025-08", id="separator"),
        pytest.param("20250801", id="a day"),
        pytest.param("20258", id="one digit month"),
    ],
)
def test_validate_ref_rejects_an_invalid_reference(ref):
    with pytest.raises(scripts.InvalidReferenceError, match="YYYYMM"):
        scripts.validate_ref(ref)


def test_ingest_monthly_defaults_to_the_current_month_in_belem(pipeline):
    scripts.ingest_monthly(monthly_args())

    assert pipeline.calls == [("compras", "202611")]


def test_ingest_monthly_ingests_every_month_in_the_range(pipeline):
    scripts.ingest_monthly(monthly_args("202511", "202602"))

    assert pipeline.calls == [
        ("compras", "202511"),
        ("compras", "202512"),
        ("compras", "202601"),
        ("compras", "202602"),
    ]


def test_ingest_monthly_rejects_ref_ini_after_ref_fin(pipeline):
    with pytest.raises(scripts.InvalidReferenceError):
        scripts.ingest_monthly(monthly_args("202603", "202601"))

    assert pipeline.calls == []


def test_ingest_monthly_rejects_an_invalid_reference(pipeline):
    with pytest.raises(scripts.InvalidReferenceError, match="202413"):
        scripts.ingest_monthly(monthly_args("202501", "202413"))

    assert pipeline.calls == []


def test_ingest_snapshot_downloads_today_in_belem(pipeline):
    scripts.ingest_snapshot(snapshot_args())

    assert pipeline.calls == [("ceis", "20261104")]


@pytest.mark.parametrize(
    "status", [HTTPStatus.FORBIDDEN, HTTPStatus.NOT_FOUND]
)
def test_ingest_snapshot_falls_back_to_yesterday(pipeline, status):
    pipeline.errors["20261104"] = http_error(status)

    scripts.ingest_snapshot(snapshot_args())

    assert pipeline.calls == [("ceis", "20261104"), ("ceis", "20261103")]


def test_ingest_snapshot_reraises_other_http_errors(pipeline):
    error = http_error(HTTPStatus.INTERNAL_SERVER_ERROR)
    pipeline.errors["20261104"] = error

    with pytest.raises(requests.HTTPError) as excinfo:
        scripts.ingest_snapshot(snapshot_args())

    assert excinfo.value is error
    assert pipeline.calls == [("ceis", "20261104")]


def test_ingest_snapshot_reraises_an_error_without_response(pipeline):
    pipeline.errors["20261104"] = http_error()

    with pytest.raises(requests.HTTPError, match="no response"):
        scripts.ingest_snapshot(snapshot_args())

    assert pipeline.calls == [("ceis", "20261104")]


def test_ingest_monthly_logs_the_range(pipeline, caplog):
    caplog.set_level(logging.INFO, logger="kybr_pipeline")

    scripts.ingest_monthly(monthly_args("202511", "202602"))

    assert caplog.messages == [
        "Ingesting compras: 4 month(s), 202511 to 202602"
    ]


def test_ingest_monthly_logs_the_month_that_fails(pipeline, caplog):
    caplog.set_level(logging.INFO, logger="kybr_pipeline")
    error = http_error(HTTPStatus.INTERNAL_SERVER_ERROR)
    pipeline.errors["202512"] = error

    with pytest.raises(requests.HTTPError):
        scripts.ingest_monthly(monthly_args("202511", "202602"))

    [record] = [r for r in caplog.records if r.levelno == logging.ERROR]
    assert record.getMessage() == f"compras 202512 failed: {error!r}"
    assert pipeline.calls == [("compras", "202511"), ("compras", "202512")]


def test_ingest_snapshot_logs_the_fallback_to_yesterday(pipeline, caplog):
    pipeline.errors["20261104"] = http_error(HTTPStatus.NOT_FOUND)

    scripts.ingest_snapshot(snapshot_args())

    [record] = caplog.records
    assert record.levelno == logging.WARNING
    assert record.getMessage() == (
        "ceis 20261104 is not published (HTTP 404); falling back to 20261103"
    )


def test_ingest_snapshot_does_not_warn_without_a_fallback(pipeline, caplog):
    scripts.ingest_snapshot(snapshot_args())

    assert caplog.records == []
