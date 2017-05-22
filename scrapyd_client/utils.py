import sys

import requests
from scrapy.utils.conf import get_config as get_scrapy_config


class ErrorResponse(Exception):
    pass


class MalformedRespone(Exception):
    pass


if sys.version_info < (3,):
    from ConfigParser import NoOptionError, NoSectionError
else:
    from configparser import NoOptionError, NoSectionError


if sys.version_info < (3, 3):
    def indent(s, prefix):
        return '\n'.join(prefix + x for x in s.splitlines())
else:
    from textwrap import indent  # noqa: F401


if sys.version_info < (3, 5):
    JSONDecodeError = ValueError
else:
    from json.decoder import JSONDecodeError


scrapy_config = get_scrapy_config()


def get_config(section, option, fallback):
    """ Compatibilty wrapper for Python 2.7 which lacks the fallback parameter. """
    try:
        return scrapy_config.get(section, option)
    except (NoOptionError, NoSectionError):
        return fallback


def _process_response(response):
    try:
        response = response.json()
    except JSONDecodeError:
        raise MalformedRespone(response.text)

    status = response['status']
    if status == 'ok':
        pass
    elif status == 'error':
        raise ErrorResponse(response['message'])
    else:
        raise RuntimeError('Unhandled response status: {}'.format(status))

    return response


def get_request(url, params={}):
    response = requests.get(url, params=params)
    return _process_response(response)


def post_request(url, data):
    response = requests.post(url, data=data)
    return _process_response(response)


__all__ = [
    ErrorResponse.__name__,
    MalformedRespone.__name__,
    get_config.__name__,
    get_request.__name__,
    post_request.__name__
]
