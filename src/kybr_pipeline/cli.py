import argparse
from collections.abc import Sequence


def _reference(value: str) -> str:
    """Check that a reference is a month (YYYYMM) or a day (YYYYMMDD).

    Args:
        value: The reference typed on the command line.

    Returns:
        The reference, unchanged.

    Raises:
        argparse.ArgumentTypeError: If the reference has another format.
    """
    if not (value.isdigit() and len(value) in {6, 8}):
        raise argparse.ArgumentTypeError(
            f"invalid reference {value!r}: use YYYYMM or YYYYMMDD"
        )
    return value


def build_parser(endpoints: Sequence[str]) -> argparse.ArgumentParser:
    """Build the command line parser of the pipeline.

    Args:
        endpoints: The open data sets the ingest command accepts.

    Returns:
        The parser with the ingest subcommand.
    """
    parser = argparse.ArgumentParser(
        prog="kybr-pipeline",
        description="Know-Your-Business Pipeline for Brazil.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest = subparsers.add_parser(
        "ingest",
        help="download an open data set and upload it to S3",
    )
    ingest.add_argument(
        "endpoint",
        choices=endpoints,
        help="the open data set to download",
    )
    ingest.add_argument(
        "ref",
        type=_reference,
        help="the reference to download, as YYYYMM or YYYYMMDD",
    )

    return parser


def parse_args(
    endpoints: Sequence[str],
    argv: Sequence[str] | None = None,
) -> argparse.Namespace:
    """Parse the command line arguments.

    Args:
        endpoints: The open data sets the ingest command accepts.
        argv: The arguments to parse. Defaults to `sys.argv[1:]`.

    Returns:
        The parsed arguments: `command`, `endpoint` and `ref`.
    """
    return build_parser(endpoints).parse_args(argv)
