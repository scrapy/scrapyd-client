import requests


class ErrorResponse(Exception):
    pass


def get_response(url, params={}):
    response = requests.get(url, params=params).json()
    status = response['status']
    if status == 'ok':
        return response
    elif status == 'error':
        raise ErrorResponse(response['message'])
    else:
        raise RuntimeError('Unhandled response status: {}'.format(status))
