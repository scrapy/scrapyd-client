import pytest

from scrapyd_client.exceptions import ErrorResponse
from scrapyd_client.pyclient import ScrapydClient


def test_daemon_status_returns_valid_response(mocker, conf_default_target):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"status": "ok", "running": 5, "pending": 2, "finished": 10}
    mocker.patch("scrapyd_client.pyclient.requests.get", autospec=True, return_value=mock_response)

    assert ScrapydClient().daemonstatus() == {"status": "ok", "running": 5, "pending": 2, "finished": 10}


def test_daemon_status_handles_error_response(mocker, conf_default_target):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"status": "error", "message": "Daemon is not reachable."}
    mocker.patch("scrapyd_client.pyclient.requests.get", autospec=True, return_value=mock_response)

    with pytest.raises(ErrorResponse) as excinfo:
        ScrapydClient().daemonstatus()
    assert "Daemon is not reachable." in str(excinfo.value)


def test_versions_returns_versions(mocker, conf_default_target):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"status": "ok", "versions": ["v1.0", "v1.1", "v2.0"]}
    mocker.patch("scrapyd_client.pyclient.requests.get", autospec=True, return_value=mock_response)

    assert ScrapydClient().versions("my_project") == ["v1.0", "v1.1", "v2.0"]


def test_versions_handles_no_versions(mocker, conf_default_target):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"status": "ok", "versions": []}
    mocker.patch("scrapyd_client.pyclient.requests.get", autospec=True, return_value=mock_response)

    assert ScrapydClient().versions("my_project") == []


def test_versions_handles_error_response(mocker, conf_default_target):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"status": "error", "message": "Project not found."}
    mocker.patch("scrapyd_client.pyclient.requests.get", autospec=True, return_value=mock_response)

    with pytest.raises(ErrorResponse) as excinfo:
        ScrapydClient().versions("nonexistent")
    assert "Project not found." in str(excinfo.value)
