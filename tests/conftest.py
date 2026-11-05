import os
from pathlib import Path

import pytest

# `kybr_pipeline.configs` reads the file on import, so this must be set
# before any test module imports the package. It makes the tests work
# from any directory, not only from the project root.
os.environ.setdefault(
    "KYBR_PIPELINE_CONFIG",
    str(Path(__file__).parents[1] / "config.yaml"),
)


class FakePipeline:
    """Stands in for `Pipeline` in `scripts`, recording `ingest` calls.

    An instance is also its own class: `Pipeline()` returns it, so the
    test reads the calls from the fixture. `ingest` raises the error set
    in `errors` for a reference.
    """

    def __init__(self):
        self.calls: list[tuple[str, str]] = []
        self.errors: dict[str, Exception] = {}

    def __call__(self):
        return self

    def ingest(self, endpoint, ref):
        self.calls.append((endpoint, ref))
        if ref in self.errors:
            raise self.errors[ref]


@pytest.fixture
def pipeline(monkeypatch):
    fake = FakePipeline()
    monkeypatch.setattr("kybr_pipeline.scripts.Pipeline", fake)
    return fake
