import netrc
import os
from configparser import BasicInterpolation, ConfigParser
from urllib.parse import urlparse

from requests.auth import HTTPBasicAuth
from scrapy.utils import conf

DEFAULT_TARGET_URL = "http://localhost:6800"


class EnvInterpolation(BasicInterpolation):
    """Interpolation which expands environment variables in values."""

    def before_get(self, parser, section, option, value, defaults):
        value = super().before_get(parser, section, option, value, defaults)
        return os.path.expandvars(value)


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
    if username:
        return HTTPBasicAuth(username=username, password=password)

    try:
        username, _account, password = netrc.netrc().authenticators(urlparse(url).hostname)
        return HTTPBasicAuth(username=username, password=password)
    except (OSError, netrc.NetrcParseError, TypeError):
        return None


def get_config(use_closest=True):
    """Get Scrapy config file as a ConfigParser."""
    cfg = ConfigParser(interpolation=EnvInterpolation())
    cfg.read(conf.get_sources(use_closest))
    return cfg
