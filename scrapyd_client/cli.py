from __future__ import print_function

from argparse import ArgumentParser
import sys
from textwrap import indent
from traceback import print_exc

from scrapy.utils.conf import get_config as get_scrapy_config

from scrapyd_client import lib
from scrapyd_client.utils import ErrorResponse


DEFAULT_TARGET_URL = 'http://localhost:6800'
INDENT_PREFIX = '  '
ISSUE_TRACKER_URL = 'https://github.com/scrapy/scrapyd-client/issues'


# commands' functions


def deploy(args):
    """ Deploys a Scrapy project to a Scrapyd instance.
        For help on this command, invoke `scrapyd-deploy`. """
    from scrapyd_client import deploy
    sys.argv.pop(1)
    deploy.main()


def projects(args):
    """ Lists all projects deployed on a Scrapyd instance. """
    _projects = lib.get_projects(args.target)
    if _projects:
        print('\n'.join(_projects))


def schedule(args):
    """ Schedules the specified spider(s). """
    job_args = dict((x[0], x[1]) for x in (y.split('=', 1) for y in args.arg))
    _projects = lib.get_projects(args.target, args.project)
    for project in _projects:
        _spiders = lib.get_spiders(args.target, _projects, args.spider)
        for spider in _spiders:
            job_id = lib.schedule(args.target, project, spider, job_args)
            print(job_id)


def spiders(args):
    """ Lists all spiders for the given project(s). """
    _projects = lib.get_projects(args.target, args.project)
    for project in _projects:
        print('{}:'.format(project))
        _spiders = lib.get_spiders(args.target, project)
        if _spiders:
            print(indent('\n'.join(_spiders), INDENT_PREFIX))
        else:
            print(INDENT_PREFIX + 'No spiders.')


# cli


def parse_cli_args(args, cfg):
    target_default = cfg.get('deploy', 'url', fallback=DEFAULT_TARGET_URL).rstrip('/')
    project_default = cfg.get('deploy', 'project', fallback='*')

    description = 'A command line interface for Scrapyd.'
    mainparser = ArgumentParser(description=description)
    subparsers = mainparser.add_subparsers()
    mainparser.add_argument('-t', '--target', default=target_default,
                            help="Specifies the Scrapyd's API base URL.")

    parser = subparsers.add_parser('deploy', description=deploy.__doc__)
    parser.set_defaults(action=deploy)

    parser = subparsers.add_parser('projects', description=projects.__doc__)
    parser.set_defaults(action=projects)

    parser = subparsers.add_parser('schedule', description=schedule.__doc__)
    parser.set_defaults(action=schedule)
    parser.add_argument('-p', '--project', default=project_default,
                        help='Specifies the project, can contain wildcard-patterns.')
    parser.add_argument('-s', '--spider', default='*',
                        help='Specifies the spider, can contain wildcard-patterns.')
    parser.add_argument('--arg', action='append', default=[],
                        help='Additional argument (key=value), can be specified multiple times.')

    parser = subparsers.add_parser('spiders', description=spiders.__doc__)
    parser.set_defaults(action=spiders)
    parser.add_argument('-p', '--project', default=project_default,
                        help='Specifies the project, can contain wildcard-patterns.')

    # TODO remove next two lines when 'deploy' is moved to this module
    parsed_args, _ = mainparser.parse_known_args(args)
    if getattr(parsed_args, 'action', None) is not deploy:
        parsed_args = mainparser.parse_args(args)

    if not hasattr(parsed_args, 'action'):
        mainparser.print_help()
        raise SystemExit(0)

    return parsed_args


def main():
    try:
        config = get_scrapy_config()
        args = parse_cli_args(sys.argv[1:], config)
        args.action(args)
    except SystemExit:
        raise
    except ErrorResponse as e:
        print('Scrapyd responded with an error: {}'.format(str(e)))
        raise SystemExit(1)
    except Exception:
        print('Caught unhandled exception, please report at {}'.format(ISSUE_TRACKER_URL))
        print_exc()
        raise SystemExit(3)
