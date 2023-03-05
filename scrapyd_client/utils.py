import errno
import netrc
import os
from configparser import BasicInterpolation, ConfigParser
from json.decoder import JSONDecodeError
from os.path import dirname, join
from textwrap import indent
from urllib.parse import urlparse

import requests
from requests.auth import HTTPBasicAuth
from scrapy.utils import conf

with open(join(dirname(__file__), "VERSION"), "rt") as f:
    VERSION = f.readline().strip()

HEADERS = requests.utils.default_headers().copy()
HEADERS["User-Agent"] = f"Scrapyd-client/{VERSION}"
DEFAULT_TARGET_URL = "http://localhost:6800"


class EnvInterpolation(BasicInterpolation):
    """Interpolation which expands environment variables in values."""

    def before_get(self, parser, section, option, value, defaults):
        value = super().before_get(parser, section, option, value, defaults)
        return os.path.expandvars(value)


class ErrorResponse(Exception):
    """Raised when Scrapyd reports an error."""

    pass


class MalformedResponse(Exception):
    """Raised when the response can't be decoded."""

    pass


def _process_response(response):
    """Process the response object into a dictionary."""
    try:
        response = response.json()
    except JSONDecodeError:
        raise MalformedResponse(response.text)

    status = response["status"]
    if status == "ok":
        pass
    elif status == "error":
        raise ErrorResponse(response["message"])
    else:
        raise RuntimeError(f"Unhandled response status: {status}")

    return response


def get_auth(url, username, password):
    """
    Retrieve authentication from arguments or infers from .netrc.

    :param url: The URL to check.
    :type url: str
    :param username: The username to use.
    :type username: str
    :param password: The password to use.
    :type password: str
    :returns: An HTTPBasicAuth object or None.
    :rtype: requests.auth.HTTPBasicAuth or None
    """
    auth = None
    if username:
        auth = HTTPBasicAuth(username=username, password=password)
    else:  # try netrc
        try:
            host = urlparse(url).hostname
            a = netrc.netrc().authenticators(host)
            auth = HTTPBasicAuth(username=a[0], password=a[2])
        except (netrc.NetrcParseError, IOError, TypeError):
            pass
    return auth


def get_request(url, params={}, auth=None):
    """
    Dispatches a request with GET method.

    :param url: The URL to request.
    :type url: str
    :param params: The GET parameters.
    :type params: mapping
    :returns: The processed response.
    :rtype: mapping
    """
    response = requests.get(url, params=params, headers=HEADERS, auth=auth)
    return _process_response(response)


def post_request(url, data, auth=None):
    """
    Dispatches a request with POST method.

    :param url: The URL to request.
    :type url: str
    :param data: The data to post.
    :returns: The processed response.
    :rtype: mapping
    """
    response = requests.post(url, data=data, headers=HEADERS, auth=auth)
    return _process_response(response)


def retry_on_eintr(function, *args, **kw):
    """Run a function and retry it while getting EINTR errors."""
    while True:
        try:
            return function(*args, **kw)
        except IOError as e:
            if e.errno != errno.EINTR:
                raise


def get_config(use_closest=True):
    """Get Scrapy config file as a ConfigParser."""
    sources = conf.get_sources(use_closest)
    cfg = ConfigParser(interpolation=EnvInterpolation())
    cfg.read(sources)
    return cfg


__all__ = [
    ErrorResponse.__name__,
    MalformedResponse.__name__,
    get_request.__name__,
    indent.__name__,
    post_request.__name__,
    retry_on_eintr.__name__,
]
