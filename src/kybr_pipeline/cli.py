import argparse
from importlib.metadata import version

from kybr_pipeline import configs, scripts

parser = argparse.ArgumentParser(
    prog="kybr-pipeline",
    description="Know-Your-Business Pipeline for Brazil.",
)
parser.add_argument(
    '-V',
    '--version',
    action='version',
    version=f'%(prog)s {version("kybr-pipeline")}',
)

subparsers = parser.add_subparsers(dest="command", required=True)

ingest = subparsers.add_parser(
    "ingest",
    help="download an open data set and upload it to S3",
)
ingest_subparsers = ingest.add_subparsers(dest="kind", required=True)

monthly = ingest_subparsers.add_parser(
    "monthly",
    help="data sets with one file per month, such as compras",
)
monthly.add_argument(
    "-l", "--label",
    dest="endpoint",
    required=True,
    choices=configs.MONTHLY_ENDPOINTS,
    help="the open data set to download",
)
monthly.add_argument(
    "-i", "--ref-ini",
    help="the first month, as YYYYMM; defaults to the current month",
)
monthly.add_argument(
    "-f", "--ref-fin",
    help="the last month, as YYYYMM; defaults to the current month",
)
monthly.set_defaults(func=scripts.ingest_monthly)

snapshot = ingest_subparsers.add_parser(
    "snapshot",
    help="data sets with only the latest day's file, such as ceis",
)
snapshot.add_argument(
    "-l", "--label",
    dest="endpoint",
    required=True,
    choices=configs.SNAPSHOT_ENDPOINTS,
    help="the open data set to download",
)
snapshot.set_defaults(func=scripts.ingest_snapshot)


def main() -> None:
    """Run the `kybr-pipeline` command typed on the command line.

    Each subcommand calls its function in `kybr_pipeline.scripts`. An
    invalid reference ends with a usage error, like any other bad
    argument.
    """
    args = parser.parse_args()
    try:
        args.func(args)

    except scripts.InvalidReferenceError as e:
        parser.error(str(e))


if __name__ == "__main__":
    main()
