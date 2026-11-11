import logging

import pytest

from kybr_pipeline import logs


@pytest.mark.parametrize("value", [None, ""], ids=["unset", "empty"])
def test_level_defaults_to_info(monkeypatch, package_logger, value):
    if value is not None:
        monkeypatch.setenv("LOG_LEVEL", value)

    logs.configure_logging()

    assert package_logger.level == logging.INFO


def test_level_comes_from_the_environment(monkeypatch, package_logger):
    """The name is taken in any case, as typed in `.env`."""
    monkeypatch.setenv("LOG_LEVEL", "warning")

    logs.configure_logging()

    assert package_logger.level == logging.WARNING


def test_verbose_overrides_the_environment(monkeypatch, package_logger):
    monkeypatch.setenv("LOG_LEVEL", "ERROR")

    logs.configure_logging(verbose=True)

    assert package_logger.level == logging.DEBUG
