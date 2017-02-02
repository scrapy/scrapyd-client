from __future__ import print_function

from argparse import ArgumentParser
import sys
from traceback import print_exc

from scrapy.utils.conf import get_config as get_scrapy_config

from scrapyd_client.lib import get_projects
from scrapyd_client.utils import ErrorResponse


DEFAULT_TARGET_URL = 'http://localhost:6800'
ISSUE_TRACKER_URL = 'https://github.com/scrapy/scrapyd-client/issues'


def deploy(args):
    from scrapyd_client import deploy
    sys.argv.pop(1)
    deploy.main()


def projects(args):
    _projects = get_projects(args.target)
    if _projects:
        print('\n'.join(_projects))


def parse_cli_args(args, cfg):
    target_default = cfg.get('deploy', 'url', fallback=DEFAULT_TARGET_URL).rstrip('/')

    description = 'A command line interface for Scrapyd.'
    mainparser = ArgumentParser(description=description)
    subparsers = mainparser.add_subparsers()
    mainparser.add_argument('-t', '--target', default=target_default,
                        help="Specifies the Scrapyd's API base URL.")

    description = 'Deploys a Scrapy project to a Scrapyd instance. ' \
                  'For help on this command, invoke `scrapyd-deploy`.'
    parser = subparsers.add_parser('deploy', description=description)
    parser.set_defaults(action=deploy)

    description = 'Lists all projects deployed on a Scrapyd instance.'
    parser = subparsers.add_parser('projects', description=description)
    parser.set_defaults(action=projects)

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
