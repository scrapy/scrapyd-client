import requests


class ErrorResponse(Exception):
    pass


def _check_status(response):
    status = response['status']
    if status == 'ok':
        pass
    elif status == 'error':
        raise ErrorResponse(response['message'])
    else:
        raise RuntimeError('Unhandled response status: {}'.format(status))


def get_response(url, params={}):
    response = requests.get(url, params=params).json()
    _check_status(response)
    return response


def post_response(url, data):
    response = requests.post(url, data=data).json()
    _check_status(response)
    return response
