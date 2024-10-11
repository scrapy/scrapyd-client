import pytest
from scrapy.utils import conf


@pytest.fixture(autouse=True)
def only_closest_scrapy_cfg(monkeypatch):
    """Avoids a developer's own configuration files interfering with tests."""

    def get_sources(use_closest=True):
        if use_closest:
            return [conf.closest_scrapy_cfg()]
        return []

    monkeypatch.setattr(conf, "get_sources", get_sources)
