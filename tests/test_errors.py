import json

import requests


def test_decode_error(mocker, script_runner, conf_default_target):
    mock_response = mocker.Mock()
    mock_response.json.side_effect = json.decoder.JSONDecodeError("", "", 0)
    mock_get = mocker.patch("scrapyd_client.pyclient.requests.get", autospec=True)
    mock_get.return_value = mock_response
    result = script_runner.run(["scrapyd-client", "projects"])

    assert not result.success
    assert result.stdout.startswith("Received a malformed response:\n")


def test_projects(mocker, script_runner, conf_default_target):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        "status": "error",
        "message": "Something went wrong.",
    }
    mock_get = mocker.patch("scrapyd_client.pyclient.requests.get", autospec=True)
    mock_get.return_value = mock_response
    result = script_runner.run(["scrapyd-client", "projects"])

    assert not result.success
    assert result.stdout == "Scrapyd responded with an error:\nSomething went wrong.\n"


def test_connection_error(mocker, script_runner, conf_default_target):
    mock_get = mocker.patch("scrapyd_client.pyclient.requests.get", autospec=True)
    mock_get.side_effect = requests.ConnectionError()
    result = script_runner.run(["scrapyd-client", "projects"])

    assert not result.success
    assert result.stdout == "Failed to connect to target (default):\n\n"
