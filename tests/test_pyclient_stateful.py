from scrapyd_client.pyclient import ScrapydClient


def test_delproject(mocker, conf_default_target):
    client = ScrapydClient()

    mocker.patch.object(client, "projects", return_value=["existing_project"])
    mock_post = mocker.patch.object(client, "_post", return_value={"status": "ok"})

    response = client.delproject("existing_project")

    assert response["status"] == "ok"
    mock_post.assert_called_once_with("delproject", data={"project": "existing_project"})


def test_delversion(mocker, conf_default_target):
    client = ScrapydClient()

    mocker.patch.object(client, "projects", return_value=["existing_project"])
    mocker.patch.object(client, "versions", return_value=["v1.0", "v1.1"])
    mock_post = mocker.patch.object(client, "_post", return_value={"status": "ok"})

    response = client.delversion("existing_project", "v1.0")

    assert response["status"] == "ok"
    mock_post.assert_called_once_with("delversion", data={"project": "existing_project", "version": "v1.0"})


def test_cancel(mocker, conf_default_target):
    client = ScrapydClient()

    mocker.patch.object(client, "projects", return_value=["existing_project"])
    mocker.patch.object(client, "jobs", return_value={"running": ["jobid1", "jobid2"]})
    mock_post = mocker.patch.object(client, "_post", return_value={"status": "ok"})

    response = client.cancel("existing_project", "jobid1")

    assert response["status"] == "ok"
    mock_post.assert_called_once_with("cancel", data={"project": "existing_project", "job": "jobid1"})
