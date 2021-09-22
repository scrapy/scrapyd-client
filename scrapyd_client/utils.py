import errno
from json.decoder import JSONDecodeError
from os.path import dirname, join
from textwrap import indent

import requests


with open(join(dirname(__file__), 'VERSION'), 'rt') as f:
    VERSION = f.readline().strip()

HEADERS = requests.utils.default_headers().copy()
HEADERS['User-Agent'] = f'Scrapyd-client/{VERSION}'


class ErrorResponse(Exception):
    """ Raised when Scrapyd reports an error. """
    pass


class MalformedRespone(Exception):
    """ Raised when the response can't be decoded. """
    pass


def _process_response(response):
    """ Processes the response object into a dictionary. """
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
        raise RuntimeError(f'Unhandled response status: {status}')

    return response


def get_request(url, params={}):
    """ Dispatches a request with GET method.
        :param url: The URL to request.
        :type url: str
        :param params: The GET parameters.
        :type params: mapping
        :returns: The processed response.
        :rtype: mapping
    """
    response = requests.get(url, params=params, headers=HEADERS)
    return _process_response(response)


def post_request(url, data):
    """ Dispatches a request with POST method.
        :param url: The URL to request.
        :type url: str
        :param data: The data to post.
        :returns: The processed response.
        :rtype: mapping
    """
    response = requests.post(url, data=data, headers=HEADERS)
    return _process_response(response)


def retry_on_eintr(function, *args, **kw):
    """Run a function and retry it while getting EINTR errors"""
    while True:
        try:
            return function(*args, **kw)
        except IOError as e:
            if e.errno != errno.EINTR:
                raise


__all__ = [
    ErrorResponse.__name__,
    MalformedRespone.__name__,
    get_request.__name__,
    indent.__name__,
    post_request.__name__,
    retry_on_eintr.__name__
]
