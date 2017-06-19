import fnmatch

from scrapyd_client.utils import get_request, post_request


def get_projects(url, pattern='*'):
    """ Returns the project names deployed in a Scrapyd instance.
        :param url: The base URL of the Scrapd instance.
        :type url: str
        :param pattern: A globbing pattern that is used to filter the results,
                        defaults to '*'.
        :type pattern: str
        :rtype: A list of strings.
    """
    response = get_request(url + '/listprojects.json')
    return fnmatch.filter(response['projects'], pattern)


def get_spiders(url, project, pattern='*'):
    """ Returns the list of spiders implemented in a project.
        :param url: The base URL of the Scrapd instance.
        :type url: str
        :param project: The name of the project.
        :type project: str
        :param pattern: A globbing pattern that is used to filter the results,
                        defaults to '*'.
        :type pattern: str
        :rtype: A list of strings.
    """
    response = get_request(url + '/listspiders.json',
                           params={'project': project})
    return fnmatch.filter(response['spiders'], pattern)


def schedule(url, project, spider, args={}):
    """ Schedules a spider to be executed.
        :param url: The base URL of the Scrapd instance.
        :type url: str
        :param project: The name of the project.
        :type project: str
        :param spider: The name of the spider.
        :type project: str
        :param args: Extra arguments to the spider.
        :type pattern: mapping
        :returns: The job id.
        :rtype: str
    """
    data = args.copy()
    data.update({'project': project, 'spider': spider})
    response = post_request(url + '/schedule.json', data=data)
    return response['jobid']


__all__ = [get_projects.__name__,
           get_spiders.__name__,
           schedule.__name__]
