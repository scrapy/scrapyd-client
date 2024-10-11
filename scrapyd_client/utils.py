from __future__ import annotations

import netrc
import os
from configparser import BasicInterpolation, ConfigParser
from urllib.parse import urlparse

from requests.auth import HTTPBasicAuth
from scrapy.utils import conf


class EnvInterpolation(BasicInterpolation):
    """Interpolation which expands environment variables in values."""

    def before_get(self, parser, section, option, value, defaults):
        value = super().before_get(parser, section, option, value, defaults)
        return os.path.expandvars(value)


def get_auth(url: str, username: str, password: str) -> HTTPBasicAuth | None:
    """Retrieve authentication from arguments or infers from .netrc."""
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


def _get_targets():
    cfg = get_config()
    baset = dict(cfg.items("deploy")) if cfg.has_section("deploy") else {}
    targets = {}
    if "url" in baset:
        targets["default"] = baset
    for section in cfg.sections():
        if section.startswith("deploy:"):
            t = baset.copy()
            t.update(cfg.items(section))
            targets[section[7:]] = t
    return targets
