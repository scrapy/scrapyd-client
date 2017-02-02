import requests


def get_projects(url):
    response = requests.get(url + '/listprojects.json')
    return response.json()['projects']
