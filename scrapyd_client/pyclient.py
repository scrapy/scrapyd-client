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
