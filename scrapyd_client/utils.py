from json.decoder import JSONDecodeError

import requests


class ErrorResponse(Exception):
    pass


class MalformedRespone(Exception):
    pass


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


def get_response(url, params={}):
    response = requests.get(url, params=params)
    return _process_response(response)


def post_response(url, data):
    response = requests.post(url, data=data)
    return _process_response(response)

