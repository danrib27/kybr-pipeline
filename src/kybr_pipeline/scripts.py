import argparse
from datetime import datetime, timedelta
from http import HTTPStatus

import requests

from kybr_pipeline import Pipeline
from kybr_pipeline.utils import TIMEZONE, calculate_refs

# Status the portal returns for a daily file that is not published.
MISSING_FILE_STATUS = {HTTPStatus.FORBIDDEN, HTTPStatus.NOT_FOUND}


class InvalidReferenceError(ValueError):
    """A reference that is not a valid YYYYMM month."""


def validate_ref(ref: str) -> None:
    """Check that a reference is a real month.

    Args:
        ref: The reference, as 'YYYYMM'.

    Raises:
        InvalidReferenceError: If the reference has another format, such
            as '20258', or is not a real month, such as '202413'.
    """
    message = f"invalid reference {ref!r}: use YYYYMM"
    try:
        month = datetime.strptime(ref, "%Y%m").replace(tzinfo=TIMEZONE)

    except ValueError as e:
        raise InvalidReferenceError(message) from e

    # strptime's %m also takes one digit, so '20258' would pass.
    if month.strftime("%Y%m") != ref:
        raise InvalidReferenceError(message)


def ingest_monthly(args: argparse.Namespace) -> None:
    """Run `ingest monthly`: download every month in the range.

    A missing reference defaults to the current month in Belém.

    Args:
        args: The parsed command line, with `endpoint`, `ref_ini` and
            `ref_fin`.

    Raises:
        InvalidReferenceError: If a reference is invalid or ref_ini comes
            after ref_fin.
    """
    current_ref = datetime.now(TIMEZONE).strftime("%Y%m")
    ref_ini = args.ref_ini or current_ref
    ref_fin = args.ref_fin or current_ref

    for ref in (ref_ini, ref_fin):
        validate_ref(ref)

    try:
        references = calculate_refs(ref_ini, ref_fin)

    except ValueError as e:
        raise InvalidReferenceError(str(e)) from e

    pipeline = Pipeline()

    for ref in references:
        pipeline.ingest(args.endpoint, ref)


def ingest_snapshot(args: argparse.Namespace) -> None:
    """Run `ingest snapshot`: download the latest daily file.

    The portal keeps only the file of the latest published day, and
    today's file may not be out yet, so it tries today first and falls
    back to yesterday.

    Args:
        args: The parsed command line, with `endpoint`.
    """
    today = datetime.now(TIMEZONE)
    pipeline = Pipeline()

    try:
        pipeline.ingest(args.endpoint, today.strftime("%Y%m%d"))

    except requests.HTTPError as e:
        response = e.response
        if response is None or response.status_code not in MISSING_FILE_STATUS:
            raise

        yesterday = today - timedelta(days=1)
        pipeline.ingest(args.endpoint, yesterday.strftime("%Y%m%d"))
