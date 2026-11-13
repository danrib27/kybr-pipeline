import logging

import pytest

from kybr_pipeline import cli


def run(monkeypatch, *argv):
    monkeypatch.setattr("sys.argv", ["kybr-pipeline", *argv])
    cli.main()


def test_ingest_monthly_runs_the_range(monkeypatch, pipeline):
    run(
        monkeypatch,
        "ingest",
        "monthly",
        "-l",
        "compras",
        "-i",
        "202501",
        "-f",
        "202502",
    )

    assert pipeline.calls == [("compras", "202501"), ("compras", "202502")]


def test_ingest_snapshot_runs(monkeypatch, pipeline):
    run(monkeypatch, "ingest", "snapshot", "-l", "cnep")

    assert len(pipeline.calls) == 1
    assert pipeline.calls[0][0] == "cnep"


def test_invalid_reference_is_a_usage_error(monkeypatch, pipeline, capsys):
    with pytest.raises(SystemExit) as excinfo:
        run(
            monkeypatch,
            "ingest",
            "monthly",
            "-l",
            "compras",
            "-i",
            "202413",
        )

    assert excinfo.value.code == 2
    assert "invalid reference '202413'" in capsys.readouterr().err
    assert pipeline.calls == []


@pytest.mark.parametrize(
    "argv",
    [
        pytest.param(["ingest", "monthly"], id="no label"),
        pytest.param(["ingest", "monthly", "-l", "ceis"], id="snapshot label"),
        pytest.param(
            ["ingest", "snapshot", "-l", "compras"], id="monthly label"
        ),
        pytest.param(
            ["ingest", "snapshot", "-l", "ceis", "-i", "202501"],
            id="snapshot reference",
        ),
    ],
)
def test_bad_arguments_are_usage_errors(monkeypatch, pipeline, argv):
    with pytest.raises(SystemExit) as excinfo:
        run(monkeypatch, *argv)

    assert excinfo.value.code == 2
    assert pipeline.calls == []


@pytest.mark.usefixtures("pipeline")
def test_verbose_logs_at_debug(monkeypatch, package_logger):
    run(monkeypatch, "-v", "ingest", "snapshot", "-l", "ceis")

    assert package_logger.level == logging.DEBUG


@pytest.mark.usefixtures("package_logger")
def test_invalid_log_level_is_a_usage_error(monkeypatch, pipeline, capsys):
    monkeypatch.setenv("LOG_LEVEL", "LOUD")

    with pytest.raises(SystemExit) as excinfo:
        run(monkeypatch, "ingest", "snapshot", "-l", "ceis")

    assert excinfo.value.code == 2
    assert "invalid LOG_LEVEL" in capsys.readouterr().err
    assert pipeline.calls == []
