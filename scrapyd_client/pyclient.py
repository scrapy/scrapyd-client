from __future__ import annotations

import fnmatch
import json
import warnings
from typing import Any
from urllib.parse import urlparse

import requests

from scrapyd_client.exceptions import ErrorResponse, MalformedResponse
from scrapyd_client.utils import get_auth

DEFAULT_TARGET_URL = "http://localhost:6800"
HEADERS = requests.utils.default_headers().copy()
HEADERS["User-Agent"] = "Scrapyd-client/2.0.3"

DEFAULT_TIMEOUT = 30.0


class ScrapydClient:
    """ScrapydClient to interact with a Scrapyd instance with security features."""

    def __init__(
        self,
        url: str | None = None,
        username: str | None = None,
        password: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        verify_ssl: bool = True,
        cert_file: str | None = None,
        key_file: str | None = None,
        ca_bundle: str | None = None,
    ) -> None:
        """
        Initialize ScrapydClient with security options.

        Args:
            url: Scrapyd server URL
            username: Authentication username
            password: Authentication password
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates for HTTPS requests
            cert_file: Path to client certificate file for mutual TLS
            key_file: Path to client private key file for mutual TLS
            ca_bundle: Path to CA bundle file for custom certificate validation

        """
        self.url = DEFAULT_TARGET_URL if url is None else url
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        # Validate URL and security settings
        self._validate_security_settings()

        # Set up authentication
        self.auth = get_auth(url=self.url, username=username, password=password)

        # Configure SSL/TLS settings
        self.cert = None
        if cert_file and key_file:
            self.cert = (cert_file, key_file)

        # Configure CA bundle
        self.ca_bundle = ca_bundle if ca_bundle else verify_ssl

        # Create session for connection reuse and security
        self.session = requests.Session()
        self.session.verify = self.ca_bundle
        if self.cert:
            self.session.cert = self.cert

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

    def _validate_security_settings(self) -> None:
        """Validate security settings and warn about potential issues."""
        parsed_url = urlparse(self.url)

        # Warn about insecure HTTP usage
        if parsed_url.scheme == "http":
            if parsed_url.hostname not in ("localhost", "127.0.0.1", "::1"):
                warnings.warn(
                    f"Using HTTP instead of HTTPS for remote server {self.url}. "
                    "Credentials and data will be transmitted in plain text.",
                    UserWarning,
                    stacklevel=3,
                )

        # Warn about disabled SSL verification
        if not self.verify_ssl and parsed_url.scheme == "https":
            warnings.warn(
                "SSL certificate verification is disabled. This is insecure and should only be used for testing.",
                UserWarning,
                stacklevel=3,
            )

    def health_check(self, timeout: float | None = None) -> dict[str, Any]:
        """
        Perform a comprehensive health check of the Scrapyd server.

        Args:
            timeout: Override default timeout for health check

        Returns:
            Dict containing health check results

        """
        check_timeout = timeout or min(self.timeout, 10.0)
        health_info = {
            "server_reachable": False,
            "ssl_valid": None,
            "auth_working": False,
            "daemon_status": None,
            "error": None,
        }

        try:
            # Check basic connectivity and daemon status
            daemon_status = self._get("daemonstatus", timeout=check_timeout)
            health_info["server_reachable"] = True
            health_info["daemon_status"] = daemon_status

            # Check SSL certificate validity for HTTPS
            parsed_url = urlparse(self.url)
            if parsed_url.scheme == "https":
                health_info["ssl_valid"] = self.verify_ssl  # Simplified for now

            # If we got here without exception, auth is working
            health_info["auth_working"] = True

        except Exception as e:
            health_info["error"] = str(e)

        return health_info

    def _get(
        self, basename: str, params: dict[str, Any] | None = None, timeout: float | None = None
    ) -> dict[str, Any]:
        """Make a secure GET request."""
        if params is None:
            params = {}

        request_timeout = timeout or self.timeout

        try:
            response = self.session.get(
                f"{self.url}/{basename}.json", params=params, headers=HEADERS, auth=self.auth, timeout=request_timeout
            )
            return _process_response(response)
        except requests.exceptions.SSLError as e:
            raise ConnectionError(f"SSL certificate verification failed for {self.url}: {e}") from e
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to Scrapyd at {self.url}: {e}") from e

    def _post(
        self, basename: str, data: dict[str, Any] | list[tuple[str, str]], timeout: float | None = None
    ) -> dict[str, Any]:
        """Make a secure POST request."""
        request_timeout = timeout or self.timeout

        try:
            response = self.session.post(
                f"{self.url}/{basename}.json", data=data, headers=HEADERS, auth=self.auth, timeout=request_timeout
            )
            return _process_response(response)
        except requests.exceptions.SSLError as e:
            raise ConnectionError(f"SSL certificate verification failed for {self.url}: {e}") from e
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to Scrapyd at {self.url}: {e}") from e

    def close(self) -> None:
        """Close the session and clean up resources."""
        if hasattr(self, "session"):
            self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def _process_response(response: requests.Response) -> dict[str, Any]:
    """Process HTTP response with security-conscious error handling."""
    # Check HTTP status first
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            raise ConnectionError("Authentication failed. Check username and password.") from e
        if response.status_code == 403:
            raise ConnectionError("Access forbidden. Check user permissions.") from e
        if response.status_code == 404:
            raise ConnectionError(f"Scrapyd API endpoint not found: {response.url}") from e
        raise ConnectionError(f"HTTP {response.status_code}: {response.reason}") from e

    # Parse JSON response with size limit for security
    content_length = response.headers.get("content-length")
    if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
        raise MalformedResponse("Response too large (>10MB), potential security issue")

    try:
        json_response = response.json()
    except json.decoder.JSONDecodeError as e:
        # Don't include full response text in error for security
        response_preview = response.text[:200] if len(response.text) <= 200 else response.text[:200] + "..."
        raise MalformedResponse(
            f"Invalid JSON response from {response.url}. Response preview: {response_preview}"
        ) from e

    # Validate response structure
    if not isinstance(json_response, dict):
        raise MalformedResponse(f"Expected JSON object, got {type(json_response).__name__}")

    if "status" not in json_response:
        raise MalformedResponse("Response missing required 'status' field")

    status = json_response["status"]
    if status == "ok":
        return json_response
    if status == "error":
        error_msg = json_response.get("message", "Unknown error")
        raise ErrorResponse(f"Scrapyd error: {error_msg}")
    raise RuntimeError(f"Unhandled response status: {status}")
