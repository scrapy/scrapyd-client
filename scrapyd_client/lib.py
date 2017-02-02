from scrapyd_client.utils import get_response


def get_projects(url):
    response = get_response(url + '/listprojects.json')
    return response['projects']
