from __future__ import print_function

import sys
from argparse import ArgumentParser
from traceback import print_exc

from requests.exceptions import ConnectionError
from scrapy.utils.conf import get_config as get_scrapy_config

from scrapyd_client import commands
from scrapyd_client.utils import ErrorResponse, MalformedRespone


DEFAULT_TARGET_URL = 'http://localhost:6800'
ISSUE_TRACKER_URL = 'https://github.com/scrapy/scrapyd-client/issues'


def parse_cli_args(args, cfg):
    target_default = cfg.get('deploy', 'url', fallback=DEFAULT_TARGET_URL).rstrip('/')
    project_default = cfg.get('deploy', 'project', fallback='*')

    description = 'A command line interface for Scrapyd.'
    mainparser = ArgumentParser(description=description)
    subparsers = mainparser.add_subparsers()
    mainparser.add_argument('-t', '--target', default=target_default,
                            help="Specifies the Scrapyd's API base URL.")

    parser = subparsers.add_parser('deploy', description=commands.deploy.__doc__)
    parser.set_defaults(action=commands.deploy)

    parser = subparsers.add_parser('projects', description=commands.projects.__doc__)
    parser.set_defaults(action=commands.projects)

    parser = subparsers.add_parser('schedule', description=commands.schedule.__doc__)
    parser.set_defaults(action=commands.schedule)
    parser.add_argument('-p', '--project', default=project_default,
                        help='Specifies the project, can contain wildcard-patterns.')
    parser.add_argument('-s', '--spider', default='*',
                        help='Specifies the spider, can contain wildcard-patterns.')
    parser.add_argument('--arg', action='append', default=[],
                        help='Additional argument (key=value), can be specified multiple times.')

    parser = subparsers.add_parser('spiders', description=commands.spiders.__doc__)
    parser.set_defaults(action=commands.spiders)
    parser.add_argument('-p', '--project', default=project_default,
                        help='Specifies the project, can contain wildcard-patterns.')

    # TODO remove next two lines when 'deploy' is moved to this module
    parsed_args, _ = mainparser.parse_known_args(args)
    if getattr(parsed_args, 'action', None) is not commands.deploy:
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
    except KeyboardInterrupt:
        print('Aborted due to keyboard interrupt.')
        exit_code = 0
    except SystemExit as e:
        exit_code = e.code
    except ConnectionError as e:
        print('Failed to connect to target ({}):'.format(args.target))
        print(e)
        exit_code = 1
    except ErrorResponse as e:
        print('Scrapyd responded with an error:')
        print(e)
        exit_code = 1
    except MalformedRespone as e:
        text = str(e)
        if len(text) > 120:
            text = text[:50] + ' [...] ' + text[-50:]
        print('Received a malformed response:')
        print(text)
        exit_code = 1
    except Exception:
        print('Caught unhandled exception, please report at {}'.format(ISSUE_TRACKER_URL))
        print_exc()
        exit_code = 3
    else:
        exit_code = 0
    finally:
        raise SystemExit(exit_code)
