"""Logging settings of the pipeline, applied once per run by the CLI.

Each module logs through `logging.getLogger(__name__)`, a child of the
`kybr_pipeline` logger, so the level set here applies to all of them.
"""

import logging
import os

# The parent of the loggers of every module in the package.
PACKAGE_LOGGER = "kybr_pipeline"
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
# Level of the pipeline logs when `LOG_LEVEL` is unset or empty.
DEFAULT_LEVEL = "INFO"
# Level of other libraries, such as boto3 and urllib3, which are noisy
# at DEBUG.
LIBRARY_LEVEL = logging.WARNING


def configure_logging(verbose: bool = False) -> None:
    """Configure the logs of the pipeline, once per run.

    The level of the `kybr_pipeline` loggers is DEBUG with `verbose`,
    otherwise the `LOG_LEVEL` environment variable, or `DEFAULT_LEVEL`
    when it is unset or empty. Other libraries log at `LIBRARY_LEVEL`,
    so DEBUG shows the pipeline steps without their noise.

    Args:
        verbose: Whether to log at DEBUG level, overriding `LOG_LEVEL`.

    Raises:
        ValueError: If `LOG_LEVEL` is not a level name, such as 'DEBUG'
            or 'INFO'.
    """
    level = (
        "DEBUG" if verbose else os.environ.get("LOG_LEVEL") or DEFAULT_LEVEL
    )
    logging.getLogger(PACKAGE_LOGGER).setLevel(level.upper())
    logging.basicConfig(level=LIBRARY_LEVEL, format=LOG_FORMAT)
