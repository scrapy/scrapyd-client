import fnmatch

from scrapyd_client.utils import get_auth, get_request, post_request


def get_projects(url, pattern="*", username=None, password=None):
    """
    Return the project names deployed in a Scrapyd instance.

    :param url: The base URL of the Scrapd instance.
    :type url: str
    :param pattern: A globbing pattern that is used to filter the results,
                    defaults to '*'.
    :type pattern: str
    :param username: The username to connect to Scrapyd.
    :type pattern: str
    :param password: The password to connect to Scrapyd.
    :type pattern: str
    :rtype: A list of strings.
    """
    response = get_request(
        url + "/listprojects.json",
        auth=get_auth(url=url, username=username, password=password),
    )
    return fnmatch.filter(response["projects"], pattern)


def get_spiders(url, project, pattern="*", username=None, password=None):
    """
    Return the list of spiders implemented in a project.

    :param url: The base URL of the Scrapd instance.
    :type url: str
    :param project: The name of the project.
    :type project: str
    :param pattern: A globbing pattern that is used to filter the results,
                    defaults to '*'.
    :type pattern: str
    :param username: The username to connect to Scrapyd.
    :type pattern: str
    :param password: The password to connect to Scrapyd.
    :type pattern: str
    :rtype: A list of strings.
    """
    response = get_request(
        url + "/listspiders.json",
        params={"project": project},
        auth=get_auth(url=url, username=username, password=password),
    )
    return fnmatch.filter(response["spiders"], pattern)


def get_jobs(url, project, username=None, password=None):
    """
    Return the list of jobs implemented in a project.

    :param url: The base URL of the Scrapd instance.
    :type url: str
    :param project: The name of the project.
    :type project: str
    :param username: The username to connect to Scrapyd.
    :type pattern: str
    :param password: The password to connect to Scrapyd.
    :type pattern: str
    :rtype: A list of strings.
    """
    response = get_request(
        url + "/listjobs.json",
        params={"project": project},
        auth=get_auth(url=url, username=username, password=password),
    )
    return response


def schedule(url, project, spider, args={}, username=None, password=None):
    """
    Schedule a spider to be executed.

    :param url: The base URL of the Scrapd instance.
    :type url: str
    :param project: The name of the project.
    :type project: str
    :param spider: The name of the spider.
    :type project: str
    :param args: Extra arguments to the spider.
    :type pattern: mapping
    :param username: The username to connect to Scrapyd.
    :type pattern: str
    :param password: The password to connect to Scrapyd.
    :type pattern: str
    :returns: The job id.
    :rtype: str
    """
    data = args.copy()
    data.update({"project": project, "spider": spider})
    response = post_request(
        url + "/schedule.json",
        data=data,
        auth=get_auth(url=url, username=username, password=password),
    )
    return response["jobid"]


__all__ = [
    get_projects.__name__,
    get_spiders.__name__,
    get_jobs.__name__,
    schedule.__name__,
]
