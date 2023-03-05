import pytest

from scrapyd_client import ScrapydClient


@pytest.fixture
def fxt_client():
    return ScrapydClient()


@pytest.fixture
def fxt_lib(mocker):
    return mocker.patch("scrapyd_client.pyclient.lib")


def test_projects(fxt_lib, fxt_client):
    fxt_client.projects()
    fxt_lib.get_projects.assert_called_once()


def test_spiders(fxt_lib, fxt_client):
    kwargs = {"project": "project"}
    fxt_client.spiders(**kwargs)
    fxt_lib.get_spiders.assert_called_once()


def test_jobs(fxt_lib, fxt_client):
    kwargs = {"project": "project"}
    fxt_client.jobs(**kwargs)
    fxt_lib.get_jobs.assert_called_once()


def test_schedule(fxt_lib, fxt_client):
    kwargs = {"project": "myproject", "spider": "myspider"}
    fxt_client.schedule(**kwargs)
    fxt_lib.schedule.assert_called_once()
