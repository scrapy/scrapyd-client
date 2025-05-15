from __future__ import annotations

import fnmatch
import json

import requests

from scrapyd_client.exceptions import ErrorResponse, MalformedResponse
from scrapyd_client.utils import get_auth

DEFAULT_TARGET_URL = "http://localhost:6800"
HEADERS = requests.utils.default_headers().copy()
HEADERS["User-Agent"] = "Scrapyd-client/2.0.3"


class ScrapydClient:
    """ScrapydClient to interact with a Scrapyd instance."""

    def __init__(self, url: str | None = None, username: str | None = None, password: str | None = None) -> None:
        """Initialize ScrapydClient."""
        self.url = DEFAULT_TARGET_URL if url is None else url
        self.auth = get_auth(url=self.url, username=username, password=password)

    def projects(self, pattern: str = "*") -> list[str]:
        """
        Return the projects matching a pattern (if provided).

        :param pattern: The `pattern <https://docs.python.org/3/library/fnmatch.html>`__ for the projects to match
        :return: The "projects" value of the API response, filtered by the pattern (if provided).

        .. seealso:: `listprojects.json <https://scrapyd.readthedocs.io/en/latest/api.html#listprojects-json>`__
        """
        return fnmatch.filter(self._get("listprojects")["projects"], pattern)

    def spiders(self, project: str, pattern: str = "*") -> list[str]:
        """
        Return the spiders matching a pattern (if provided).

        :param pattern: The `pattern <https://docs.python.org/3/library/fnmatch.html>`__ for the spiders to match
        :return: The "spiders" value of the API response, filtered by the pattern (if provided).

        .. seealso:: `listspiders.json <https://scrapyd.readthedocs.io/en/latest/api.html#listspiders-json>`__
        """
        return fnmatch.filter(self._get("listspiders", {"project": project})["spiders"], pattern)

    def jobs(self, project: str) -> dict:
        """
        :return: The unmodified API response.

        .. seealso:: `listjobs.json <https://scrapyd.readthedocs.io/en/latest/api.html#listjobs-json>`__
        """
        return self._get("listjobs", {"project": project})

    def daemonstatus(self) -> dict:
        """
        :return: The unmodified API response.

        .. seealso:: `daemonstatus.json <https://scrapyd.readthedocs.io/en/latest/api.html#daemonstatus-json>`__
        """
        return self._get("daemonstatus")

    def versions(self, project: str) -> list[str]:
        """
        :return: The "versions" value of the API response.

        .. seealso:: `listversions.json <https://scrapyd.readthedocs.io/en/latest/api.html#listversions-json>`__
        """
        return self._get("listversions", {"project": project})["versions"]

    def schedule(self, project: str, spider: str, args: list[tuple[str, str]] | None = None) -> str:
        """
        :return: The "jobid" value of the API response.

        .. seealso:: `schedule.json <https://scrapyd.readthedocs.io/en/latest/api.html#schedule-json>`__
        """
        if args is None:
            args = []

        return self._post("schedule", data=[*args, ("project", project), ("spider", spider)])["jobid"]

    def status(self, jobid: str, project: str | None = None) -> dict:
        """
        :return: The unmodified API response.

        .. seealso:: `status.json <https://scrapyd.readthedocs.io/en/latest/api.html#status-json>`__
        """
        params = {"job": jobid}
        if project is not None:
            params["project"] = project

        return self._get("status", params)

    def delproject(self, project: str) -> dict:
        """
        :return: The unmodified API response.

        .. seealso:: `delproject.json <https://scrapyd.readthedocs.io/en/latest/api.html#delproject-json>`__
        """
        return self._post("delproject", data={"project": project})

    def delversion(self, project: str, version: str) -> dict:
        """
        :return: The unmodified API response.

        .. seealso:: `delversion.json <https://scrapyd.readthedocs.io/en/latest/api.html#delversion-json>`__
        """
        return self._post("delversion", data={"project": project, "version": version})

    def cancel(self, project: str, jobid: str) -> dict:
        """
        :return: The unmodified API response.

        .. seealso:: `cancel.json <https://scrapyd.readthedocs.io/en/latest/api.html#cancel-json>`__
        """
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
