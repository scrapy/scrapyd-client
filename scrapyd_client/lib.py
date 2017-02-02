import fnmatch

from scrapyd_client.utils import get_response, post_response


def get_projects(url, pattern='*'):
    response = get_response(url + '/listprojects.json')
    return fnmatch.filter(response['projects'], pattern)


def get_spiders(url, project, pattern='*'):
    response = get_response(url + '/listspiders.json',
                            params={'project': project})
    return fnmatch.filter(response['spiders'], pattern)


def schedule(url, project, spider, args={}):
    data = args.copy()
    data.update({'project': project, 'spider': spider})
    response = post_response(url + '/schedule.json', data=data)
    return response['jobid']


__all__ = [get_projects.__name__,
           get_spiders.__name__,
           schedule.__name__]
