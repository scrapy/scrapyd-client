import pytest

from scrapyd_client.exceptions import ErrorResponse
from scrapyd_client.pyclient import ScrapydClient


def test_delproject_raises_error_if_project_not_found(mocker, conf_default_target):
    client = ScrapydClient()

    mocker.patch.object(client, "projects", return_value=[])

    with pytest.raises(ErrorResponse) as excinfo:
        client.delproject("nonexistent_project")
    assert "Project nonexistent_project not found." in str(excinfo.value)


def test_delproject_deletes_project_successfully(mocker, conf_default_target):
    client = ScrapydClient()

    mocker.patch.object(client, "projects", return_value=["existing_project"])
    mock_post = mocker.patch.object(client, "_post", return_value={"status": "ok"})

    response = client.delproject("existing_project")

    assert response["status"] == "ok"
    mock_post.assert_called_once_with("delproject", data={"project": "existing_project"})


def test_delversion_raises_error_if_project_not_found(mocker, conf_default_target):
    client = ScrapydClient()

    mocker.patch.object(client, "projects", return_value=[])

    with pytest.raises(ErrorResponse) as excinfo:
        client.delversion("nonexistent_project", "v1.0")
    assert "Project nonexistent_project not found." in str(excinfo.value)


def test_delversion_raises_error_if_version_not_found(mocker, conf_default_target):
    client = ScrapydClient()

    mocker.patch.object(client, "projects", return_value=["existing_project"])
    mocker.patch.object(client, "versions", return_value=["v1.0"])

    with pytest.raises(ErrorResponse) as excinfo:
        client.delversion("existing_project", "v2.0")
    assert "Version v2.0 not found in project existing_project." in str(excinfo.value)


def test_delversion_deletes_all_versions_successfully(mocker, conf_default_target):
    client = ScrapydClient()

    mocker.patch.object(client, "projects", return_value=["existing_project"])
    mocker.patch.object(client, "versions", return_value=["v1.0", "v1.1"])
    mock_post = mocker.patch.object(client, "_post", return_value={"status": "ok"})

    response = client.delversion("existing_project", "all")

    assert response["status"] == "ok"
    assert mock_post.call_count == 2


def test_cancel_raises_error_if_project_not_found(mocker, conf_default_target):
    client = ScrapydClient()

    mocker.patch.object(client, "projects", return_value=[])

    with pytest.raises(ErrorResponse) as excinfo:
        client.cancel("nonexistent_project", "jobid123")
    assert "Project nonexistent_project not found." in str(excinfo.value)


def test_cancel_raises_error_if_job_not_found(mocker, conf_default_target):
    client = ScrapydClient()

    mocker.patch.object(client, "projects", return_value=["existing_project"])
    mocker.patch.object(client, "jobs", return_value={"running": []})

    with pytest.raises(ErrorResponse) as excinfo:
        client.cancel("existing_project", "jobid123")
    assert "Job jobid123 not found in project existing_project." in str(excinfo.value)


def test_cancel_cancels_all_jobs_successfully(mocker, conf_default_target):
    client = ScrapydClient()

    mocker.patch.object(client, "projects", return_value=["existing_project"])
    mocker.patch.object(client, "jobs", return_value={"running": ["jobid1", "jobid2"]})
    mock_post = mocker.patch.object(client, "_post", return_value={"status": "ok"})

    response = client.cancel("existing_project", "all")

    assert response["status"] == "ok"
    assert mock_post.call_count == 2
