def test_projects(mocker, script_runner, conf_default_target):
    projects = ["foo", "bar"]
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"projects": ["foo", "bar"], "status": "ok"}
    mock_get = mocker.patch("scrapyd_client.pyclient.requests.get", autospec=True)
    mock_get.return_value = mock_response
    result = script_runner.run(["scrapyd-client", "projects"])

    assert result.success, result.stdout + "\n" + result.stderr
    assert not result.stderr, result.stderr
    assert result.stdout == "\n".join(projects) + "\n"
