from __future__ import annotations

import fnmatch
import json

import requests

from scrapyd_client.exceptions import ErrorResponse, MalformedResponse
from scrapyd_client.utils import get_auth

DEFAULT_TARGET_URL = "http://localhost:6800"
HEADERS = requests.utils.default_headers().copy()
HEADERS["User-Agent"] = "Scrapyd-client/2.0.2"


class ScrapydClient:
    """ScrapydClient to interact with a Scrapyd instance."""

    def __init__(self, url: str | None = None, username: str | None = None, password: str | None = None) -> None:
        """Initialize ScrapydClient."""
        self.url = DEFAULT_TARGET_URL if url is None else url
        self.auth = get_auth(url=self.url, username=username, password=password)

    def projects(self, pattern: str = "*") -> list[str]:
        response = self._get("listprojects")
        return fnmatch.filter(response["projects"], pattern)

    def spiders(self, project: str, pattern: str = "*") -> list[str]:
        response = self._get("listspiders", params={"project": project})
        return fnmatch.filter(response["spiders"], pattern)

    def jobs(self, project: str) -> dict:
        return self._get("listjobs", params={"project": project})

    def daemonstatus(self) -> dict:
        """
        Get the status of the Scrapyd daemon.
        :return: JSON response from the Scrapyd daemon status endpoint.
        """
        return self._get("daemonstatus")

    def versions(self, project: str) -> list[str]:
        """
        List versions for a given project.
        :param project: Name of the project.
        :return: List of versions for the project.
        """
        params = {"project": project}
        response = self._get("listversions", params)
        return response.get("versions", [])

    def schedule(self, project: str, spider: str, args: list[tuple[str, str]] | None = None) -> str:
        if args is None:
            args = []
        response = self._post("schedule", data=[*args, ("project", project), ("spider", spider)])
        return response["jobid"]

    def status(self, jobid: str, project: str | None = None) -> dict:
        params = {"job": jobid}
        if project is not None:
            params["project"] = project

        return self._get("status", params)

    def delproject(self, project: str) -> dict:
        """
        Delete a project.
        :param project: Name of the project.
        :return: JSON response from the Scrapyd delete project endpoint.
        :raises ErrorResponse if the project is not found.
        """
        if project not in self.projects():
            raise ErrorResponse(f"Project {project} not found.")
        return self._post("delproject", data={"project": project})

    def delversion(self, project: str, version: str) -> dict:
        """
        Delete a specific version of a project.
        :param project: Name of the project.
        :param version: Version to delete. Can be "all" to delete all versions.
        :return: JSON response from the Scrapyd delete version endpoint.
        :raises: ErrorResponse if the project or version is not found.
        """
        if project not in self.projects():
            raise ErrorResponse(f"Project {project} not found.")
        if version == "all":
            versions = self.versions(project)
            for ver in versions:
                self._post("delversion", data={"project": project, "version": ver})
            return {"status": "ok", "message": "All versions deleted."}
        if version not in self.versions(project):
            raise ErrorResponse(f"Version {version} not found in project {project}.")

        return self._post("delversion", data={"project": project, "version": version})

    def cancel(self, project: str, jobid: str) -> dict:
        """
        Cancel a running job or all running jobs.
        :param project: Name of the project.
        :param jobid: ID of the job to cancel or "all" to cancel all jobs.
        :return: JSON response from the Scrapyd cancel job endpoint.
        :raises: ErrorResponse if the project or job is not found.
        """
        if project not in self.projects():
            raise ErrorResponse(f"Project {project} not found.")

        running_jobs = self.jobs(project)["running"]
        if jobid == "all":
            responses = []
            for job in running_jobs:
                responses.append(self._post("cancel", data={"project": project, "job": job}))
            return {"status": "ok", "responses": responses}

        if jobid not in running_jobs:
            raise ErrorResponse(f"Job {jobid} not found in project {project}.")

        return self._post("cancel", data={"project": project, "job": jobid})

    def _get(self, basename: str, params=None):
        if params is None:
            params = {}
        return _process_response(
            requests.get(f"{self.url}/{basename}.json", params=params, headers=HEADERS, auth=self.auth)
        )

    def _post(self, basename: str, data):
        return _process_response(
            requests.post(f"{self.url}/{basename}.json", data=data, headers=HEADERS, auth=self.auth)
        )


def _process_response(response):
    try:
        response = response.json()
    except json.decoder.JSONDecodeError as e:
        raise MalformedResponse(response.text) from e

    status = response["status"]
    if status == "ok":
        return response
    if status == "error":
        raise ErrorResponse(response["message"])
    raise RuntimeError(f"Unhandled response status: {status}")
