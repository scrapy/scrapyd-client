from __future__ import print_function

from argparse import ArgumentParser
import sys
from traceback import print_exc

from scrapy.utils.conf import get_config as get_scrapy_config

from scrapyd_client.lib import get_projects


DEFAULT_TARGET_URL = 'http://localhost:6800'
ISSUE_TRACKER_URL = 'https://github.com/scrapy/scrapyd-client/issues'


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


    description = 'Lists all projects deployed on a Scrapyd instance.'
    parser = subparsers.add_parser('projects', description=description)
    parser.set_defaults(action=projects)




def main():
    try:
        config = get_scrapy_config()
        args = parse_cli_args(sys.argv[1:], config)
        args.action(args)
    except SystemExit:
        raise
    except Exception:
        print('Caught unhandled exception, please report at {}'.format(ISSUE_TRACKER_URL))
        print_exc()
        raise SystemExit(3)
