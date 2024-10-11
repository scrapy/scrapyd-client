import fnmatch
import json

import requests

from scrapyd_client.exceptions import ErrorResponse, MalformedResponse
from scrapyd_client.utils import get_auth

HEADERS = requests.utils.default_headers().copy()
HEADERS["User-Agent"] = "Scrapyd-client/2.0.0"


def get_projects(url, pattern="*", username=None, password=None):
    """
    Return the project names deployed in a Scrapyd instance.

    :param url: The base URL of the Scrapd instance.
    :type url: str
    :param pattern: A globbing pattern that is used to filter the results,
                    defaults to '*'.
    :type pattern: str
    :param username: The username to connect to Scrapyd.
    :type pattern: str
    :param password: The password to connect to Scrapyd.
    :type pattern: str
    :rtype: A list of strings.
    """
    response = _get_request(
        f"{url}/listprojects.json",
        auth=get_auth(url=url, username=username, password=password),
    )
    return fnmatch.filter(response["projects"], pattern)


def get_spiders(url, project, pattern="*", username=None, password=None):
    """
    Return the list of spiders implemented in a project.

    :param url: The base URL of the Scrapd instance.
    :type url: str
    :param project: The name of the project.
    :type project: str
    :param pattern: A globbing pattern that is used to filter the results,
                    defaults to '*'.
    :type pattern: str
    :param username: The username to connect to Scrapyd.
    :type pattern: str
    :param password: The password to connect to Scrapyd.
    :type pattern: str
    :rtype: A list of strings.
    """
    response = _get_request(
        f"{url}/listspiders.json",
        params={"project": project},
        auth=get_auth(url=url, username=username, password=password),
    )
    return fnmatch.filter(response["spiders"], pattern)


def get_jobs(url, project, username=None, password=None):
    """
    Return the list of jobs implemented in a project.

    :param url: The base URL of the Scrapd instance.
    :type url: str
    :param project: The name of the project.
    :type project: str
    :param username: The username to connect to Scrapyd.
    :type pattern: str
    :param password: The password to connect to Scrapyd.
    :type pattern: str
    :rtype: A list of strings.
    """
    return _get_request(
        f"{url}/listjobs.json",
        params={"project": project},
        auth=get_auth(url=url, username=username, password=password),
    )


def schedule(url, project, spider, args=None, username=None, password=None):
    """
    Schedule a spider to be executed.

    :param url: The base URL of the Scrapd instance.
    :type url: str
    :param project: The name of the project.
    :type project: str
    :param spider: The name of the spider.
    :type spider: str
    :param args: Extra arguments to the spider.
    :type args: list of tuple
    :param username: The username to connect to Scrapyd.
    :type username: str
    :param password: The password to connect to Scrapyd.
    :type password: str
    :returns: The job id.
    :rtype: str
    """
    if args is None:
        args = []
    response = _post_request(
        f"{url}/schedule.json",
        data=[*args, ("project", project), ("spider", spider)],
        auth=get_auth(url=url, username=username, password=password),
    )
    return response["jobid"]


def _process_response(response):
    """Process the response object into a dictionary."""
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


def _get_request(url, params=None, auth=None):
    """
    Dispatches a request with GET method.

    :param url: The URL to request.
    :type url: str
    :param params: The GET parameters.
    :type params: mapping
    :returns: The processed response.
    :rtype: mapping
    """
    if params is None:
        params = {}
    return _process_response(requests.get(url, params=params, headers=HEADERS, auth=auth))


def _post_request(url, data, auth=None):
    """
    Dispatches a request with POST method.

    :param url: The URL to request.
    :type url: str
    :param data: The data to post.
    :returns: The processed response.
    :rtype: mapping
    """
    return _process_response(requests.post(url, data=data, headers=HEADERS, auth=auth))
